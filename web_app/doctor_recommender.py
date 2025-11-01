"""
AI-powered doctor recommendation system using Mistral:7b-instruct.

Analyzes clinical analysis results and recommends suitable doctors based on:
- Medical conditions found
- Medications prescribed
- Risk level
- Specializations needed
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional


def _build_doctor_recommendation_prompt(clinical_result: Dict[str, Any], 
                                       available_doctors: List[Dict[str, Any]]) -> str:
    """Build a prompt for Mistral to recommend suitable doctors."""
    
    # Extract clinical information
    conditions = clinical_result.get('conditions', [])
    medications = clinical_result.get('medications', [])
    risk_level = clinical_result.get('risk_level', 'UNKNOWN')
    observations = clinical_result.get('observations', [])
    procedures = clinical_result.get('procedures', [])
    
    # Format doctor list for prompt
    doctor_list = []
    for i, doc in enumerate(available_doctors[:30], 1):  # Limit to 30 for token efficiency
        specialization = doc.get('specialization', 'Unknown')
        name = doc.get('name', doc.get('username', 'Unknown'))
        doctor_list.append(f"{i}. Dr. {name} - Specialization: {specialization}")
    
    doctors_text = "\n".join(doctor_list)
    
    # Build prompt
    prompt = f"""You are a medical assistant helping a patient find the most suitable doctor for a medical review based on their clinical analysis results.

CLINICAL ANALYSIS SUMMARY:
- Conditions Found: {', '.join(conditions[:10]) if conditions else 'None specified'}
- Medications: {', '.join(medications[:10]) if medications else 'None specified'}
- Risk Level: {risk_level}
- Observations: {', '.join(observations[:5]) if observations else 'None'}
- Procedures: {', '.join(procedures[:5]) if procedures else 'None'}

AVAILABLE DOCTORS:
{doctors_text}

INSTRUCTIONS:
1. Analyze the clinical data and identify which medical specialties would be most appropriate for review.
2. Select the top 5-8 doctors from the list who would be most suitable to review this case.
3. Consider matching specializations with the conditions, medications, and risk factors present.
4. Consider general practitioners if multiple specialties are involved or if primary care is appropriate.
5. For high-risk cases, prioritize specialists relevant to the conditions.

OUTPUT FORMAT (JSON array of doctor numbers only, in order of suitability):
[1, 5, 12, 8, 3]

