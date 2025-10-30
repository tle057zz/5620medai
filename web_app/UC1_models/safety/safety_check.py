import json
import os
import re
import subprocess
from typing import Any, Dict, List, Tuple, Optional

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
FHIR_DIR = os.path.join(PROJECT_ROOT, "fhir_mapper")
EXPLAIN_DIR = os.path.join(PROJECT_ROOT, "explain")
OUT_DIR = THIS_DIR

FHIR_BUNDLE_PATH = os.path.join(FHIR_DIR, "fhir_bundle.json")
SAFETY_JSON_PATH = os.path.join(OUT_DIR, "safety_report.json")
SAFETY_TXT_PATH = os.path.join(OUT_DIR, "safety_summary.txt")
SAFETY_FLUENT_PATH = os.path.join(OUT_DIR, "safety_fluent.txt")


# ----------------------------
# Utility functions
# ----------------------------
def _read_json(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).lower()


def _get_resource_entries(bundle: Dict[str, Any], rtype: str) -> List[Dict[str, Any]]:
    entries = bundle.get("entry") or []
    return [e.get("resource") for e in entries if isinstance(e.get("resource"), dict) and e.get("resource", {}).get("resourceType") == rtype]


def _codeable_concepts_to_text(cc: Any) -> List[str]:
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
            out.extend(_codeable_concepts_to_text(i))
    return [x for x in out if x]


# ----------------------------
# Extractors
# ----------------------------
def _extract_condition_names(conditions: List[Dict[str, Any]]) -> List[str]:
    out = []
    for c in conditions:
        out.extend(_codeable_concepts_to_text(c.get("code")))
    seen, uniq = set(), []
    for x in out:
        n = _norm(x)
        if n not in seen:
            seen.add(n)
            uniq.append(x)
    return uniq


def _extract_medication_names(meds: List[Dict[str, Any]]) -> List[str]:
    out = []
    for m in meds:
        for k in ("medicationCodeableConcept", "medication", "code"):
            out.extend(_codeable_concepts_to_text(m.get(k)))
        if "contained" in m:
            for cont in m.get("contained") or []:
                if isinstance(cont, dict):
                    out.extend(_codeable_concepts_to_text(cont.get("code")))
    seen, uniq = set(), []
    for x in out:
        n = _norm(x)
        if n not in seen:
            seen.add(n)
            uniq.append(x)
    return uniq


# Unit normalization (mg/dL → mmol/L for glucose, mg/dL → µmol/L for creatinine)
def _normalize_units(label: str, value: Optional[float], unit: Optional[str]) -> Tuple[Optional[float], Optional[str]]:
    if value is None or unit is None:
        return value, unit
    nunit = _norm(str(unit))
    lbl = _norm(str(label))
    if "glucose" in lbl and "mg/dl" in nunit:
        return round(value / 18.0, 2), "mmol/L"
    if "creatinine" in lbl and "mg/dl" in nunit:
        return round(value * 88.4, 1), "umol/L"
    return value, unit


def _extract_observations(obs_list: List[Dict[str, Any]]) -> Dict[str, List[Tuple[str, Optional[float], Optional[str]]]]:
    """
    Returns dict normalized_label -> list of tuples (display_label, value, unit)
    Applies unit normalization at extraction time to support correct thresholds.
    """
    out: Dict[str, List[Tuple[str, Optional[float], Optional[str]]]] = {}
    for obs in obs_list:
        labels = _codeable_concepts_to_text(obs.get("code"))
        if not labels:
            continue

        def record(label_raw: str, val: Optional[float], unit: Optional[str]):
            norm_key = _norm(label_raw)
            out.setdefault(norm_key, []).append((label_raw, val, unit))

        # Scalar observation
        vq = obs.get("valueQuantity")
        if isinstance(vq, dict):
            val = None
            try:
                val = float(vq.get("value")) if vq.get("value") is not None else None
            except Exception:
                val = None
            unit = vq.get("unit") or vq.get("code")
            # apply normalization using the first code label as representative
            nval, nunit = _normalize_units(labels[0], val, unit)
            record(labels[0], nval, nunit)

        # Component observations (e.g., BP systolic/diastolic)
        for comp in obs.get("component") or []:
            comp_lbls = _codeable_concepts_to_text(comp.get("code")) or labels
            vqc = comp.get("valueQuantity") or {}
            val_c = None
            try:
                val_c = float(vqc.get("value")) if vqc.get("value") is not None else None
            except Exception:
                val_c = None
            unit_c = vqc.get("unit") or vqc.get("code")
            nval_c, nunit_c = _normalize_units(comp_lbls[0] if comp_lbls else labels[0], val_c, unit_c)
            for lbl in comp_lbls:
                record(lbl, nval_c, nunit_c)
    return out


