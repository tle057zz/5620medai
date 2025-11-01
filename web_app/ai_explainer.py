"""
AI explainer for insurance quotes using local Ollama models.

Generates short, patient-safe rationales using a free local model:
- mistral:7b-instruct

If Ollama is not installed or a model call fails, returns a safe fallback
string and continues without raising.
"""

from __future__ import annotations

import os
import json
import subprocess
from typing import Dict


def _build_prompt(product: dict, profile: dict, risk_score: float) -> str:
    """Compose a concise prompt for rationale generation."""
    key_cov = ", ".join(product.get("coverage_details", [])[:4])
    exclusions = ", ".join(product.get("exclusions", [])[:3])
    conditions = ", ".join(profile.get("conditions", [])) or "(none specified)"
    income = profile.get("income_bracket", "middle")

    return (
        "You are a data analyst  and an insurance explainer. Write a concise, patient-safe reason "
        "why the following plan fits the user's profile. Analyze Medical History, Medical current data, income and employment with each one for 1 paragraph of 3 sentences each. "
        "No medical advice, no hallucinations.\n\n"
        f"Plan: {product.get('plan_type')} from {product.get('provider')} | "
        f"Monthly premium: ${product.get('monthly_premium')} | Coverage: ${product.get('coverage_amount')} | "
        f"Deductible: ${product.get('annual_deductible')} | Max OOP: ${product.get('max_out_of_pocket')}\n"
        f"Key benefits: {key_cov}. Exclusions: {exclusions}.\n"
        f"User profile: conditions=[{conditions}], income_bracket={income}, risk={round(risk_score,1)}.\n"
        "Make Explain very detailed why this plan matches the needs, referencing coverage/affordability and some other aspects including Medical History, Medical current data, income and employment."
    )


