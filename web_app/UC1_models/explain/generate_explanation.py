import os
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

# ==========================================================
# Path / IO utilities
# ==========================================================
def _here(*parts: str) -> str:
    return os.path.normpath(os.path.join(os.path.dirname(__file__), *parts))

def _read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def _safe_get(d: Any, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

# ==========================================================
# Ollama detection
# ==========================================================
def ollama_installed() -> bool:
    """Check if Ollama is installed and print a friendly log."""
    try:
        subprocess.run(["ollama", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        print("Ollama installation detected.")
        print(f"version of Ollama is installed. {_safe_get('Ollama', 'version')}")
        return True
    except FileNotFoundError:
        print("Ollama not found — skipping local LLM enhancement.")
        return False
    except Exception as e:
        print("Ollama detection failed:", e)
        return False

# ==========================================================
# FHIR index + helpers
# ==========================================================
def build_index(bundle: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    idx: Dict[str, Dict[str, Any]] = {}
    for e in bundle.get("entry", []) or []:
        res = e.get("resource")
        if not isinstance(res, dict):
            continue
        rtype, rid = res.get("resourceType"), res.get("id")
        if rtype and rid:
            idx[f"{rtype}/{rid}"] = res
    return idx

def human_name(name_obj: Any) -> Optional[str]:
    if not name_obj:
        return None
    n = name_obj[0] if isinstance(name_obj, list) and name_obj else name_obj
    if not isinstance(n, dict):
        return None
    if n.get("text"):
        return n["text"].strip()
    family = (n.get("family") or "").strip()
    given = " ".join([g for g in (n.get("given") or []) if isinstance(g, str)]).strip()
    return " ".join([x for x in [given, family] if x])

def codeable_to_texts(cc: Any) -> List[str]:
    out = []
    if isinstance(cc, dict):
        if cc.get("text"):
            out.append(cc["text"])
        for c in cc.get("coding") or []:
            if c.get("display"):
                out.append(c["display"])
            elif c.get("code"):
                out.append(c["code"])
    elif isinstance(cc, list):
        for i in cc:
            out.extend(codeable_to_texts(i))
    return [x for x in out if x]

# ==========================================================
# Extractors
# ==========================================================
def extract_patient(bundle: Dict[str, Any]) -> Dict[str, Any]:
    for e in bundle.get("entry", []) or []:
        r = e.get("resource")
        if isinstance(r, dict) and r.get("resourceType") == "Patient":
            return {
                "name": human_name(r.get("name")),
                "gender": r.get("gender"),
                "birthDate": r.get("birthDate")
            }
    return {}

def extract_conditions(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    conds = []
    for e in bundle.get("entry", []) or []:
        r = e.get("resource")
        if not (isinstance(r, dict) and r.get("resourceType") == "Condition"):
            continue
        code_texts = codeable_to_texts(r.get("code"))
        if code_texts:
            conds.append({
                "text": code_texts[0],
                "status": _safe_get(r, "clinicalStatus", "text"),
                "onsetDateTime": r.get("onsetDateTime")
            })
    return conds

def extract_medications(bundle: Dict[str, Any], idx: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    meds = []
    for e in bundle.get("entry", []) or []:
        r = e.get("resource")
        if not isinstance(r, dict):
            continue
        if r.get("resourceType") in ("MedicationStatement", "MedicationRequest"):
            code_texts = codeable_to_texts(r.get("medicationCodeableConcept"))
            med_text = code_texts[0] if code_texts else None
            if med_text:
                meds.append({"text": med_text})
    return meds

def extract_observations(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    obs = []
    for e in bundle.get("entry", []) or []:
        r = e.get("resource")
        if not (isinstance(r, dict) and r.get("resourceType") == "Observation"):
            continue
        code_texts = codeable_to_texts(r.get("code"))
        if code_texts:
            obs.append({"text": code_texts[0]})
    return obs

def extract_care_context(bundle: Dict[str, Any]) -> Dict[str, Any]:
    orgs, pracs = [], []
    for e in bundle.get("entry", []) or []:
        r = e.get("resource")
        if not isinstance(r, dict):
            continue
        if r.get("resourceType") == "Organization" and r.get("name"):
            orgs.append({"name": r["name"]})
        if r.get("resourceType") == "Practitioner" and r.get("name"):
            pracs.append({"name": human_name(r["name"])})
    return {"organizations": orgs, "practitioners": pracs}

# ==========================================================
# Build Explanation JSON and Plain Text
# ==========================================================
def to_explanation_json(bundle: Dict[str, Any]) -> Dict[str, Any]:
    idx = build_index(bundle)
    return {
        "patient": extract_patient(bundle),
        "conditions": extract_conditions(bundle),
        "medications": extract_medications(bundle, idx),
        "observations": extract_observations(bundle),
        "care_context": extract_care_context(bundle),
        "notes": [
            "This summary is generated from the provided FHIR Bundle.",
            "Only information present in the bundle is included; no additional facts were inferred."
        ]
    }

def to_plain_text(data: Dict[str, Any]) -> str:
    p = data.get("patient", {})
    lines = []
    header = p.get("name") or "Patient"
    if p.get("gender"):
        header += f" ({p['gender']})"
    lines.append(header + "\n")

    conds = data.get("conditions", [])
    if conds:
        lines.append("Conditions")
        for c in conds:
            t = c["text"]
            if c.get("status"):
                t += f" — {c['status']}"
            lines.append(f"- {t}")
        lines.append("")

    meds = data.get("medications", [])
    if meds:
        lines.append("Medications")
        for m in meds:
            lines.append(f"- {m['text']}")
        lines.append("")

    obs = data.get("observations", [])
    if obs:
        lines.append("Observations")
        for o in obs:
            lines.append(f"- {o['text']}")
        lines.append("")

    ctx = data.get("care_context", {})
    orgs = [o["name"] for o in ctx.get("organizations", []) if "name" in o]
    pracs = [p["name"] for p in ctx.get("practitioners", []) if "name" in p]

    if orgs:
        lines.append("Organizations")
        for o in orgs:
            lines.append(f"- {o}")
        lines.append("")

    if pracs:
        lines.append("Practitioners")
        for n in pracs:
            lines.append(f"- {n}")
        lines.append("")

    lines.append("Notes")
    for n in data.get("notes", []):
        lines.append(f"- {n}")
    return "\n".join(lines) + "\n"

# ==========================================================
# LLM enhancement (Mistral via Ollama)
# ==========================================================
def enhance_with_ollama(explanation_json_path: str, model: str = "mistral") -> Optional[str]:
    try:
        with open(explanation_json_path, "r", encoding="utf-8") as f:
            facts = json.load(f)
        prompt = (
            "You are a clinical summarization assistant. Write a patient-friendly summary "
            "strictly using this JSON information. Do not add or assume facts:\n\n"
            f"{json.dumps(facts, indent=2, ensure_ascii=False)}"
        )
        print("Enhancing explanation using local Mistral (via Ollama)...")
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180
        )
        if result.returncode == 0:
            return result.stdout.decode("utf-8").strip()
    except Exception as e:
        print("Ollama enhancement failed:", e)
    return None

# ==========================================================
# Main
# ==========================================================
def main() -> int:
    bundle_path = _here("..", "fhir_mapper", "fhir_bundle.json")
    out_json = _here("explanation.json")
    out_txt = _here("explanation.txt")
    out_fluent = _here("explanation_fluent.txt")

    if not os.path.exists(bundle_path):
        print("FHIR bundle not found.")
        return 1

    bundle = _read_json(bundle_path)
    data = to_explanation_json(bundle)

    _write_json(out_json, data)
    _write_text(out_txt, to_plain_text(data))

    USE_LLM = ollama_installed()
    if USE_LLM:
        fluent = enhance_with_ollama(out_json)
        if fluent:
            _write_text(out_fluent, fluent)
            print("Wrote:", os.path.relpath(out_fluent, os.getcwd()))
    else:
        print("Skipping Mistral enhancement.")

    print("Explanation generation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
