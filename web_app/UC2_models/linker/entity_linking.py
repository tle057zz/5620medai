# ai_medical/linker/entity_linking.py
"""
Day 4 — Entity Linking (SapBERT-based with robust fallbacks)

Features
- GPU-aware SapBERT loading with graceful CPU and model fallback
- Path independent JSON I/O
- Expanded mini vocabulary with SNOMED-CT, RxNorm, LOINC
- Per-ontology routing and thresholds
- Batch encoding for entities, cached vocab embeddings per ontology
- Per-entity error isolation
- Deterministic JSON with metadata block
"""

import os
import json
import torch
import pandas as pd
from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer, util


# -----------------------------
# 1. Model loading with fallback
# -----------------------------
def safe_load_sapbert() -> Tuple[SentenceTransformer, str, str]:
    """
    Try SapBERT, else fall back to a general biomedical/sentence model.
    Returns (model, device, model_name).
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tried = []
    for name in [
        "cambridgeltl/SapBERT-from-PubMedBERT-fulltext",
        "pritamdeka/S-BioBert-snli-multinli-stsb",
        "all-MiniLM-L6-v2"
    ]:
        try:
            model = SentenceTransformer(name, device=device)
            print(f"Loaded model: {name} on {device.upper()}")
            return model, device, name
        except Exception as e:
            tried.append(f"{name} ({e})")
    raise RuntimeError("No sentence-transformer model could be loaded. Tried: " + " | ".join(tried))


# -----------------------------
# 2. Reference vocabulary
# -----------------------------
def load_reference_vocab(vocab_path: str | None = None) -> pd.DataFrame:
    if vocab_path and os.path.exists(vocab_path):
        df = pd.read_csv(vocab_path)
    else:
        df = pd.DataFrame([
            # SNOMED-CT (Diseases/Conditions)
            {"term": "hypertension", "code": "38341003", "vocab": "SNOMED-CT"},
            {"term": "hyperlipidemia", "code": "55822004", "vocab": "SNOMED-CT"},
            {"term": "stroke", "code": "230690007", "vocab": "SNOMED-CT"},
            {"term": "chronic renal disease", "code": "90721000119101", "vocab": "SNOMED-CT"},
            {"term": "dementia", "code": "52448006", "vocab": "SNOMED-CT"},
            {"term": "cardiac failure", "code": "84114007", "vocab": "SNOMED-CT"},
            {"term": "psychotic symptoms", "code": "30746006", "vocab": "SNOMED-CT"},
            {"term": "memory deficit", "code": "386807006", "vocab": "SNOMED-CT"},
            # RxNorm (Medications)
            {"term": "atorvastatin", "code": "83367", "vocab": "RxNorm"},
            {"term": "metformin", "code": "6809", "vocab": "RxNorm"},
            {"term": "aspirin", "code": "1191", "vocab": "RxNorm"},
            # LOINC (Tests/Observations)
            {"term": "CT brain", "code": "36626-4", "vocab": "LOINC"},
            {"term": "MRI brain scan", "code": "24727-0", "vocab": "LOINC"},
            {"term": "MRI scan", "code": "24531-6", "vocab": "LOINC"},
            {"term": "blood pressure measurement", "code": "85354-9", "vocab": "LOINC"},
            # SNOMED-CT (Procedures)
            {"term": "rehabilitation", "code": "22850007", "vocab": "SNOMED-CT"},
        ])
    df = df[["term", "code", "vocab"]].dropna().reset_index(drop=True)
    return df


# -----------------------------
# 3. Ontology routing and thresholds
# -----------------------------
def choose_ontology(label: str, text: str) -> str | None:
    lab = (label or "").upper()
    t = (text or "").lower()

    if lab in {"DISEASE", "CONDITION", "SYMPTOM"}:
        return "SNOMED-CT"
    if lab in {"MEDICATION", "DRUG", "CHEMICAL"}:
        return "RxNorm"
    if lab in {"OBSERVATION", "TEST"}:
        return "LOINC"

    if any(k in t for k in ["ct", "mri", "scan", "test", "pressure"]):
        return "LOINC"
    if any(k in t for k in ["rehabilitation", "procedure"]):
        return "SNOMED-CT"
    return None


THRESHOLDS = {
    "SNOMED-CT": 0.45,
    "RxNorm": 0.55,
    "LOINC": 0.50,
}


# -----------------------------
# 4. Build vocab embeddings cache
# -----------------------------
def build_vocab_cache(model: SentenceTransformer, device: str, vocab_df: pd.DataFrame) -> Dict[str, Dict]:
    cache: Dict[str, Dict] = {}
    for vocab_name, sub in vocab_df.groupby("vocab"):
        terms = sub["term"].tolist()
        embeds = model.encode(terms, convert_to_tensor=True, device=device)
        cache[vocab_name] = {
            "df": sub.reset_index(drop=True),
            "embeddings": embeds,  # tensor [N, D] on device
        }
    return cache


# -----------------------------
# 5. Core linking
# -----------------------------
def link_entities(
    ner_json_path: str,
    output_path: str,
    vocab_path: str | None = None,
) -> None:
    model, device, model_name = safe_load_sapbert()
    vocab_df = load_reference_vocab(vocab_path)
    cache = build_vocab_cache(model, device, vocab_df)

    with open(ner_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    linked_output = {}
    sections = [(k, v) for k, v in data.items() if not k.startswith("_")]

    for section, entities in sections:
        if not isinstance(entities, list) or not entities:
            linked_output[section] = []
            continue

        linked_output[section] = []

        # Batch encode all entity texts for this section
        texts = [str(e.get("text", "")).strip() for e in entities]
        try:
            ent_embeddings = model.encode(texts, convert_to_tensor=True, device=device)
        except Exception as e:
            # If the whole batch fails, fall back to per-entity
            ent_embeddings = [None] * len(texts)
            print(f"[WARN] Batch encode failed for section '{section}': {e}")

        for idx, ent in enumerate(entities):
            text = texts[idx]
            label = ent.get("label", "")
            if not text:
                continue

            ontology = choose_ontology(label, text)
            if not ontology or ontology not in cache:
                linked_output[section].append(ent)
                continue

            sub_df = cache[ontology]["df"]
            sub_emb = cache[ontology]["embeddings"]  # [N, D]
            cutoff = THRESHOLDS.get(ontology, 0.5)

            # Per-entity embedding
            try:
                q_embed = ent_embeddings[idx]
                if q_embed is None or isinstance(q_embed, list):
                    q_embed = model.encode(text, convert_to_tensor=True, device=device)
            except Exception as e:
                print(f"[WARN] Skipped entity '{text}' in section '{section}': {e}")
                linked_output[section].append(ent)
                continue

            try:
                sims = util.cos_sim(q_embed, sub_emb)[0]
                best_idx = int(torch.argmax(sims).item())
                best_score = float(sims[best_idx].item())
            except Exception as e:
                print(f"[WARN] Similarity failed for '{text}' in section '{section}': {e}")
                linked_output[section].append(ent)
                continue

            linked = dict(ent)
            if best_score > cutoff:
                linked.update({
                    "linked_code": sub_df.iloc[best_idx]["code"],
                    "vocabulary": sub_df.iloc[best_idx]["vocab"],
                    "display": sub_df.iloc[best_idx]["term"],
                    "confidence": round(best_score, 3),
                })
            else:
                linked.update({
                    "linked_code": None,
                    "vocabulary": ontology,
                    "display": None,
                    "confidence": round(best_score, 3),
                })

            linked_output[section].append(linked)

    # Metadata for traceability
    linked_output["_meta"] = {
        "model": model_name,
        "device": device,
        "thresholds": THRESHOLDS,
        "total_sections": len(sections),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(linked_output, f, indent=2, ensure_ascii=False)

    print(f"Entity linking complete. Output saved to {output_path}")
    print("Linked entities with ontology codes injected.")


# -----------------------------
# 6. Entry point
# -----------------------------
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ner_path = os.path.abspath(os.path.join(base_dir, "../ner/ner_output_final.json"))
    out_path = os.path.abspath(os.path.join(base_dir, "linked_entities.json"))
    vocab_path = os.path.abspath(os.path.join(base_dir, "mini_vocab.csv"))

    if not os.path.exists(ner_path):
        raise FileNotFoundError(f"NER file not found: {ner_path}")

    link_entities(ner_path, out_path, vocab_path)
