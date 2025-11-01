# ai_medical/fhir_mapper/fhir_mapping.py
"""
Day 5 — FHIR Mapper (Final Production-Grade Version)

Fixes:
- Skips _meta and any non-list/non-dict sections (prevents AttributeError)
- Adds UTC timestamps ("Z")
- Sorts entries for deterministic ordering
- Maintains full FHIR R4 compliance
"""

import os
import re
import json
from uuid import uuid4
from datetime import datetime

# ---------------------------------
# Utility
# ---------------------------------
def utcnow():
    """Return UTC time in FHIR-compliant Zulu format."""
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def norm_text(t: str) -> str:
    return " ".join(t.strip().lower().split())

def make_ref(resource_type, res_id):
    return {"reference": f"{resource_type}/{res_id}"}

# ---------------------------------
# FHIR Resource Builders
# ---------------------------------
def make_patient(name, gender="unknown"):
    return {
        "resourceType": "Patient",
        "id": str(uuid4()),
        "name": [{"text": name}],
        "gender": gender
    }

def make_practitioner(name):
    return {
        "resourceType": "Practitioner",
        "id": str(uuid4()),
        "name": [{"text": name}]
    }

def make_org(name):
    return {
        "resourceType": "Organization",
        "id": str(uuid4()),
        "name": name
    }

def make_condition(ent, patient_id, pract_id):
    code = ent.get("linked_code") or "000000"
    vocab = ent.get("vocabulary") or "SNOMED-CT"
    display = ent.get("display") or ent.get("text", "")
    return {
        "resourceType": "Condition",
        "id": str(uuid4()),
        "code": {
            "text": display,
            "coding": [{
                "system": "http://snomed.info/sct" if vocab == "SNOMED-CT" else "",
                "code": code,
                "display": display
            }]
        },
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": "active",
                "display": "Active"
            }],
            "text": "active"
        },
        "subject": make_ref("Patient", patient_id),
        "asserter": make_ref("Practitioner", pract_id),
        "onsetDateTime": utcnow()
    }

def make_medication(ent, patient_id, pract_id):
    GENERIC_WORDS = {"medicine", "medication", "drug", "tablet", "capsule", "dose"}
    text = (ent.get("display") or ent.get("text") or "").strip()
    if not text or text.lower() in GENERIC_WORDS:
        return None

    code = ent.get("linked_code") or "000000"
    vocab = ent.get("vocabulary") or "RxNorm"
    system = (
        "http://www.nlm.nih.gov/research/umls/rxnorm"
        if vocab == "RxNorm"
        else "http://snomed.info/sct"
        if vocab == "SNOMED-CT"
        else ""
    )
    display = ent.get("canonical_name") or text
    med = {
        "resourceType": "MedicationStatement",
        "id": str(uuid4()),
        "status": "active",
        "medicationCodeableConcept": {
            "text": display,
            "coding": [{
                "system": system,
                "code": code,
                "display": display
            }]
        },
        "subject": make_ref("Patient", patient_id),
        "informationSource": make_ref("Practitioner", pract_id),
        "effectiveDateTime": utcnow()
    }
    if ent.get("dosage"):
        med["dosage"] = [{"text": ent["dosage"]}]
    return med

def make_observation(ent, patient_id, pract_id):
    code = ent.get("linked_code") or "000000"
    vocab = ent.get("vocabulary") or "LOINC"
    display = ent.get("display") or ent.get("text", "")
    return {
        "resourceType": "Observation",
        "id": str(uuid4()),
        "status": "final",
        "code": {
            "text": display,
            "coding": [{
                "system": "http://loinc.org" if vocab == "LOINC" else "",
                "code": code,
                "display": display
            }]
        },
        "subject": make_ref("Patient", patient_id),
        "performer": [make_ref("Practitioner", pract_id)],
        "effectiveDateTime": utcnow()
    }

def make_procedure(ent, patient_id, pract_id):
    return {
        "resourceType": "Procedure",
        "id": str(uuid4()),
        "status": "completed",
        "code": {"text": ent.get("text", "")},
        "subject": make_ref("Patient", patient_id),
        "performer": [{"actor": make_ref("Practitioner", pract_id)}],
        "performedDateTime": utcnow()
    }

def make_encounter(patient_id):
    """Adds a minimal Encounter for care context."""
    return {
        "resourceType": "Encounter",
        "id": str(uuid4()),
        "status": "finished",
        "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "AMB"},
        "subject": make_ref("Patient", patient_id),
        "period": {"start": utcnow(), "end": utcnow()}
    }

# ---------------------------------
# Name Extraction
# ---------------------------------
def extract_patient_name(txt):
    txt = re.sub(r"\b(said|reported|noted|identified|born)\b.*", "", txt, flags=re.IGNORECASE)
    match = re.match(r"(Mr|Ms|Mrs|Miss)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4}", txt)
    if match:
        return match.group(0).strip()
    tokens = re.findall(r"\b[A-Z][a-zA-Z\.]+\b", txt)
    if 2 <= len(tokens) <= 5:
        return " ".join(tokens)
    return "Unknown Patient"

def extract_practitioner_name(txt):
    txt = re.split(r"\b(NRIC|FIN|Passport|ID|License|Reg)\b", txt, maxsplit=1)[0]
    match = re.match(r"(Dr|Doctor)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}", txt)
    if match:
        return match.group(0).strip()
    match = re.match(r"[A-Z][a-z]+(?:\s+[A-Z][a-zA-Z\.]+){1,3}", txt)
    if match:
        return re.sub(r",?\s*(MD|MBBS|PhD|DO)$", "", match.group(0).strip(), flags=re.IGNORECASE)
    return "Unknown Practitioner"

