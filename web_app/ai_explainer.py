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
        "You are an insurance explainer. Write a concise, patient-safe reason "
        "why the following plan fits the user's profile. 2 sentences max. "
        "No medical advice, no hallucinations.\n\n"
        f"Plan: {product.get('plan_type')} from {product.get('provider')} | "
        f"Monthly premium: ${product.get('monthly_premium')} | Coverage: ${product.get('coverage_amount')} | "
        f"Deductible: ${product.get('annual_deductible')} | Max OOP: ${product.get('max_out_of_pocket')}\n"
        f"Key benefits: {key_cov}. Exclusions: {exclusions}.\n"
        f"User profile: conditions=[{conditions}], income_bracket={income}, risk={round(risk_score,1)}.\n"
        "Explain why this plan matches the needs, referencing coverage/affordability."
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
                            save_dir: str, request_id: str, product_id: str) -> Dict[str, str]:
    """Generate rationales with llama3.1 and mistral, save to disk, return texts.

    Files saved to: <save_dir>/<request_id>_<product_id>_{model}.txt
    """
    os.makedirs(save_dir, exist_ok=True)
    prompt = _build_prompt(product, profile, risk_score)
    try:
        print(f"[AI_EXPLAINER] Prompt for request={request_id} product={product_id}:\n{prompt}\n---")
    except Exception:
        pass

    results: Dict[str, str] = {}

    model = "mistral:7b-instruct"
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

    return results