Return ONLY the JSON array, no additional text or explanation."""

    return prompt


def _run_ollama(model: str, prompt: str, timeout: int = 30) -> str:
    """Run an Ollama model locally and return its response text."""
    ollama_bin = os.environ.get("OLLAMA_BIN", "ollama")
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
            return ""
        out = proc.stdout.strip() or proc.stderr.strip()
        return out
    except Exception as e:
        print(f"[Doctor Recommender] Ollama error: {e}")
        return ""


def _parse_llm_recommendations(llm_output: str, available_doctors: List[Dict[str, Any]]) -> List[int]:
    """Parse LLM output to extract doctor IDs.
    Returns list of doctor indices (0-based) from available_doctors list.
    """
    try:
        # Try to extract JSON array from output
        # Look for patterns like [1, 5, 12] or [1,5,12]
        import re
        
        # Find JSON array in the output
        json_match = re.search(r'\[[\s\d,]+\]', llm_output)
        if json_match:
            numbers_str = json_match.group(0)
            numbers = json.loads(numbers_str)
            
            # Convert to 0-based indices (subtract 1 from each number)
            indices = [int(n) - 1 for n in numbers if isinstance(n, int) and 1 <= n <= len(available_doctors)]
            
            # Remove duplicates and invalid indices
            valid_indices = []
            seen = set()
            for idx in indices:
                if 0 <= idx < len(available_doctors) and idx not in seen:
                    valid_indices.append(idx)
                    seen.add(idx)
            
            return valid_indices[:8]  # Limit to top 8
        
        # Fallback: try to find numbers in the text
        numbers = re.findall(r'\b(\d+)\b', llm_output)
        if numbers:
            indices = [int(n) - 1 for n in numbers[:8] if n.isdigit() and 1 <= int(n) <= len(available_doctors)]
            # Remove duplicates
            seen = set()
            valid_indices = []
            for idx in indices:
                if 0 <= idx < len(available_doctors) and idx not in seen:
                    valid_indices.append(idx)
                    seen.add(idx)
            return valid_indices[:8]
        
        return []
    except Exception as e:
        print(f"[Doctor Recommender] Error parsing LLM output: {e}")
        return []


def recommend_doctors(clinical_result: Dict[str, Any], 
                     available_doctors: List[Dict[str, Any]],
                     model: str = "mistral:7b-instruct") -> List[Dict[str, Any]]:
    """Recommend suitable doctors based on clinical analysis results.
    
    Args:
        clinical_result: Dictionary containing clinical analysis results
            (conditions, medications, risk_level, observations, procedures, etc.)
        available_doctors: List of doctor dictionaries from database
        model: Ollama model name to use (default: mistral:7b-instruct)
    
    Returns:
        List of recommended doctor dictionaries (up to 8), sorted by suitability
    """
    if not available_doctors:
        return []
    
    # Limit to first 30 doctors to keep prompt manageable
    doctors_for_analysis = available_doctors[:30]
    
    # Build prompt
    prompt = _build_doctor_recommendation_prompt(clinical_result, doctors_for_analysis)
    
    # Get LLM recommendation
    print(f"[Doctor Recommender] Analyzing {len(doctors_for_analysis)} doctors for recommendation...")
    llm_output = _run_ollama(model, prompt, timeout=30)
    
    if not llm_output:
        print("[Doctor Recommender] LLM returned empty output, using fallback recommendation")
        # Fallback: return first 5 doctors (simple matching by specialization keywords)
        return _fallback_recommendation(clinical_result, doctors_for_analysis)
    
    print(f"[Doctor Recommender] LLM output: {llm_output[:200]}...")
    
    # Parse recommendations
    recommended_indices = _parse_llm_recommendations(llm_output, doctors_for_analysis)
    
    if not recommended_indices:
        print("[Doctor Recommender] Could not parse recommendations, using fallback")
        return _fallback_recommendation(clinical_result, doctors_for_analysis)
    
    # Build list of recommended doctors
    recommended = []
    for idx in recommended_indices:
        if 0 <= idx < len(doctors_for_analysis):
            recommended.append(doctors_for_analysis[idx])
    
    print(f"[Doctor Recommender] Recommended {len(recommended)} doctors")
    return recommended


def _fallback_recommendation(clinical_result: Dict[str, Any], 
                            available_doctors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Fallback recommendation using simple keyword matching.
    Returns top 5 doctors based on specialization keywords matching conditions.
    """
    conditions = [c.lower() for c in clinical_result.get('conditions', [])]
    
    # Map common conditions to specializations
    condition_to_specialization = {
        'cardiac': ['cardiology', 'cardiologist'],
        'heart': ['cardiology', 'cardiologist'],
        'hypertension': ['cardiology', 'general medicine', 'internal medicine'],
        'diabetes': ['endocrinology', 'general medicine', 'internal medicine'],
        'diabetic': ['endocrinology', 'general medicine'],
        'neurological': ['neurology', 'neurologist'],
        'stroke': ['neurology', 'neurologist'],
        'epilepsy': ['neurology', 'neurologist'],
        'dermatology': ['dermatology', 'dermatologist'],
        'skin': ['dermatology', 'dermatologist'],
        'respiratory': ['respiratory', 'pulmonology'],
        'asthma': ['respiratory', 'pulmonology', 'general medicine'],
        'orthopedic': ['orthopedics', 'orthopedic'],
        'bone': ['orthopedics', 'orthopedic'],
        'mental': ['psychiatry', 'psychiatrist', 'psychology'],
        'depression': ['psychiatry', 'psychiatrist'],
        'anxiety': ['psychiatry', 'psychiatrist'],
        'cancer': ['oncology', 'oncologist'],
        'tumor': ['oncology', 'oncologist'],
    }
    
    # Score doctors based on specialization matches
    scored_doctors = []
    for doc in available_doctors[:20]:  # Limit to 20 for fallback
        score = 0
        specialization = doc.get('specialization', '').lower()
        
        # Check if specialization matches any condition-related keywords
        for condition in conditions:
            for keyword, specializations in condition_to_specialization.items():
                if keyword in condition:
                    for spec in specializations:
                        if spec in specialization:
                            score += 1
        
        # Boost score for general practitioners if no specific match
        if 'general' in specialization or 'gp' in specialization or 'family' in specialization:
            score += 0.5
        
        scored_doctors.append((score, doc))
    
    # Sort by score (descending) and return top 5
    scored_doctors.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored_doctors[:5] if score > 0] or available_doctors[:5]

