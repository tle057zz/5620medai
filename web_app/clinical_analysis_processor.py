"""
AI-Assisted Clinical Record Analysis Processor (Saahir Khan)

Complete AI medical pipeline for document ingestion, extraction, explanation, and risk flagging:
1. OCR - Extract clean text from PDFs/images
2. Sectionizer - Structure text into clinical sections
3. NER - Identify medical entities (conditions, medications, observations)
4. Entity Linking - Map to standard codes (SNOMED, ICD-10-AM, RxNorm)
5. FHIR Mapping - Generate FHIR R4 compliant resources
6. Explanation - Patient-friendly summaries
7. Safety Checker - Red-flag detection for emergencies and contraindications
"""

import os
import json
import sys
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path to import ai_medical modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# =============================
# Availability Detection
# =============================
PIPELINE_AVAILABLE = False
SAFETY_AVAILABLE = False

try:
    from ai_medical.ocr.extract_text import extract_text_from_pdf
    from ai_medical.sectionizer.sectionize_text import sectionize_text
    from ai_medical.ner.extract_entities import extract_entities_from_sections
    from ai_medical.linker.entity_linking import link_entities
    from ai_medical.fhir_mapper.fhir_mapping import convert_to_fhir_bundle
    from ai_medical.explain.generate_explanation import to_explanation_json, to_plain_text
    PIPELINE_AVAILABLE = True
    print("✓ AI Medical Pipeline loaded successfully")
except Exception as e:
    print(f"⚠ AI Medical Pipeline unavailable: {e}")
    PIPELINE_AVAILABLE = False

try:
    from ai_medical.safety.safety_check import run_safety_check
    SAFETY_AVAILABLE = True
    print("✓ Safety Checker loaded successfully")
except Exception as e:
    print(f"⚠ Safety Checker unavailable: {e}")
    SAFETY_AVAILABLE = False


# =============================
# Clinical Analysis Result Model
# =============================
class ClinicalAnalysisResult:
    """Stores results from complete AI medical pipeline"""
    
    def __init__(self):
        self.analysis_id = f"CA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.timestamp = datetime.now()
        self.success = False
        self.error_message = None
        
        # Pipeline outputs
        self.extracted_text = None
        self.sections = {}
        self.entities = {}
        self.linked_entities = {}
        self.fhir_bundle = None
        self.explanation = {}
        self.explanation_text = None
        self.safety_report = {}
        
        # Extracted clinical data
        self.patient_name = None
        self.conditions = []
        self.medications = []
        self.observations = []
        self.procedures = []
        
        # Red flags
        self.red_flags = []
        self.risk_level = "unknown"  # low, medium, high, critical
        
        # Metadata
        self.document_type = None
        self.processing_steps = []
    
    def add_processing_step(self, step_name: str, status: str, details: str = ""):
        """Track pipeline progress"""
        self.processing_steps.append({
            "step": step_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        })
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "analysis_id": self.analysis_id,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error_message": self.error_message,
            "patient_name": self.patient_name,
            "conditions": self.conditions,
            "medications": self.medications,
            "observations": self.observations,
            "procedures": self.procedures,
            "red_flags": self.red_flags,
            "risk_level": self.risk_level,
            "explanation_text": self.explanation_text,
            "document_type": self.document_type,
            "processing_steps": self.processing_steps,
            "fhir_bundle": self.fhir_bundle,
            "safety_report": self.safety_report
        }


