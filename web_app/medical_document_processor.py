"""
Medical Document Processor - Integration with AI Medical Pipeline
Integrates OCR, NER, Entity Linking, and Safety Checker for insurance quotes
"""

import os
import sys
import json
import tempfile
from typing import Dict, List, Tuple, Optional

# Add project root and this web_app dir to sys.path so we can import either
# the original ai_medical modules or the alternative UC1_models pipeline
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WEB_APP_DIR = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if WEB_APP_DIR not in sys.path:
    sys.path.insert(0, WEB_APP_DIR)

# =============================
# Availability flags (granular)
# =============================
# We separate the heavy NLP (OCR → Sectionizer → NER → Linking) from the
# lightweight clinical safety heuristics so that the app can still benefit
# from risk assessment even when NLP models aren't available on the system.

# NLP pipeline availability (SpaCy models, etc.)
NLP_AVAILABLE = False

# Preferred: Local UC1_models pipeline (web_app/UC1_models)
try:
    from UC1_models.ocr.extract_text import extract_text_from_pdf  # type: ignore
    from UC1_models.sectionizer.sectionize_text import sectionize_text  # type: ignore
    from UC1_models.ner.extract_entities import extract_entities_from_sections  # type: ignore
    from UC1_models.linker.entity_linking import link_entities  # type: ignore
    NLP_AVAILABLE = True
    print("AI NLP pipeline: UC1_models (web_app) active")
except Exception as uc1_err:
    # Fallback: ai_medical package at project root
    try:
        from ai_medical.ocr.extract_text import extract_text_from_pdf  # type: ignore
        from ai_medical.sectionizer.sectionize_text import sectionize_text  # type: ignore
        from ai_medical.ner.extract_entities import extract_entities_from_sections  # type: ignore
        from ai_medical.linker.entity_linking import link_entities  # type: ignore
        NLP_AVAILABLE = True
        print("AI NLP pipeline: ai_medical active")
    except Exception as am_err:
        print(f"Info: AI NLP pipeline disabled: UC1_models error={uc1_err} | ai_medical error={am_err}")
        NLP_AVAILABLE = False

# Safety checker availability (pure-Python, no heavy deps)
SAFETY_AVAILABLE = False
try:
    # Prefer UC1_models safety if available, else ai_medical
    try:
        from UC1_models.safety.safety_check import (  # type: ignore
            _extract_condition_names,  # noqa: F401
            _extract_medication_names,  # noqa: F401
            _classify_medications,
            _normalize_conditions,
        )
        SAFETY_AVAILABLE = True
        print("Safety checker: UC1_models active")
    except Exception:
        from ai_medical.safety.safety_check import (  # type: ignore
            _extract_condition_names,  # noqa: F401
            _extract_medication_names,  # noqa: F401
            _classify_medications,
            _normalize_conditions,
        )
        SAFETY_AVAILABLE = True
        print("Safety checker: ai_medical active")
except Exception as e:
    print(f"Info: Safety checker unavailable: {e}")
    SAFETY_AVAILABLE = False

# Backward-compatible flag used by templates to show/hide document upload
AI_MEDICAL_AVAILABLE = NLP_AVAILABLE