def _run_ollama(model: str, prompt: str, timeout: int = 25) -> str:
    """Run an Ollama model locally and return its response text."""
    ollama_bin = os.environ.get("OLLAMA_BIN", "ollama")
    # Silence huggingface tokenizers warning in subprocess environments
    env = os.environ.copy()
    env.setdefault("TOKENIZERS_PARALLELISM", "false")
    try:
        proc = subprocess.run(
            [ollama_bin, "run", model, prompt],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        if proc.returncode != 0:
            return ""  # signal failure -> caller will fallback to baseline only
        out = proc.stdout.strip() or proc.stderr.strip()
        # Some ollama builds stream JSON lines; keep simple text fallback
        return out[-2000:]  # trim to a safe length
    except Exception as e:
        return ""  # treat as failure so UI shows baseline only


def generate_ai_rationales(product: dict, profile: dict, risk_score: float,
                            save_dir: str, request_id: str, product_id: str,
                            progress_cb=None, provider: str | None = None,
                            current: int | None = None, total: int | None = None) -> Dict[str, str]:
    """Generate rationales with llama3.1 and mistral, save to disk, return texts.

    Files saved to: <save_dir>/<request_id>_<product_id>_{model}.txt
    """
    os.makedirs(save_dir, exist_ok=True)
    prompt = _build_prompt(product, profile, risk_score)
    if progress_cb:
        try:
            label = provider or product.get('provider')
            suffix = f" ({current}/{total})" if (current and total) else ""
            progress_cb(82, f"AI analyzer: preparing explanation for {label}{suffix}")
        except Exception:
            pass
    try:
        print(f"[AI_EXPLAINER] Prompt for request={request_id} product={product_id}:\n{prompt}\n---")
    except Exception:
        pass

    results: Dict[str, str] = {}

    model = "mistral:7b-instruct"
    if progress_cb:
        try:
            label = provider or product.get('provider')
            suffix = f" ({current}/{total})" if (current and total) else ""
            progress_cb(85, f"AI analyzer: generating explanation for {label}{suffix}")
        except Exception:
            pass
    text = _run_ollama(model, prompt)
    results[model] = text
    try:
        path = os.path.join(save_dir, f"{request_id}_{product_id}_{model.replace(':','-')}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        # Best-effort write; ignore if path not writable
        pass

    # Also store a combined JSON for convenience
    try:
        path_json = os.path.join(save_dir, f"{request_id}_{product_id}_rationales.json")
        with open(path_json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    if progress_cb:
        try:
            assessed = f", {current} insurances have been assessed" if current else ""
            progress_cb(90, f"AI analyzer: explanation ready{assessed}")
        except Exception:
            pass

    return results


def score_plan_with_ai(product: dict, profile: dict, risk_score: float, progress_cb=None) -> Dict[str, int]:
    """Return AI-estimated scores for suitability, cost, coverage (0-100 each).

    Uses mistral:7b-instruct locally via Ollama. On failure, returns empty dict.
    """
    prompt = (
        "You are an insurance scoring assistant. Score a health insurance plan for a user.\n"
        "Return STRICT JSON with integer fields: {\"suitability\":0-100, \"cost\":0-100, \"coverage\":0-100}.\n"
        "Do not add any text before or after the JSON.\n\n"
        f"User risk: {round(risk_score,1)}; income_bracket: {profile.get('income_bracket')}; "
        f"conditions: {', '.join(profile.get('conditions', []))}.\n"
        f"Plan: provider={product.get('provider')}, type={product.get('plan_type')}, "
        f"premium=${product.get('monthly_premium')}, deductible=${product.get('annual_deductible')}, "
        f"max_oop=${product.get('max_out_of_pocket')}, coverage_amount=${product.get('coverage_amount')}.\n"
        f"benefits={', '.join(product.get('coverage_details', [])[:8])}; "
        f"exclusions={', '.join(product.get('exclusions', [])[:6])}.\n"
        "Scoring guidance:\n"
        "- suitability: fit to conditions+risk, plan type flexibility, chronic/cancer support.\n"
        "- cost: affordability vs premium+deductible+max_oop for income bracket. Higher = more affordable.\n"
        "- coverage: breadth/depth of benefits and coverage_amount; penalties for many exclusions.\n"
    )
    try:
        if progress_cb:
            try:
                progress_cb(78, f"AI analyzer: scoring {product.get('provider')}")
            except Exception:
                pass
        out = _run_ollama("mistral:7b-instruct", prompt)
        if not out:
            return {}
        # Extract JSON object from raw text
        import json, re
        m = re.search(r"\{[\s\S]*\}", out)
        payload = m.group(0) if m else out
        data = json.loads(payload)
        scores = {
            'suitability': int(max(0, min(100, data.get('suitability', 0)))),
            'cost': int(max(0, min(100, data.get('cost', 0)))),
            'coverage': int(max(0, min(100, data.get('coverage', 0))))
        }
        if progress_cb:
            try:
                progress_cb(80, f"AI analyzer: scored {product.get('provider')}")
            except Exception:
                pass
        return scores
    except Exception:
        return {}


def decide_top_k(profile: dict, risk_score: float, eligible_count: int, progress_cb=None) -> int:
    """Use AI to decide how many quotes to show (realistic top-K).

    Returns an integer in [3, min(eligible_count, 12)]. Fallback to 8 on failure.
    """
    lo = 3
    hi = max(lo, min(eligible_count, 12))
    prompt = (
        "You are an insurance product selection assistant. Determine how many top plans "
        "(top_k) should be shown to the user, balancing choice overload and relevance.\n"
        "Return STRICT JSON: {\"top_k\": <int between lo and hi>} and nothing else.\n\n"
        f"Constraints: lo={lo}, hi={hi}.\n"
        f"Inputs: risk={round(risk_score,1)}, income_bracket={profile.get('income_bracket')}, "
        f"conditions={', '.join(profile.get('conditions', []))}, eligible_count={eligible_count}.\n"
        "Guidance: Higher risk or low income → fewer options (closer to lo).\n"
        "If eligible_count is small, choose min(eligible_count, 5). Most cases should be 6–9.\n"
    )
    try:
        if progress_cb:
            try:
                progress_cb(58, 'AI analyzer: selecting result set size')
            except Exception:
                pass
        out = _run_ollama("mistral:7b-instruct", prompt)
        if not out:
            return 8
        import json, re
        m = re.search(r"\{[\s\S]*\}", out)
        payload = m.group(0) if m else out
        data = json.loads(payload)
        k = int(data.get('top_k', 8))
        return max(lo, min(hi, k))
    except Exception:
        return min(8, hi)