# =============================
# Helper Functions
# =============================
def extract_text_from_file(file_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Extract text from PDF, TXT, or image file
    Returns: (success, text, error_message)
    """
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            return True, text, None
        
        elif file_ext == '.pdf':
            if not PIPELINE_AVAILABLE:
                return False, None, "PDF processing requires AI pipeline (OCR module)"
            text = extract_text_from_pdf(file_path)
            if not text or len(text.strip()) < 10:
                return False, None, "No text could be extracted from PDF"
            return True, text, None
        
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            if not PIPELINE_AVAILABLE:
                return False, None, "Image processing requires AI pipeline (OCR module)"
            # For images, save temporarily as PDF-like for OCR
            text = extract_text_from_pdf(file_path)
            if not text or len(text.strip()) < 10:
                return False, None, "No text could be extracted from image"
            return True, text, None
        
        else:
            return False, None, f"Unsupported file format: {file_ext}"
    
    except Exception as e:
        return False, None, f"Text extraction failed: {str(e)}"


def extract_clinical_entities(fhir_bundle: Dict) -> Dict[str, List[str]]:
    """
    Extract structured clinical entities from FHIR bundle
    """
    entities = {
        "conditions": [],
        "medications": [],
        "observations": [],
        "procedures": []
    }
    
    if not fhir_bundle or "entry" not in fhir_bundle:
        return entities
    
    for entry in fhir_bundle.get("entry", []):
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")
        
        if resource_type == "Condition":
            code = resource.get("code", {})
            text = code.get("text", "")
            if text:
                entities["conditions"].append(text)
        
        elif resource_type == "MedicationStatement":
            med_code = resource.get("medicationCodeableConcept", {})
            text = med_code.get("text", "")
            if text:
                entities["medications"].append(text)
        
        elif resource_type == "Observation":
            code = resource.get("code", {})
            text = code.get("text", "")
            if text:
                entities["observations"].append(text)
        
        elif resource_type == "Procedure":
            code = resource.get("code", {})
            text = code.get("text", "")
            if text:
                entities["procedures"].append(text)
    
    return entities


def determine_risk_level(safety_report: Dict) -> Tuple[str, List[str]]:
    """
    Analyze safety report and determine overall risk level
    Returns: (risk_level, red_flags)
    """
    red_flags = []
    
    if not safety_report:
        return "unknown", []
    
    # Check drug interactions
    interactions = safety_report.get("drug_interactions", [])
    if interactions:
        for interaction in interactions:
            severity = interaction.get("severity", "").lower()
            if severity in ["high", "critical"]:
                red_flags.append(f"⚠ CRITICAL: {interaction.get('summary', 'Drug interaction detected')}")
            elif severity == "medium":
                red_flags.append(f"⚠ WARNING: {interaction.get('summary', 'Drug interaction')}")
    
    # Check contraindications
    contras = safety_report.get("contraindications", [])
    if contras:
        for contra in contras:
            red_flags.append(f"⚠ CONTRAINDICATION: {contra.get('summary', 'Contraindication detected')}")
    
    # Check vital signs
    vitals = safety_report.get("vital_alerts", [])
    for vital in vitals:
        severity = vital.get("severity", "").lower()
        if severity in ["high", "critical"]:
            red_flags.append(f"⚠ VITAL ALERT: {vital.get('message', 'Abnormal vital sign')}")
    
    # Check comorbidity risks
    comorbidity = safety_report.get("comorbidity_risk", {})
    if comorbidity.get("high_risk_pairs"):
        red_flags.append("⚠ High-risk comorbidity combination detected")
    
    # Determine overall risk level
    if any("CRITICAL" in flag for flag in red_flags):
        return "critical", red_flags
    elif len(red_flags) >= 3 or any("CONTRAINDICATION" in flag for flag in red_flags):
        return "high", red_flags
    elif len(red_flags) > 0:
        return "medium", red_flags
    else:
        return "low", red_flags


# =============================
# Main Processing Function
# =============================
def process_clinical_document(
    file_path: str,
    document_type: str = "medical_report",
    patient_name: Optional[str] = None,
    notes: Optional[str] = None
) -> ClinicalAnalysisResult:
    """
    Run complete AI medical pipeline on uploaded document
    
    Pipeline Steps:
    1. OCR - Extract text
    2. Sectionizer - Structure into clinical sections
    3. NER - Extract entities
    4. Entity Linking - Map to standard codes
    5. FHIR Mapping - Generate FHIR bundle
    6. Explanation - Generate patient-friendly summary
    7. Safety Check - Detect red flags
    
    Returns:
        ClinicalAnalysisResult with all extracted data and analysis
    """
    result = ClinicalAnalysisResult()
    result.document_type = document_type
    
    # Check if pipeline is available
    if not PIPELINE_AVAILABLE:
        result.error_message = "AI Medical Pipeline is not available. Please check system dependencies."
        result.add_processing_step("System Check", "failed", result.error_message)
        return result
    
    print(f"\n{'='*60}")
    print(f"🔬 AI-Assisted Clinical Record Analysis")
    print(f"{'='*60}")
    print(f"Document Type: {document_type}")
    print(f"File: {os.path.basename(file_path)}")
    
    try:
        # ===== STEP 1: OCR - Extract Text =====
        print("\n[1/7] OCR - Extracting text from document...")
        result.add_processing_step("OCR", "started")
        
        success, text, error = extract_text_from_file(file_path)
        if not success:
            result.error_message = error
            result.add_processing_step("OCR", "failed", error)
            return result
        
        result.extracted_text = text
        result.add_processing_step("OCR", "completed", f"Extracted {len(text)} characters")
        print(f"✓ Extracted {len(text)} characters")
        
        # ===== STEP 2: Sectionizer - Structure Text =====
        print("\n[2/7] Sectionizer - Structuring into clinical sections...")
        result.add_processing_step("Sectionizer", "started")
        
        # Create temp file for text
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp:
            tmp.write(text)
            text_file = tmp.name
        
        sections_dict = sectionize_text(text_file)
        result.sections = sections_dict
        result.add_processing_step("Sectionizer", "completed", f"Identified {len(sections_dict)} sections")
        print(f"✓ Identified {len(sections_dict)} sections")
        
        os.remove(text_file)
        
        # ===== STEP 3: NER - Extract Entities =====
        print("\n[3/7] NER - Extracting medical entities...")
        result.add_processing_step("NER", "started")
        
        entities_dict = extract_entities_from_sections(sections_dict)
        result.entities = entities_dict
        
        total_entities = sum(len(ents) for ents in entities_dict.values() if isinstance(ents, list))
        result.add_processing_step("NER", "completed", f"Extracted {total_entities} entities")
        print(f"✓ Extracted {total_entities} medical entities")
        
        # ===== STEP 4: Entity Linking - Map to Standard Codes =====
        print("\n[4/7] Entity Linking - Mapping to clinical codes...")
        result.add_processing_step("Entity Linking", "started")
        
        # Create temp file for entities
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
            json.dump(entities_dict, tmp, indent=2)
            entities_file = tmp.name
        
        linked_file = entities_file.replace('.json', '_linked.json')
        link_entities(entities_file, linked_file)
        
        with open(linked_file, 'r', encoding='utf-8') as f:
            linked_dict = json.load(f)
        result.linked_entities = linked_dict
        
        result.add_processing_step("Entity Linking", "completed", "Entities mapped to SNOMED/RxNorm/LOINC")
        print(f"✓ Entities mapped to standard codes")
        
        os.remove(entities_file)
        os.remove(linked_file)
        
        # ===== STEP 5: FHIR Mapping - Generate FHIR Bundle =====
        print("\n[5/7] FHIR Mapper - Generating FHIR R4 bundle...")
        result.add_processing_step("FHIR Mapping", "started")
        
        # Create temp files for FHIR conversion
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
            json.dump(linked_dict, tmp, indent=2)
            linked_input = tmp.name
        
        fhir_output = linked_input.replace('.json', '_fhir.json')
        convert_to_fhir_bundle(linked_input, fhir_output)
        
        with open(fhir_output, 'r', encoding='utf-8') as f:
            fhir_bundle = json.load(f)
        result.fhir_bundle = fhir_bundle
        
        # Extract patient name from FHIR if not provided
        if not patient_name:
            for entry in fhir_bundle.get("entry", []):
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Patient":
                    name_obj = resource.get("name", [{}])[0]
                    result.patient_name = name_obj.get("text", "Unknown Patient")
                    break
        else:
            result.patient_name = patient_name
        
        result.add_processing_step("FHIR Mapping", "completed", f"Generated {len(fhir_bundle.get('entry', []))} FHIR resources")
        print(f"✓ Generated {len(fhir_bundle.get('entry', []))} FHIR resources")
        
        os.remove(linked_input)
        os.remove(fhir_output)
        
        # ===== STEP 6: Explanation - Generate Patient-Friendly Summary =====
        print("\n[6/7] Explanation Generator - Creating patient summary...")
        result.add_processing_step("Explanation", "started")
        
        explanation_json = to_explanation_json(fhir_bundle)
        explanation_text = to_plain_text(explanation_json)
        
        result.explanation = explanation_json
        result.explanation_text = explanation_text
        result.add_processing_step("Explanation", "completed", "Patient-friendly summary generated")
        print(f"✓ Patient-friendly summary generated")
        
        # Extract structured entities from FHIR
        extracted_entities = extract_clinical_entities(fhir_bundle)
        result.conditions = extracted_entities["conditions"]
        result.medications = extracted_entities["medications"]
        result.observations = extracted_entities["observations"]
        result.procedures = extracted_entities["procedures"]
        
        # ===== STEP 7: Safety Checker - Red Flag Detection =====
        print("\n[7/7] Safety Checker - Detecting red flags...")
        result.add_processing_step("Safety Check", "started")
        
        if SAFETY_AVAILABLE:
            # Create temp file for safety check
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
                json.dump(linked_dict, tmp, indent=2)
                safety_input = tmp.name
            
            safety_output = safety_input.replace('.json', '_safety.json')
            run_safety_check(safety_input, safety_output, use_llm=False)
            
            with open(safety_output, 'r', encoding='utf-8') as f:
                safety_report = json.load(f)
            result.safety_report = safety_report
            
            # Determine risk level and extract red flags
            risk_level, red_flags = determine_risk_level(safety_report)
            result.risk_level = risk_level
            result.red_flags = red_flags
            
            result.add_processing_step("Safety Check", "completed", f"Risk Level: {risk_level.upper()}")
            print(f"✓ Safety check completed - Risk Level: {risk_level.upper()}")
            
            os.remove(safety_input)
            os.remove(safety_output)
        else:
            result.add_processing_step("Safety Check", "skipped", "Safety checker unavailable")
            result.risk_level = "unknown"
            print(f"⚠ Safety checker unavailable")
        
        # ===== SUCCESS =====
        result.success = True
        print(f"\n{'='*60}")
        print(f"✓ Analysis Complete!")
        print(f"  Patient: {result.patient_name}")
        print(f"  Conditions: {len(result.conditions)}")
        print(f"  Medications: {len(result.medications)}")
        print(f"  Observations: {len(result.observations)}")
        print(f"  Risk Level: {result.risk_level.upper()}")
        print(f"  Red Flags: {len(result.red_flags)}")
        print(f"{'='*60}\n")
        
        return result
    
    except Exception as e:
        import traceback
        result.error_message = f"Processing failed: {str(e)}"
        result.add_processing_step("Error", "failed", traceback.format_exc())
        print(f"\n✗ Error: {result.error_message}")
        return result


# =============================
# Storage (In-Memory + Database)
# =============================
analysis_results_storage: Dict[str, ClinicalAnalysisResult] = {}


def save_analysis_result(result: ClinicalAnalysisResult, patient_id: str = None) -> str:
    """
    Save analysis result to in-memory storage and optionally to database
    Returns analysis_id
    """
    # In-memory storage
    analysis_results_storage[result.analysis_id] = result
    
    # Try to save to database (if database is initialized)
    if patient_id:
        try:
            from database_config import db, MedicalRecord, FHIRBundle, Explanation, ProcessingJob
            from hashlib import sha256
            import json as jsonlib
            
            # Create medical record entry
            file_hash = sha256(result.analysis_id.encode()).hexdigest()[:32]
            
            medical_record = MedicalRecord(
                file_hash=file_hash,
                patient_id=patient_id,
                document_type=result.document_type,
                status='Processed' if result.success else 'Failed',
                uploaded_at=result.timestamp
            )
            db.session.add(medical_record)
            db.session.flush()  # Get the ID
            
            # Save FHIR bundle if available
            if result.fhir_bundle:
                fhir_bundle = FHIRBundle(
                    medical_record_id=medical_record.id,
                    json_data=jsonlib.dumps(result.fhir_bundle),
                    valid=result.success,
                    generated_at=result.timestamp
                )
                db.session.add(fhir_bundle)
            
            # Save explanation if available
            if result.explanation_text:
                explanation = Explanation(
                    medical_record_id=medical_record.id,
                    summary_md=result.explanation_text,
                    risks_md='\n'.join(result.red_flags) if result.red_flags else None,
                    low_confidence=result.risk_level == 'unknown',
                    generated_at=result.timestamp
                )
                db.session.add(explanation)
            
            # Save processing jobs
            for step in result.processing_steps:
                job = ProcessingJob(
                    medical_record_id=medical_record.id,
                    job_kind=step['step'].upper().replace(' ', '_'),
                    status='Succeeded' if step['status'] == 'completed' else 'Failed' if step['status'] == 'failed' else 'Queued',
                    pipeline_version='1.0'
                )
                db.session.add(job)
            
            db.session.commit()
            print(f"✓ Saved analysis to database (record_id: {medical_record.id})")
            
        except Exception as e:
            print(f"⚠ Could not save to database: {e}")
            # Continue anyway - in-memory storage works
    
    return result.analysis_id


def get_analysis_result(analysis_id: str) -> Optional[ClinicalAnalysisResult]:
    """Retrieve analysis result by ID"""
    return analysis_results_storage.get(analysis_id)


def get_user_analysis_history(user_id: str, limit: int = 20) -> List[ClinicalAnalysisResult]:
    """Get analysis history for a user"""
    # Return from in-memory storage
    # In production, this would query the database
    return list(analysis_results_storage.values())[:limit]