# ----------------------------
# Clinical constants
# ----------------------------
NSAIDS = {"ibuprofen", "naproxen", "diclofenac", "indometacin", "meloxicam", "piroxicam", "etoricoxib", "celecoxib", "aspirin"}
ACE_INHIBITORS = {"lisinopril", "enalapril", "ramipril", "perindopril"}
ARBS = {"losartan", "valsartan", "irbesartan"}
BETA_BLOCKERS = {"metoprolol", "atenolol", "propranolol"}
ANTICOAGULANTS = {"warfarin", "apixaban", "heparin"}
SSRIS = {"fluoxetine", "sertraline", "citalopram"}
MAOIS = {"phenelzine", "tranylcypromine", "isocarboxazid"}
METFORMIN = {"metformin"}

COND_KEYS = {
    "hypertension": {"hypertension", "high blood pressure"},
    "stroke": {"stroke", "cva", "cerebrovascular accident"},
    "ckd": {"chronic kidney disease", "renal failure"},
    "asthma": {"asthma"},
    "thrombocytopenia": {"thrombocytopenia"},
    "hyperkalemia": {"hyperkalemia"},
    "depression": {"depression"},
    "heart_failure": {"heart failure", "chf"},
    "diabetes": {"diabetes"},
}


# ----------------------------
# Helpers
# ----------------------------
def _normalize_conditions(cond_names: List[str]) -> Dict[str, bool]:
    result = {k: False for k in COND_KEYS}
    pool = {_norm(x) for x in cond_names}
    for k, vals in COND_KEYS.items():
        if any(_norm(v) in pool for v in vals):
            result[k] = True
    return result


def _classify_medications(med_names: List[str]) -> Dict[str, bool]:
    pool = {_norm(m) for m in med_names}
    def match(group): return any(any(n in m for n in group) for m in pool)
    return {
        "nsaid": match(NSAIDS),
        "acei": match(ACE_INHIBITORS),
        "arb": match(ARBS),
        "beta_blocker": match(BETA_BLOCKERS),
        "anticoagulant": match(ANTICOAGULANTS),
        "ssri": match(SSRIS),
        "maoi": match(MAOIS),
        "metformin": match(METFORMIN)
    }


def _vital_thresholds(obs: Dict[str, List[Tuple[str, Optional[float], Optional[str]]]]) -> List[str]:
    findings: List[str] = []
    def get(keys): return [i for k in keys for i in obs.get(_norm(k), [])]
    # Hypertensive crisis (SBP)
    for lbl, val, unit in get(["systolic blood pressure", "systolic"]):
        if val is not None and val >= 180:
            findings.append(f"Hypertensive crisis systolic {val}{unit or ''}")
    # Hypoxemia (SpO2)
    for lbl, val, unit in get(["oxygen saturation", "spo2"]):
        if val is not None and val < 90:
            findings.append(f"Hypoxemia oxygen saturation {val}{unit or '%'}")
    return sorted(set(findings), key=_norm)


