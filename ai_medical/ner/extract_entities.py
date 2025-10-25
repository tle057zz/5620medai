# ai_medical/ner/extract_entities.py

import os
import json
import spacy
import re
import string


# ----------------------------------------------------------
# Load Sectionized JSON
# ----------------------------------------------------------

def load_sections(json_path):
    """Load the sectionized JSON file produced by the sectionizer stage."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Sectionized JSON not found: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------
# NER Extraction Utilities
# ----------------------------------------------------------

def extract_entities_with_model(nlp, text):
    """Extract entities using a given SpaCy model."""
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text.strip(),
            "label": ent.label_,
            "start_char": ent.start_char,
            "end_char": ent.end_char
        })
    return entities


# ----------------------------------------------------------
# Merging Logic (Span + Priority)
# ----------------------------------------------------------

def spans_overlap(a, b):
    return not (a["end_char"] <= b["start_char"] or b["end_char"] <= a["start_char"])


def merge_entities(base_entities, clinical_entities):
    """
    Merge outputs from both models, preferring clinical labels over generic ones
    and eliminating duplicates by text and overlapping spans.
    """
    priority = {"DISEASE": 3, "MEDICATION": 3, "CONTEXT": 2, "GENERAL": 1}

    # First pass: keep highest-priority label per lowercase text
    best_by_text = {}
    for ent in base_entities + clinical_entities:
        key = ent["text"].strip().lower()
        if key not in best_by_text or priority.get(ent["label"].upper(), 0) > priority.get(best_by_text[key]["label"].upper(), 0):
            best_by_text[key] = ent

    # Second pass: remove overlapping duplicates by span
    kept = []
    for ent in best_by_text.values():
        drop = False
        for other in kept:
            if ent["text"].strip().lower() == other["text"].strip().lower():
                continue
            if spans_overlap(ent, other):
                if priority.get(ent["label"].upper(), 0) <= priority.get(other["label"].upper(), 0):
                    drop = True
                    break
        if not drop:
            kept.append(ent)

    return kept


# ----------------------------------------------------------
# Chemical False Positive Filter
# ----------------------------------------------------------

def is_false_chemical(text):
    """Detect non-chemical terms misclassified as CHEMICAL."""
    text_clean = text.strip()
    tokens = text_clean.split()

    if len(text_clean) < 3 or (len(tokens) <= 2 and text_clean.isalpha()):
        return True

    chem_suffixes = ("ine", "ol", "ate", "ide", "ium", "one", "acid", "azole")
    if all(c in string.ascii_letters + " " for c in text_clean):
        if not any(text_clean.lower().endswith(suf) for suf in chem_suffixes):
            return True

    if re.match(r"^([A-Z][a-z]+(\s[A-Z][a-z]+){0,2})$", text_clean):
        return True

    if len(tokens) > 3 and all(t[0].isupper() for t in tokens if t):
        return True

    return False


# ----------------------------------------------------------
# Medication Context Detector
# ----------------------------------------------------------

def detect_medication_context(section_text, entity_text):
    """
    Return 'high'/'medium'/'low'/None if entity_text likely refers to a medication.
    Excludes non-word spans, requires lexical evidence, and uses contextual triggers.
    """
    text_lower = entity_text.lower().strip()
    section_lower = section_text.lower()

    # Reject entities with non-word characters or overlong phrases
    if any(ch in text_lower for ch in {"/", "\\", "•", "–", "—", "”", "“", "’"}):
        return None
    if len(text_lower.split()) > 3:
        return None

    # Exclusion list
    excluded = {
        "date","please","minister","day","act","done","explanation","section","process",
        "report","information","assessment","questions","question","interaction","interactions",
        "tone","visual aids","state","physical state","please state","act done","no","no",
        "form","patient","tests","patient/the tests"
    }
    if text_lower in excluded:
        return None

    # Lexical clues
    med_terms = {
        "tablet","capsule","syrup","injection","dose","drug","medicine","medication","therapy",
        "ointment","cream","pill","vitamin","antibiotic","paracetamol","aspirin","metformin",
        "ibuprofen","insulin"
    }
    med_suffixes = (
        "ine","ol","ate","ide","ium","one","vir","azole","mycin","cillin","pril","sartan","statin"
    )

    lex_match = (text_lower in med_terms) or any(text_lower.endswith(suf) for suf in med_suffixes)

    # Context triggers around the entity
    idx = section_lower.find(text_lower)
    if idx == -1:
        return None
    window = 100
    context = section_lower[max(0, idx - window): min(len(section_lower), idx + len(text_lower) + window)]
    triggers = [
        "prescribed","started on","given","taking","treated with","administered",
        "course of","dose of","tablet of","therapy for","medication for","continue","stop"
    ]
    ctx_match = any(tp in context for tp in triggers)

    # Confidence rules
    if lex_match and ctx_match:
        return "high"
    if ctx_match and not lex_match:
        return "medium"
    if lex_match and not ctx_match:
        return "low"
    return None


# ----------------------------------------------------------
# Cleaning, Normalization, and Confidence Assignment
# ----------------------------------------------------------

def clean_entities(entities, section_text):
    clean = []
    for ent in entities:
        text = ent["text"].strip()
        label = ent["label"].upper()
        confidence = "medium"

        # Remove false CHEMICALs
        if label == "CHEMICAL" and is_false_chemical(text):
            continue

        # Map vague ENTITY labels
        if label == "ENTITY":
            if re.search(r"(hospital|clinic|report|relationship|information|address|date|year|name)",
                         text, re.IGNORECASE):
                label = "CONTEXT"
            else:
                label = "GENERAL"

        # Reject overlong sentence-like clinical fragments
        if label in ("DISEASE", "MEDICATION"):
            if len(text.split()) > 6:
                continue
            if re.search(r"\b(of|the|and|his|her|their|to|in|on)\b.*\b(mind|brain|functioning)\b",
                         text.lower()):
                continue

        # Contextual medication detection
        med_conf = detect_medication_context(section_text, text)
        if med_conf:
            label = "MEDICATION"
            confidence = med_conf

        # Default confidence for others
        if label in ("GENERAL", "CONTEXT"):
            confidence = "medium"
        elif label == "DISEASE":
            confidence = "high"

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        clean.append({
            "text": text,
            "label": label,
            "confidence": confidence
        })

    # Deduplicate (case-insensitive)
    unique = []
    seen = set()
    for e in clean:
        key = (e["text"].lower(), e["label"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique


# ----------------------------------------------------------
# Pipeline Execution
# ----------------------------------------------------------

def extract_entities_from_sections(sections):
    print("Loading base model (en_core_sci_sm)...")
    nlp_base = spacy.load("en_core_sci_sm")

    print("Loading biomedical model (en_ner_bc5cdr_md)...")
    nlp_clinical = spacy.load("en_ner_bc5cdr_md")

    section_entities = {}
    for section_name, content in sections.items():
        if not content.strip():
            continue

        print(f"Processing section: {section_name}")
        base_entities = extract_entities_with_model(nlp_base, content)
        clinical_entities = extract_entities_with_model(nlp_clinical, content)
        merged = merge_entities(base_entities, clinical_entities)
        cleaned = clean_entities(merged, content)

        section_entities[section_name] = cleaned

    return section_entities


# ----------------------------------------------------------
# Main Runner
# ----------------------------------------------------------

if __name__ == "__main__":
    input_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "sectionizer",
        "sectionized_output.json"
    )

    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, "ner_output_final.json")

    try:
        sections = load_sections(input_path)
        ner_results = extract_entities_from_sections(sections)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(ner_results, f, indent=4, ensure_ascii=False)

        print("\nFinal NER output saved to:", output_path)

    except Exception as e:
        print("Entity extraction failed:", e)