# ---------------------------------
# Validation Filters
# ---------------------------------
def is_valid_org(name):
    n = name.lower()
    if n in {"hospital", "clinic", "hospital clinic"}:
        return False
    if n.startswith("clinical") or "history" in n or "impression" in n:
        return False
    return True

OBS_KEYWORDS = {
    "ct", "mri", "scan", "x-ray", "imaging", "pressure",
    "test", "blood", "temperature", "pulse", "oxygen", "vital"
}

def is_valid_observation(text):
    t = text.lower().strip()
    if len(t.split()) < 2:
        return False
    if any(k in t for k in ["act", "doctor", "section", "restrictive", "patient/"]):
        return False
    if "/" in t or "patient" in t:
        return False
    return any(k in t for k in OBS_KEYWORDS)

# ---------------------------------
# Converter
# ---------------------------------
def convert_to_fhir_bundle(linked_json_path, output_path):
    with open(linked_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    patient_name, practitioner_name, gender = "Unknown Patient", "Unknown Practitioner", "unknown"

    # --- Safe Name Extraction ---
    for section_name, ents in data.items():
        if not isinstance(ents, list):
            continue  # skip _meta or invalid sections
        for e in ents:
            if not isinstance(e, dict):
                continue
            txt = e.get("text", "")
            if "Mr" in txt or "Ms" in txt or "Mrs" in txt or "Miss" in txt:
                patient_name, gender = extract_patient_name(txt), "male" if "Mr" in txt else "female"
            elif gender == "unknown":
                possible = extract_patient_name(txt)
                if possible != "Unknown Patient":
                    patient_name = possible
            if "Dr" in txt or "Doctor" in txt:
                practitioner_name = extract_practitioner_name(txt)
            elif practitioner_name == "Unknown Practitioner":
                possible_prac = extract_practitioner_name(txt)
                if possible_prac != "Unknown Practitioner":
                    practitioner_name = possible_prac

    patient = make_patient(patient_name, gender)
    practitioner = make_practitioner(practitioner_name)
    patient_id, pract_id = patient["id"], practitioner["id"]

    bundle = {
        "resourceType": "Bundle",
        "id": str(uuid4()),
        "type": "collection",
        "timestamp": utcnow(),
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/Bundle"],
            "tag": [{"system": "http://example.org/source", "code": "AI_Medical_Pipeline"}]
        },
        "entry": [{"resource": patient}, {"resource": practitioner}]
    }

    orgs, seen_conditions, seen_obs = {}, set(), set()

    for section_name, ents in data.items():
        if not isinstance(ents, list):
            continue  # skip _meta or invalid sections
        for ent in ents:
            if not isinstance(ent, dict):
                continue

            label = ent.get("label", "").upper()
            text = ent.get("text", "").strip()
            if not text:
                continue

            # --- Organization ---
            if "HOSPITAL" in text.upper() or "CLINIC" in text.upper():
                key = norm_text(text)
                if key not in orgs and is_valid_org(text):
                    orgs[key] = make_org(text)
                continue

            # --- Conditions ---
            if label in {"DISEASE", "CONDITION", "SYMPTOM"}:
                key = norm_text(ent.get("display") or text)
                if key not in seen_conditions:
                    seen_conditions.add(key)
                    bundle["entry"].append({"resource": make_condition(ent, patient_id, pract_id)})
                continue

            # --- Medications ---
            if label in {"MEDICATION", "DRUG", "CHEMICAL"}:
                med_res = make_medication(ent, patient_id, pract_id)
                if med_res:
                    bundle["entry"].append({"resource": med_res})
                continue

            # --- Observations ---
            if label in {"OBSERVATION", "TEST"} or any(k in text.lower() for k in OBS_KEYWORDS):
                if not is_valid_observation(text):
                    continue
                obs_key = norm_text(ent.get("display") or text)
                if obs_key in seen_obs:
                    continue
                seen_obs.add(obs_key)
                bundle["entry"].append({"resource": make_observation(ent, patient_id, pract_id)})
                continue

            # --- Procedures ---
            if any(k in text.lower() for k in ["rehabilitation", "procedure", "surgery"]):
                bundle["entry"].append({"resource": make_procedure(ent, patient_id, pract_id)})

    # --- Add Organizations ---
    if orgs:
        for o in orgs.values():
            bundle["entry"].append({"resource": o})
        best_org = list(orgs.values())[0]
        patient["managingOrganization"] = make_ref("Organization", best_org["id"])

    # --- Add Encounter ---
    bundle["entry"].append({"resource": make_encounter(patient_id)})

    # --- Sort entries for deterministic order ---
    bundle["entry"].sort(key=lambda e: e["resource"]["resourceType"])

    # --- Write output ---
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)

    print(f"FHIR bundle created: {output_path}")
    print("Patient:", patient_name, "| Gender:", gender)
    print("Practitioner:", practitioner_name)
    print("Resources total:", len(bundle["entry"]))

# ---------------------------------
# Execution
# ---------------------------------
if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    linked_path = os.path.abspath(os.path.join(base_dir, "../linker/linked_entities.json"))
    out_path = os.path.abspath(os.path.join(base_dir, "fhir_bundle.json"))

    if not os.path.exists(linked_path):
        raise FileNotFoundError(f"Linked entities file not found: {linked_path}")

    convert_to_fhir_bundle(linked_path, out_path)