def _has_low_dose_aspirin_only(bundle: Dict[str, Any]) -> bool:
    """
    Returns True if aspirin is present ONLY at low dose (<=150 mg) and no other NSAIDs are present.
    Used to avoid triggering NSAID+CKD rule for antiplatelet-dose aspirin.
    """
    # Gather med resources likely containing name/dose
    med_resources = (
        _get_resource_entries(bundle, "MedicationStatement")
        + _get_resource_entries(bundle, "MedicationRequest")
        + _get_resource_entries(bundle, "MedicationDispense")
    )

    any_other_nsaid = False
    found_low_dose_aspirin = False
    found_any_aspirin = False

    for m in med_resources:
        names = []
        names += _codeable_concepts_to_text(m.get("medicationCodeableConcept"))
        # MedicationReference/contained fallback
        if m.get("medicationReference"):
            ref = m["medicationReference"]
            ref_str = ref.get("reference") if isinstance(ref, dict) else str(ref)
            # We won’t resolve references here; classification is name-based
            names.append(ref_str or "")
        if m.get("contained"):
            for cont in m.get("contained") or []:
                if isinstance(cont, dict):
                    names += _codeable_concepts_to_text(cont.get("code"))

        norm_names = {_norm(n) for n in names if n}
        is_aspirin = any("aspirin" in n for n in norm_names)
        is_other_nsaid = any((drug in n) for n in norm_names for drug in (NSAIDS - {"aspirin"}))

        if is_other_nsaid:
            any_other_nsaid = True

        if is_aspirin:
            found_any_aspirin = True
            # check for low-dose in dosage/dosageInstruction
            dos_list = m.get("dosage") or m.get("dosageInstruction") or []
            low_dose_here = False
            for d in dos_list:
                if not isinstance(d, dict):
                    continue
                # doseAndRate[0].doseQuantity or doseQuantity
                dq = None
                dar = d.get("doseAndRate")
                if isinstance(dar, list) and dar:
                    dq = dar[0].get("doseQuantity")
                dq = dq or d.get("doseQuantity")
                if isinstance(dq, dict):
                    val = dq.get("value")
                    unit = dq.get("unit") or dq.get("code")
                    try:
                        if val is not None and float(val) <= 150 and unit and "mg" in _norm(str(unit)):
                            low_dose_here = True
                            break
                    except Exception:
                        pass
            if low_dose_here:
                found_low_dose_aspirin = True

    # Only low-dose aspirin present, no other NSAIDs
    return (found_low_dose_aspirin and not any_other_nsaid) or (found_any_aspirin and not any_other_nsaid and found_low_dose_aspirin)


def _ingest_detected_issues(bundle: Dict[str, Any]) -> List[str]:
    """
    Collect DetectedIssue.details deterministically into notes (severity if present).
    """
    out: List[str] = []
    for di in _get_resource_entries(bundle, "DetectedIssue"):
        if not isinstance(di, dict):
            continue
        sev = _norm(di.get("severity") or "") or "unspecified"
        detail = (di.get("detail") or "").strip()
        if detail:
            out.append(f"DetectedIssue ({sev}): {detail}")
    return sorted(set(out), key=_norm)


# ----------------------------
# Risk engine with provenance
# ----------------------------
def _derive_risks(cond_flags: Dict[str, bool], med_flags: Dict[str, bool], abn_vitals: List[str], ignore_nsaid_ckd: bool) -> Tuple[List[Dict], List[Dict], List[str], List[str]]:
    high: List[Dict[str, Any]] = []
    moderate: List[Dict[str, Any]] = []
    notes: List[str] = []

    def add(level, message, c=None, m=None, o=None):
        entry = {"message": message, "trigger": {"conditions": c or [], "meds": m or [], "observations": o or []}}
        (high if level == "high" else moderate).append(entry)

    # Comorbidity
    if cond_flags["stroke"] and cond_flags["hypertension"]:
        add("high", "History of stroke with concurrent hypertension consider secondary prevention and BP control",
            ["stroke", "hypertension"])
    if cond_flags["heart_failure"] and cond_flags["ckd"]:
        add("moderate", "Heart failure with chronic kidney disease monitor renal function", ["heart_failure", "ckd"])

    # Drug-condition
    if med_flags["nsaid"] and cond_flags["ckd"] and not ignore_nsaid_ckd:
        add("high", "NSAID use in chronic kidney disease potential nephrotoxicity risk", ["ckd"], ["nsaid"])
    if med_flags["beta_blocker"] and cond_flags["asthma"]:
        add("high", "Beta-blocker use in asthma risk of bronchospasm", ["asthma"], ["beta_blocker"])

    # Drug-lab (represented via abnormal vitals list keywords if present)
    hyperk = any("hyperkalemia" in _norm(v) for v in abn_vitals)
    if (med_flags["acei"] or med_flags["arb"]) and hyperk:
        add("high", "RAAS blockade with hyperkalemia risk of arrhythmia", ["hyperkalemia"], ["acei/arb"])

    if abn_vitals:
        notes.append("Abnormal vitals present")

    # Deterministic sorting
    high.sort(key=lambda x: _norm(x["message"]))
    moderate.sort(key=lambda x: _norm(x["message"]))
    abn_vitals.sort(key=_norm)
    notes.sort(key=_norm)

    return high, moderate, abn_vitals, notes