class MedicalDocumentProcessor:
    """
    Processes uploaded medical documents through AI pipeline
    to auto-fill insurance quote form
    """
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def process_document(self, file_path: str, verbose: bool = True) -> Dict:
        """
        Main pipeline: PDF/TXT → OCR → Sectionizer → NER → Entity Linking
        
        Returns:
            {
                'success': bool,
                'conditions': List[str],
                'medications': List[str],
                'procedures': List[str],
                'observations': Dict,
                'raw_text': str,
                'error': Optional[str]
            }
        """
        if not AI_MEDICAL_AVAILABLE:
            return {
                'success': False,
                'error': 'AI Medical pipeline not available',
                'conditions': [],
                'medications': [],
                'procedures': [],
                'observations': {},
                'raw_text': ''
            }
        
        try:
            # Step 1: Extract text from file (PDF or TXT)
            if verbose:
                print("Step 1: Extracting text from document...")
            
            # Check file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Verify file exists and has content
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'File not found: {file_path}',
                    'conditions': [],
                    'medications': [],
                    'procedures': [],
                    'observations': {},
                    'raw_text': ''
                }
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return {
                    'success': False,
                    'error': 'Uploaded file is empty (0 bytes)',
                    'conditions': [],
                    'medications': [],
                    'procedures': [],
                    'observations': {},
                    'raw_text': ''
                }
            
            if verbose:
                print(f"  → File: {os.path.basename(file_path)} ({file_size} bytes)")
            
            if file_ext == '.txt':
                # Read text file directly
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        raw_text = f.read()
                    if verbose:
                        print(f"  → Read {len(raw_text)} characters from text file")
                except Exception as txt_err:
                    return {
                        'success': False,
                        'error': f'Error reading text file: {str(txt_err)}',
                        'conditions': [],
                        'medications': [],
                        'procedures': [],
                        'observations': {},
                        'raw_text': ''
                    }
            elif file_ext == '.pdf':
                # Use OCR for PDF
                try:
                    raw_text = extract_text_from_pdf(file_path, verbose=False)
                    if verbose:
                        print(f"  → Extracted {len(raw_text)} characters from PDF")
                except Exception as pdf_err:
                    return {
                        'success': False,
                        'error': f'PDF extraction failed: {str(pdf_err)}',
                        'conditions': [],
                        'medications': [],
                        'procedures': [],
                        'observations': {},
                        'raw_text': ''
                    }
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file type: {file_ext}',
                    'conditions': [],
                    'medications': [],
                    'procedures': [],
                    'observations': {},
                    'raw_text': ''
                }
            
            if not raw_text or len(raw_text.strip()) < 10:
                return {
                    'success': False,
                    'error': 'No text extracted from document',
                    'conditions': [],
                    'medications': [],
                    'procedures': [],
                    'observations': {},
                    'raw_text': ''
                }
            
            # Step 2: Sectionize - Parse document structure
            if verbose:
                print("Step 2: Sectionizing document...")
            
            # Save text to temp file for sectionizer
            text_temp_path = os.path.join(self.temp_dir, 'insurance_doc_text.txt')
            with open(text_temp_path, 'w', encoding='utf-8') as f:
                f.write(raw_text)
            
            # Sectionize (function returns dict, doesn't write to file)
            sections = sectionize_text(text_temp_path, verbose=False)
            
            # Save sectionized data
            sectionized_temp_path = os.path.join(self.temp_dir, 'insurance_doc_sections.json')
            with open(sectionized_temp_path, 'w', encoding='utf-8') as f:
                json.dump(sections, f, indent=4, ensure_ascii=False)
            
            # Step 3: NER - Extract entities
            if verbose:
                print("Step 3: Extracting medical entities...")
            
            # Load sectionized data
            with open(sectionized_temp_path, 'r', encoding='utf-8') as f:
                sections = json.load(f)
            
            # Extract entities (function returns dict, doesn't write to file)
            ner_results = extract_entities_from_sections(sections)
            
            # Save NER results
            ner_temp_path = os.path.join(self.temp_dir, 'insurance_doc_ner.json')
            with open(ner_temp_path, 'w', encoding='utf-8') as f:
                json.dump(ner_results, f, indent=4, ensure_ascii=False)
            
            # Step 4: Entity Linking - Link to medical ontologies
            if verbose:
                print("Step 4: Linking entities to medical ontologies...")
            
            linked_temp_path = os.path.join(self.temp_dir, 'insurance_doc_linked.json')
            link_entities(ner_temp_path, linked_temp_path)
            
            # Step 5: Parse results
            if verbose:
                print("Step 5: Parsing extracted data...")
            
            result = self._parse_linked_entities(linked_temp_path)
            result['raw_text'] = raw_text[:500]  # First 500 chars for preview
            result['success'] = True
            
            # Cleanup temp files
            for temp_file in [text_temp_path, sectionized_temp_path, ner_temp_path, linked_temp_path]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Document processing failed: {str(e)}',
                'conditions': [],
                'medications': [],
                'procedures': [],
                'observations': {},
                'raw_text': ''
            }
    
    def _parse_linked_entities(self, linked_json_path: str) -> Dict:
        """
        Parse linked entities JSON to extract conditions, medications, etc.
        """
        with open(linked_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conditions = []
        medications = []
        procedures = []
        observations = {}
        
        # Parse each section
        for section_name, entities in data.items():
            if section_name.startswith('_'):  # Skip metadata
                continue
            
            if not isinstance(entities, list):
                continue
            
            for entity in entities:
                label = entity.get('label', '').upper()
                text = entity.get('text', '').strip()
                
                if not text:
                    continue
                
                # Classify by entity type
                if label in ['DISEASE', 'CONDITION']:
                    if text not in conditions:
                        conditions.append(text)
                
                elif label in ['DRUG', 'MEDICATION', 'CHEMICAL']:
                    # Check if it's actually a medication
                    if self._is_likely_medication(text):
                        if text not in medications:
                            medications.append(text)
                
                elif label in ['PROCEDURE', 'TREATMENT']:
                    if text not in procedures:
                        procedures.append(text)
                
                elif label == 'OBSERVATION':
                    # Try to extract vital signs or lab values
                    obs_data = self._parse_observation(text)
                    if obs_data:
                        observations.update(obs_data)
        
        return {
            'conditions': conditions,
            'medications': medications,
            'procedures': procedures,
            'observations': observations
        }
    
    def _is_likely_medication(self, text: str) -> bool:
        """Check if text is likely a medication name"""
        text_lower = text.lower()
        
        # Common medication suffixes
        medication_suffixes = [
            'pril', 'olol', 'statin', 'mycin', 'cillin',
            'floxacin', 'dipine', 'sartan', 'zole', 'azole'
        ]
        
        # Common medication patterns
        medication_patterns = [
            r'\d+\s*mg', r'\d+\s*mcg', r'\d+\s*ml',
            'tablet', 'capsule', 'injection', 'suspension'
        ]
        
        import re
        for pattern in medication_patterns:
            if re.search(pattern, text_lower):
                return True
        
        for suffix in medication_suffixes:
            if text_lower.endswith(suffix):
                return True
        
        # Length check - medications are usually 4-25 characters
        if 4 <= len(text) <= 25 and text[0].isupper():
            return True
        
        return False
    
    def _parse_observation(self, text: str) -> Optional[Dict]:
        """Parse observation text to extract vital signs or lab values"""
        import re
        
        observations = {}
        text_lower = text.lower()
        
        # Blood pressure pattern
        bp_match = re.search(r'(\d{2,3})/(\d{2,3})', text)
        if bp_match and 'pressure' in text_lower:
            observations['blood_pressure'] = f"{bp_match.group(1)}/{bp_match.group(2)}"
        
        # BMI pattern
        bmi_match = re.search(r'bmi[:\s]*(\d+\.?\d*)', text_lower)
        if bmi_match:
            observations['bmi'] = float(bmi_match.group(1))
        
        # Weight pattern
        weight_match = re.search(r'(\d+\.?\d*)\s*(kg|lbs?)', text_lower)
        if weight_match and 'weight' in text_lower:
            observations['weight'] = f"{weight_match.group(1)} {weight_match.group(2)}"
        
        # Glucose pattern
        glucose_match = re.search(r'glucose[:\s]*(\d+)', text_lower)
        if glucose_match:
            observations['glucose'] = f"{glucose_match.group(1)} mg/dL"
        
        # Cholesterol pattern
        chol_match = re.search(r'cholesterol[:\s]*(\d+)', text_lower)
        if chol_match:
            observations['cholesterol'] = f"{chol_match.group(1)} mg/dL"
        
        return observations if observations else None


class EnhancedRiskAssessment:
    """
    Enhanced risk assessment using Safety Checker
    Integrates medical safety rules for insurance risk scoring
    """
    
    def __init__(self):
        self.available = AI_MEDICAL_AVAILABLE
    
    def assess_safety_risks(self, conditions: List[str], medications: List[str]) -> Dict:
        """
        Run safety checks on conditions and medications
        
        Returns:
            {
                'risk_factors': List[Dict],
                'severity': str,  # 'low', 'moderate', 'high'
                'recommendations': List[str]
            }
        """
        if not self.available:
            return {
                'risk_factors': [],
                'severity': 'unknown',
                'recommendations': []
            }
        
        try:
            # Normalize conditions
            normalized_conditions = _normalize_conditions(conditions)
            
            # Classify medications
            medication_classes = _classify_medications(medications)
            
            risk_factors = []
            recommendations = []
            
            # Check for drug-drug interactions
            if self._check_anticoagulant_nsaid(medication_classes):
                risk_factors.append({
                    'type': 'drug_interaction',
                    'severity': 'high',
                    'description': 'Anticoagulant + NSAID interaction detected'
                })
                recommendations.append('Medical monitoring required for bleeding risk')
            
            # Check for comorbidities
            if 'diabetes' in normalized_conditions and 'ckd' in normalized_conditions:
                risk_factors.append({
                    'type': 'comorbidity',
                    'severity': 'high',
                    'description': 'Diabetes + Chronic Kidney Disease'
                })
                recommendations.append('Requires specialized coverage for dialysis')
            
            if 'heart_failure' in normalized_conditions and 'copd' in normalized_conditions:
                risk_factors.append({
                    'type': 'comorbidity',
                    'severity': 'moderate',
                    'description': 'Heart failure + COPD comorbidity'
                })
                recommendations.append('Pulmonary and cardiac monitoring needed')
            
            # Determine overall severity
            if any(rf['severity'] == 'high' for rf in risk_factors):
                severity = 'high'
            elif any(rf['severity'] == 'moderate' for rf in risk_factors):
                severity = 'moderate'
            else:
                severity = 'low'
            
            return {
                'risk_factors': risk_factors,
                'severity': severity,
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'risk_factors': [],
                'severity': 'unknown',
                'recommendations': [f'Error in safety assessment: {str(e)}']
            }
    
    def _check_anticoagulant_nsaid(self, medication_classes: Dict) -> bool:
        """Check for dangerous anticoagulant + NSAID combination"""
        has_anticoagulant = medication_classes.get('anticoagulant', False)
        has_nsaid = medication_classes.get('nsaid', False)
        
        return has_anticoagulant and has_nsaid


# Singleton instances
document_processor = MedicalDocumentProcessor()
risk_assessor = EnhancedRiskAssessment()


def process_uploaded_document(file_path: str) -> Dict:
    """Convenience function to process uploaded medical document"""
    return document_processor.process_document(file_path, verbose=True)


def assess_medical_safety(conditions: List[str], medications: List[str]) -> Dict:
    """Convenience function for safety assessment"""
    return risk_assessor.assess_safety_risks(conditions, medications)