def _compose_summary(high, moderate, abn):
    return f"{len(high)} high risk, {len(moderate)} moderate risk, {len(abn)} abnormal vital findings" if high or moderate or abn else "No red flags detected"


# ----------------------------
# Ollama / Mistral optional
# ----------------------------
def _ollama_available() -> bool:
    try:
        subprocess.run(["ollama", "list"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False


def _mistral_available() -> bool:
    try:
        out = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        return "mistral" in out.stdout.lower()
    except Exception:
        return False


def _generate_fluent(report: Dict[str, Any]) -> Optional[str]:
    if not (_ollama_available() and _mistral_available()):
        return None
    prompt = (
        "Summarize this safety report clearly for a patient without adding new facts:\n"
        f"{json.dumps(report, ensure_ascii=False)}"
    )
    try:
        p = subprocess.run(["ollama", "run", "mistral"], input=prompt, capture_output=True, text=True, check=True)
        return p.stdout.strip()
    except Exception:
        return None


# ----------------------------
# Main execution
# ----------------------------
def run() -> Tuple[Dict[str, Any], str, Optional[str]]:
    bundle = _read_json(FHIR_BUNDLE_PATH)
    if not bundle:
        empty = {"high_risk": [], "moderate_risk": [], "abnormal_vitals": [], "notes": ["No FHIR data"], "summary": "No red flags detected"}
        return empty, "No safety analysis performed", None

    # Collect core inputs
    conds = _extract_condition_names(_get_resource_entries(bundle, "Condition"))
    meds_resources = (
        _get_resource_entries(bundle, "MedicationStatement")
        + _get_resource_entries(bundle, "MedicationRequest")
        + _get_resource_entries(bundle, "MedicationDispense")
        + _get_resource_entries(bundle, "Medication")
    )
    meds = _extract_medication_names(meds_resources)
    obs = _extract_observations(_get_resource_entries(bundle, "Observation"))

    cond_flags = _normalize_conditions(conds)
    med_flags = _classify_medications(meds)

    # Low-dose aspirin exception (only aspirin present as NSAID at ≤150 mg)
    ignore_nsaid_ckd = _has_low_dose_aspirin_only(bundle)

    abn = _vital_thresholds(obs)
    high, moderate, abn_sorted, notes = _derive_risks(cond_flags, med_flags, abn, ignore_nsaid_ckd)

    # Ingest DetectedIssue details into notes (deterministic)
    notes.extend(_ingest_detected_issues(bundle))
    notes = sorted(set(notes), key=_norm)

    # Create the final report
    report = {
        "high_risk": high,
        "moderate_risk": moderate,
        "abnormal_vitals": abn_sorted,
        "notes": notes,
        "summary": _compose_summary(high, moderate, abn_sorted)
    }

    # Save deterministic TXT
    lines = ["SAFETY SUMMARY", "", f"Summary: {report['summary']}", ""]
    if high:
        lines.append("High Risk")
        for h in high:
            lines.append(f"  • {h['message']}")
        lines.append("")
    if moderate:
        lines.append("Moderate Risk")
        for m in moderate:
            lines.append(f"  • {m['message']}")
        lines.append("")
    if abn_sorted:
        lines.append("Abnormal Vitals")
        for v in abn_sorted:
            lines.append(f"  • {v}")
        lines.append("")
    if notes:
        lines.append("Notes")
        for n in notes:
            lines.append(f"  • {n}")
    summary_txt = "\n".join(lines)

    # Write the report to JSON and text files
    _write_json(SAFETY_JSON_PATH, report)
    _write_text(SAFETY_TXT_PATH, summary_txt)

    # Optionally, generate a fluent version of the safety report using Mistral
    fluent = _generate_fluent(report)
    if fluent:
        _write_text(SAFETY_FLUENT_PATH, fluent)

    return report, summary_txt, fluent


# Backward-compatible alias expected by web_app
def run_safety_check() -> Tuple[Dict[str, Any], str, Optional[str]]:
    return run()


if __name__ == "__main__":
    rep, txt, fl = run()
    print(f"Wrote JSON: {SAFETY_JSON_PATH}")
    print(f"Wrote TXT: {SAFETY_TXT_PATH}")
    if fl:
        print(f"Wrote fluent TXT: {SAFETY_FLUENT_PATH}")

