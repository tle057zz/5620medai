"""
AI-Assisted Clinical Record Analysis Processor (Saahir Khan - Use Case 2)

Complete AI medical pipeline aligned with use_case2.html specification for document ingestion,
extraction, explanation, and risk flagging. Uses UC2_models pipeline modules.

Pipeline Steps (per use_case2.html):
1. OCR - Extract clean text from PDFs/images
2. Sectionizer - Split text into meaningful medical categories
3. NER - Identify clinical entities (problems, medications, allergies, lab tests)
4. Entity Linking - Map to standardized ontologies (ICD-10-AM, SNOMED, RxNorm)
5. FHIR Mapping - Generate FHIR R4 compliant resources
6. Explanation - AI model generates patient-friendly summary with glossary and health risks
7. Safety Checker - Detect red flags (contraindications, emergency symptoms)

Outputs: summary_md, risks_md, safety_flags_json, fhir_data
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
    # Import from UC2_models pipeline (aligned with use_case2.html specification)
    # Add the parent directory to path so we can import UC2_models as a package
    uc2_models_path = os.path.join(os.path.dirname(__file__), 'UC2_models')
    uc2_parent_path = os.path.dirname(__file__)
    if uc2_parent_path not in sys.path:
        sys.path.insert(0, uc2_parent_path)
    
    from UC2_models.ocr.extract_text import extract_text_from_pdf
    from UC2_models.sectionizer.sectionize_text import sectionize_text
    from UC2_models.ner.extract_entities import extract_entities_from_sections
    from UC2_models.linker.entity_linking import link_entities
    from UC2_models.fhir_mapper.fhir_mapping import convert_to_fhir_bundle
    from UC2_models.explain.generate_explanation import to_explanation_json, to_plain_text
    PIPELINE_AVAILABLE = True
    print("✓ UC2 AI Medical Pipeline loaded successfully")
except Exception as e:
    print(f"⚠ UC2 AI Medical Pipeline unavailable: {e}")
    import traceback
    traceback.print_exc()
    PIPELINE_AVAILABLE = False

try:
    from UC2_models.safety.safety_check import run_safety_check
    SAFETY_AVAILABLE = True
    print("✓ UC2 Safety Checker loaded successfully")
except Exception as e:
    print(f"⚠ UC2 Safety Checker unavailable: {e}")
    import traceback
    traceback.print_exc()
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
        
        # Mistral LLM Analysis (additional AI analysis using mistral:7b-instruct)
        self.mistral_analysis = None
        
        # File path information
        self.file_path = None  # Relative path (e.g., "user_id_analysis_id/filename.pdf")
        self.original_filename = None  # Original filename when uploaded
    
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
            "mistral_analysis": self.mistral_analysis,
            "document_type": self.document_type,
            "processing_steps": self.processing_steps,
            "fhir_bundle": self.fhir_bundle,
            "safety_report": self.safety_report,
            "file_path": self.file_path,
            "original_filename": self.original_filename
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


def generate_mistral_clinical_analysis(extracted_text: str = None, fhir_bundle: Dict = None,
                                       conditions: List[str] = None, medications: List[str] = None,
                                       risk_level: str = "unknown", red_flags: List[str] = None) -> str:
    """
    Generate clinical document analysis using mistral:7b-instruct LLM
    
    Args:
        extracted_text: Raw extracted text from the document
        fhir_bundle: FHIR R4 bundle with structured data
        conditions: List of identified medical conditions
        medications: List of identified medications
        risk_level: Overall risk level (low, medium, high, critical)
        red_flags: List of red flag warnings
        
    Returns:
        Analysis text from mistral:7b-instruct
    """
    try:
        from ai_explainer import _run_ollama
        
        # Build comprehensive prompt for clinical analysis
        conditions_str = ", ".join(conditions) if conditions else "None identified"
        medications_str = ", ".join(medications) if medications else "None identified"
        red_flags_str = "\n- ".join(red_flags) if red_flags else "None detected"
        
        # Prepare text summary (limit to avoid token limits)
        text_preview = (extracted_text[:2000] + "...") if extracted_text and len(extracted_text) > 2000 else (extracted_text or "No text extracted")
        
        # Count FHIR resources
        fhir_count = len(fhir_bundle.get('entry', [])) if fhir_bundle else 0
        
        # Build risk assessment section (avoid backslash in f-string expression)
        if red_flags:
            risk_section = "- Red flags detected:\n  " + red_flags_str
        else:
            risk_section = "- No red flags detected"
        
        prompt = f"""You are a medical AI assistant analyzing a clinical document. Provide a comprehensive analysis including:

1. **Document Overview**: Summarize the key clinical information from this medical document.

2. **Clinical Findings**: Based on the extracted data, identify and explain:
   - Medical conditions: {conditions_str}
   - Medications: {medications_str}
   - Clinical significance and relationships between findings

3. **Risk Assessment**: Evaluate the risk level ({risk_level.upper()}) and explain what factors contribute to this assessment.
   {risk_section}

4. **Clinical Insights**: Provide insights about:
   - Potential drug interactions or contraindications
   - Important clinical patterns or trends
   - Recommendations for follow-up care
   - Patient safety considerations

5. **Summary**: Provide a concise executive summary for healthcare providers.

**Document Context:**
- Extracted text (preview): {text_preview}
- Structured FHIR resources: {fhir_count} resources extracted
- Document type: Medical record/clinical document

**Instructions:**
- Use professional medical terminology appropriately
- Be clear and concise
- Highlight critical information
- Focus on actionable insights
- Do not provide specific treatment recommendations (leave that to clinicians)

Provide your analysis in clear, structured format with sections."""

        # Call mistral:7b-instruct
        analysis = _run_ollama("mistral:7b-instruct", prompt, timeout=60)
        
        if not analysis or len(analysis.strip()) < 50:
            return "Mistral analysis unavailable. The LLM service may be unavailable or the response was too short."
        
        return analysis.strip()
        
    except Exception as e:
        import traceback
        error_msg = f"Mistral analysis failed: {str(e)}"
        print(f"⚠ {error_msg}")
        traceback.print_exc()
        return None


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
    notes: Optional[str] = None,
    progress_cb=None
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
    8. Mistral LLM Analysis - AI-powered clinical analysis
    
    Args:
        progress_cb: Optional callback function(percentage, message) to report progress
    
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
        print(f"\n{'='*70}")
        print("[STEP 1/8] 🔍 OCR - Extracting text from document...")
        print(f"{'='*70}")
        if progress_cb:
            progress_cb(5, "Step 1/8: Extracting text from document...")
        result.add_processing_step("OCR", "started")
        step_start = datetime.now()
        
        success, text, error = extract_text_from_file(file_path)
        if not success:
            result.error_message = error
            result.add_processing_step("OCR", "failed", error)
            print(f"✗ OCR FAILED: {error}")
            return result
        
        step_duration = (datetime.now() - step_start).total_seconds()
        result.extracted_text = text
        result.add_processing_step("OCR", "completed", f"Extracted {len(text)} characters")
        if progress_cb:
            progress_cb(15, f"Step 1/8: OCR completed - Extracted {len(text):,} characters")
        print(f"✓ OCR Completed in {step_duration:.2f}s")
        print(f"  → Extracted {len(text):,} characters")
        print(f"  → Text preview: {text[:200].replace(chr(10), ' ')}...")
        
        # ===== STEP 2: Sectionizer - Structure Text =====
        print(f"\n{'='*70}")
        print("[STEP 2/8] 📑 Sectionizer - Structuring into clinical sections...")
        print(f"{'='*70}")
        if progress_cb:
            progress_cb(20, "Step 2/8: Structuring document into clinical sections...")
        result.add_processing_step("Sectionizer", "started")
        step_start = datetime.now()
        
        # Create temp file for text
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp:
            tmp.write(text)
            text_file = tmp.name
        
        sections_dict = sectionize_text(text_file)
        step_duration = (datetime.now() - step_start).total_seconds()
        result.sections = sections_dict
        result.add_processing_step("Sectionizer", "completed", f"Identified {len(sections_dict)} sections")
        if progress_cb:
            progress_cb(30, f"Step 2/8: Sectionizer completed - Identified {len(sections_dict)} sections")
        print(f"✓ Sectionizer Completed in {step_duration:.2f}s")
        print(f"  → Identified {len(sections_dict)} sections:")
        for section_name in list(sections_dict.keys())[:5]:
            content_preview = sections_dict[section_name][:100].replace('\n', ' ')
            print(f"    • {section_name}: {content_preview}...")
        if len(sections_dict) > 5:
            print(f"    ... and {len(sections_dict) - 5} more sections")
        
        os.remove(text_file)
        
        # ===== STEP 3: NER - Extract Entities =====
        print(f"\n{'='*70}")
        print("[STEP 3/8] 🏷️  NER - Extracting medical entities (problems, medications, allergies, lab tests)...")
        print(f"{'='*70}")
        if progress_cb:
            progress_cb(38, "Step 3/8: Extracting medical entities...")
        result.add_processing_step("NER", "started")
        step_start = datetime.now()
        
        entities_dict = extract_entities_from_sections(sections_dict)
        step_duration = (datetime.now() - step_start).total_seconds()
        result.entities = entities_dict
        
        total_entities = sum(len(ents) for ents in entities_dict.values() if isinstance(ents, list))
        
        # Count by type
        entity_types = {}
        for section_ents in entities_dict.values():
            if isinstance(section_ents, list):
                for ent in section_ents:
                    label = ent.get('label', 'UNKNOWN')
                    entity_types[label] = entity_types.get(label, 0) + 1
        
        result.add_processing_step("NER", "completed", f"Extracted {total_entities} entities")
        if progress_cb:
            progress_cb(48, f"Step 3/8: NER completed - Extracted {total_entities} entities")
        print(f"✓ NER Completed in {step_duration:.2f}s")
        print(f"  → Total entities extracted: {total_entities}")
        print(f"  → Entity breakdown:")
        for label, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True):
            print(f"    • {label}: {count}")
        
        # ===== STEP 4: Entity Linking - Map to Standard Codes =====
        print(f"\n{'='*70}")
        print("[STEP 4/8] 🔗 Entity Linking - Mapping to ICD-10-AM, SNOMED, RxNorm...")
        print(f"{'='*70}")
        if progress_cb:
            progress_cb(55, "Step 4/8: Mapping entities to medical codes...")
        result.add_processing_step("Entity Linking", "started")
        step_start = datetime.now()
        
        # Create temp file for entities
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
            json.dump(entities_dict, tmp, indent=2)
            entities_file = tmp.name
        
        linked_file = entities_file.replace('.json', '_linked.json')
        link_entities(entities_file, linked_file)
        
        with open(linked_file, 'r', encoding='utf-8') as f:
            linked_dict = json.load(f)
        step_duration = (datetime.now() - step_start).total_seconds()
        result.linked_entities = linked_dict
        
        # Count linked entities with codes
        linked_count = 0
        ontology_counts = {'SNOMED': 0, 'ICD-10-AM': 0, 'RxNorm': 0, 'LOINC': 0}
        for section_data in linked_dict.values():
            if isinstance(section_data, list):
                for ent in section_data:
                    if isinstance(ent, dict) and ent.get('codes'):
                        linked_count += 1
                        for code_obj in ent.get('codes', []):
                            system = code_obj.get('system', '')
                            if 'SNOMED' in system.upper():
                                ontology_counts['SNOMED'] += 1
                            elif 'ICD' in system.upper():
                                ontology_counts['ICD-10-AM'] += 1
                            elif 'RXNORM' in system.upper():
                                ontology_counts['RxNorm'] += 1
                            elif 'LOINC' in system.upper():
                                ontology_counts['LOINC'] += 1
        
        result.add_processing_step("Entity Linking", "completed", "Entities mapped to SNOMED/RxNorm/LOINC")
        if progress_cb:
            progress_cb(62, f"Step 4/8: Entity linking completed - {linked_count} entities mapped")
        print(f"✓ Entity Linking Completed in {step_duration:.2f}s")
        print(f"  → Entities linked: {linked_count}/{total_entities}")
        print(f"  → Ontology mappings:")
        for ont, count in ontology_counts.items():
            if count > 0:
                print(f"    • {ont}: {count}")
        
        os.remove(entities_file)
        os.remove(linked_file)
        
        # ===== STEP 5: FHIR Mapping - Generate FHIR Bundle =====
        print(f"\n{'='*70}")
        print("[STEP 5/8] 📋 FHIR Mapper - Generating FHIR R4 compliant bundle...")
        print(f"{'='*70}")
        if progress_cb:
            progress_cb(68, "Step 5/8: Generating FHIR R4 compliant bundle...")
        result.add_processing_step("FHIR Mapping", "started")
        step_start = datetime.now()
        
        # Create temp files for FHIR conversion
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
            json.dump(linked_dict, tmp, indent=2)
            linked_input = tmp.name
        
        fhir_output = linked_input.replace('.json', '_fhir.json')
        convert_to_fhir_bundle(linked_input, fhir_output)
        
        with open(fhir_output, 'r', encoding='utf-8') as f:
            fhir_bundle = json.load(f)
        step_duration = (datetime.now() - step_start).total_seconds()
        result.fhir_bundle = fhir_bundle
        
        # Count resource types
        resource_types = {}
        for entry in fhir_bundle.get('entry', []):
            res_type = entry.get('resource', {}).get('resourceType', 'Unknown')
            resource_types[res_type] = resource_types.get(res_type, 0) + 1
        
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
        if progress_cb:
            progress_cb(75, f"Step 5/8: FHIR mapping completed - {len(fhir_bundle.get('entry', []))} resources generated")
        print(f"✓ FHIR Mapping Completed in {step_duration:.2f}s")
        print(f"  → Total FHIR resources: {len(fhir_bundle.get('entry', []))}")
        print(f"  → Resource types:")
        for res_type, count in sorted(resource_types.items(), key=lambda x: x[1], reverse=True):
            print(f"    • {res_type}: {count}")
        
        os.remove(linked_input)
        os.remove(fhir_output)
        
        # ===== STEP 6: Explanation - Generate Patient-Friendly Summary =====
        print(f"\n{'='*70}")
        print("[STEP 6/8] 📝 Explanation Generator - Creating patient-friendly summary with glossary and risks...")
        print(f"{'='*70}")
        if progress_cb:
            progress_cb(80, "Step 6/8: Generating patient-friendly summary...")
        result.add_processing_step("Explanation", "started")
        step_start = datetime.now()
        
        explanation_json = to_explanation_json(fhir_bundle)
        explanation_text = to_plain_text(explanation_json)
        step_duration = (datetime.now() - step_start).total_seconds()
        
        result.explanation = explanation_json
        result.explanation_text = explanation_text
        result.add_processing_step("Explanation", "completed", "Patient-friendly summary generated")
        if progress_cb:
            progress_cb(85, "Step 6/8: Explanation generation completed")
        print(f"✓ Explanation Generation Completed in {step_duration:.2f}s")
        print(f"  → Summary length: {len(explanation_text):,} characters")
        print(f"  → Summary preview: {explanation_text[:150].replace(chr(10), ' ')}...")
        
        # Extract structured entities from FHIR
        extracted_entities = extract_clinical_entities(fhir_bundle)
        result.conditions = extracted_entities["conditions"]
        result.medications = extracted_entities["medications"]
        result.observations = extracted_entities["observations"]
        result.procedures = extracted_entities["procedures"]
        
        # ===== STEP 7: Safety Checker - Red Flag Detection =====
        print(f"\n{'='*70}")
        print("[STEP 7/8] ⚠️  Safety Checker - Detecting red flags and contraindications...")
        print(f"{'='*70}")
        if progress_cb:
            progress_cb(88, "Step 7/8: Running safety checks and detecting red flags...")
        result.add_processing_step("Safety Check", "started")
        step_start = datetime.now()
        
        if SAFETY_AVAILABLE:
            # UC2 safety_check reads from fixed paths - write FHIR bundle to expected location
            # Save FHIR bundle to UC2_models/fhir_mapper/fhir_bundle.json for safety check
            uc2_fhir_dir = os.path.join(os.path.dirname(__file__), 'UC2_models', 'fhir_mapper')
            os.makedirs(uc2_fhir_dir, exist_ok=True)
            uc2_fhir_path = os.path.join(uc2_fhir_dir, 'fhir_bundle.json')
            
            with open(uc2_fhir_path, 'w', encoding='utf-8') as f:
                json.dump(fhir_bundle, f, indent=2, ensure_ascii=False)
            
            # Run safety check (reads from fixed path, writes to fixed output paths)
            safety_report_dict, safety_summary_txt, safety_fluent = run_safety_check()
            
            # Convert UC2 safety report format to expected format
            safety_report = {
                "high_risk": safety_report_dict.get("high_risk", []),
                "moderate_risk": safety_report_dict.get("moderate_risk", []),
                "abnormal_vitals": safety_report_dict.get("abnormal_vitals", []),
                "summary": safety_report_dict.get("summary", "No red flags detected"),
                "drug_interactions": [],  # Extract from high_risk if needed
                "contraindications": [r.get("message", "") for r in safety_report_dict.get("high_risk", []) if "contraindication" in r.get("message", "").lower()],
                "vital_alerts": [{"message": v, "severity": "high"} for v in safety_report_dict.get("abnormal_vitals", [])],
                "comorbidity_risk": {"high_risk_pairs": [] if not safety_report_dict.get("high_risk") else safety_report_dict.get("high_risk")}
            }
            result.safety_report = safety_report
            
            # Determine risk level and extract red flags
            step_duration = (datetime.now() - step_start).total_seconds()
            risk_level, red_flags = determine_risk_level(safety_report)
            result.risk_level = risk_level
            result.red_flags = red_flags
            
            result.add_processing_step("Safety Check", "completed", f"Risk Level: {risk_level.upper()}")
            if progress_cb:
                progress_cb(92, f"Step 7/8: Safety check completed - Risk level: {risk_level.upper()}, {len(red_flags)} red flags")
            print(f"✓ Safety Check Completed in {step_duration:.2f}s")
            print(f"  → Risk Level: {risk_level.upper()}")
            print(f"  → Red Flags Detected: {len(red_flags)}")
            if red_flags:
                print(f"  → Flags:")
                for i, flag in enumerate(red_flags[:3], 1):
                    print(f"    {i}. {flag[:70]}{'...' if len(flag) > 70 else ''}")
                if len(red_flags) > 3:
                    print(f"    ... and {len(red_flags) - 3} more")
            
            # Clean up temp FHIR file
            try:
                os.remove(uc2_fhir_path)
            except:
                pass
        else:
            result.add_processing_step("Safety Check", "skipped", "Safety checker unavailable")
            result.risk_level = "unknown"
            if progress_cb:
                progress_cb(92, "Step 7/8: Safety checker unavailable")
            print(f"⚠ Safety checker unavailable")
        
        # ===== STEP 8: Mistral LLM Analysis =====
        print(f"\n{'='*70}")
        print("[STEP 8/8] 🤖 Mistral LLM Analysis - AI-powered clinical document analysis...")
        print(f"{'='*70}")
        if progress_cb:
            progress_cb(95, "Step 8/8: Running Mistral LLM analysis...")
        result.add_processing_step("Mistral LLM Analysis", "started")
        step_start = datetime.now()
        
        try:
            mistral_analysis = generate_mistral_clinical_analysis(
                extracted_text=result.extracted_text,
                fhir_bundle=result.fhir_bundle,
                conditions=result.conditions,
                medications=result.medications,
                risk_level=result.risk_level,
                red_flags=result.red_flags
            )
            result.mistral_analysis = mistral_analysis
            step_duration = (datetime.now() - step_start).total_seconds()
            result.add_processing_step("Mistral LLM Analysis", "completed", f"Generated {len(mistral_analysis):,} characters")
            if progress_cb:
                progress_cb(98, f"Step 8/8: Mistral LLM analysis completed - {len(mistral_analysis):,} characters generated")
            print(f"✓ Mistral LLM Analysis Completed in {step_duration:.2f}s")
            print(f"  → Analysis length: {len(mistral_analysis):,} characters")
            print(f"  → Preview: {mistral_analysis[:200].replace(chr(10), ' ')}...")
        except Exception as e:
            result.mistral_analysis = None
            step_duration = (datetime.now() - step_start).total_seconds()
            result.add_processing_step("Mistral LLM Analysis", "failed", f"Error: {str(e)}")
            if progress_cb:
                progress_cb(98, "Step 8/8: Mistral LLM analysis unavailable (continuing without it)")
            print(f"⚠ Mistral LLM Analysis failed: {e}")
            print(f"  → Continuing without Mistral analysis")
        
        # ===== SUCCESS =====
        result.success = True
        if progress_cb:
            progress_cb(100, "Analysis complete! Preparing results...")
        total_time = (datetime.now() - result.timestamp).total_seconds()
        
        print(f"\n{'='*70}")
        print(f"✅ PIPELINE PROCESSING COMPLETE!")
        print(f"{'='*70}")
        print(f"Analysis ID: {result.analysis_id}")
        print(f"Total Processing Time: {total_time:.2f} seconds")
        print(f"Patient: {result.patient_name or 'Unknown'}")
        print(f"Conditions: {len(result.conditions)}")
        print(f"Medications: {len(result.medications)}")
        print(f"Observations: {len(result.observations)}")
        print(f"Procedures: {len(result.procedures)}")
        print(f"Risk Level: {result.risk_level.upper()}")
        print(f"Red Flags: {len(result.red_flags)}")
        print(f"FHIR Resources: {len(result.fhir_bundle.get('entry', [])) if result.fhir_bundle else 0}")
        print(f"Mistral Analysis: {'✓ Available' if result.mistral_analysis else '✗ Not available'}")
        if result.mistral_analysis:
            print(f"  → Length: {len(result.mistral_analysis):,} characters")
        print(f"Processing Steps Completed: {len([s for s in result.processing_steps if s.get('status') == 'completed'])}/8")
        print(f"{'='*70}\n")
        
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


def save_analysis_result(result: ClinicalAnalysisResult, patient_id: str = None, 
                         notes: str = None, file_path: str = None, original_filename: str = None) -> str:
    """
    Save analysis result to in-memory storage and to AWS RDS database
    Returns analysis_id
    """
    print(f"[Save Debug] save_analysis_result called: analysis_id={result.analysis_id}, patient_id={patient_id}")
    print(f"[Save Debug] file_path={file_path}, original_filename={original_filename}")
    
    # Store file path and original filename in result object
    if file_path:
        result.file_path = file_path
    if original_filename:
        result.original_filename = original_filename
    # In-memory storage
    analysis_results_storage[result.analysis_id] = result
    print(f"[Save Debug] Saved to in-memory storage")
    
    # Try to save to AWS RDS database
    if patient_id:
        print(f"[Save Debug] Attempting to save to RDS for patient_id={patient_id}")
        try:
            from hashlib import sha256
            import json as jsonlib
            from rds_repository import save_medical_record_to_rds
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            # Get patient_user_id (convert string to int if needed)
            try:
                patient_user_id = int(str(patient_id))
            except (ValueError, TypeError):
                print(f"⚠ Could not convert patient_id to int: {patient_id}")
                return result.analysis_id
            
            # Store analysis_id directly in file_hash for easy lookup
            # This allows us to retrieve analyses by their analysis_id
            file_hash = result.analysis_id  # Store analysis_id directly instead of hashing
            
            # Save medical record to RDS (this was already done in clinical_analysis route, but ensure it exists)
            print(f"[Save Debug] Calling save_medical_record_to_rds with file_hash={file_hash}")
            print(f"[Save Debug] file_path parameter: {file_path}")
            print(f"[Save Debug] original_filename parameter: {original_filename}")
            record_id = save_medical_record_to_rds(
                patient_user_id=patient_user_id,
                file_hash=file_hash,
                document_type=result.document_type,
                status='Processed' if result.success else 'Failed',
                uploaded_at=result.timestamp,
                file_path=file_path,
                original_filename=original_filename
            )
            print(f"[Save Debug] save_medical_record_to_rds returned record_id={record_id}")
            
            if record_id:
                # Connect to RDS to save FHIR, explanation, and safety flags
                from rds_repository import _conn
                
                with _conn() as conn:
                    conn.autocommit = False
                    cur = conn.cursor()
                    
                    try:
                        # Save FHIR bundle
                        if result.fhir_bundle:
                            cur.execute("""
                                INSERT INTO fhir_bundles(medical_record_id, json, valid, generated_at)
                                VALUES (%s, %s::text, %s, %s)
                                ON CONFLICT DO NOTHING
                            """, (record_id, jsonlib.dumps(result.fhir_bundle), result.success, result.timestamp))
                        
                        # Save explanation and get explanation_id
                        explanation_id = None
                        if result.explanation_text or result.mistral_analysis:
                            cur.execute("""
                                INSERT INTO explanations(medical_record_id, summary_md, risks_md, mistral_analysis, low_confidence, generated_at)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                RETURNING id
                            """, (
                                record_id,
                                result.explanation_text,
                                '\n'.join(result.red_flags) if result.red_flags else None,
                                result.mistral_analysis,  # Save mistral analysis
                                result.risk_level == 'unknown',
                                result.timestamp
                            ))
                            exp_row = cur.fetchone()
                            if exp_row:
                                explanation_id = exp_row[0]
                        
                        # Save safety flags
                        if result.red_flags and explanation_id:
                            for flag_text in result.red_flags:
                                # Parse flag to determine type and severity
                                flag_type = 'Emergency'  # Default
                                severity = 'High'  # Default
                                
                                flag_lower = flag_text.lower()
                                if 'contraindication' in flag_lower:
                                    flag_type = 'Contraindication'
                                elif 'allergy' in flag_lower:
                                    flag_type = 'Allergy'
                                elif 'interaction' in flag_lower:
                                    flag_type = 'Interaction'
                                
                                if 'critical' in flag_lower:
                                    severity = 'High'
                                elif 'warning' in flag_lower:
                                    severity = 'Medium'
                                else:
                                    severity = 'Low'
                                
                                cur.execute("""
                                    INSERT INTO safety_flags(medical_record_id, explanation_id, type, severity, details, created_at)
                                    VALUES (%s, %s, %s::safety_flag_type, %s::safety_severity, %s, %s)
                                """, (record_id, explanation_id, flag_type, severity, flag_text, result.timestamp))
                        
                        # Save processing jobs
                        # Map pipeline steps to valid enum values: OCR, IE, EXPLAIN, SAFETY
                        for step in result.processing_steps:
                            step_name = step['step']
                            # Map to valid job_kind enum values
                            if step_name == 'OCR':
                                job_kind = 'OCR'
                            elif step_name in ['Sectionizer', 'NER', 'Entity Linking', 'FHIR Mapping']:
                                job_kind = 'IE'  # Information Extraction
                            elif step_name in ['Explanation', 'Mistral LLM Analysis']:
                                job_kind = 'EXPLAIN'
                            elif step_name == 'Safety Check':
                                job_kind = 'SAFETY'
                            else:
                                # Default to IE for unknown steps
                                job_kind = 'IE'
                            job_status_map = {
                                'completed': 'Succeeded',
                                'failed': 'Failed',
                                'started': 'Queued',
                                'skipped': 'Queued'
                            }
                            job_status = job_status_map.get(step['status'], 'Queued')
                            
                            cur.execute("""
                                INSERT INTO processing_jobs(medical_record_id, kind, status, started_at, finished_at)
                                VALUES (%s, %s::job_kind, %s::job_status, %s, %s)
                            """, (
                                record_id,
                                job_kind,
                                job_status,
                                result.timestamp,
                                result.timestamp if step['status'] in ('completed', 'failed') else None
                            ))
                        
                        conn.commit()
                        print(f"✓ Saved complete analysis to AWS RDS (record_id: {record_id}, analysis_id: {result.analysis_id})")
                        print(f"[Save Debug] Successfully committed to RDS")
                        
                    except Exception as e:
                        conn.rollback()
                        print(f"⚠ Error saving analysis details to RDS: {e}")
                        import traceback
                        traceback.print_exc()
            else:
                print(f"[Save Debug] No record_id returned from save_medical_record_to_rds - cannot save analysis details")
            
        except Exception as e:
            print(f"⚠ Could not save analysis to AWS RDS: {e}")
            import traceback
            traceback.print_exc()
            # Continue anyway - in-memory storage works
    else:
        print(f"[Save Debug] No patient_id provided - skipping RDS save")
    
    print(f"[Save Debug] Returning analysis_id: {result.analysis_id}")
    return result.analysis_id


def get_analysis_result(analysis_id: str, patient_user_id: int = None) -> Optional[ClinicalAnalysisResult]:
    """Retrieve analysis result by ID - tries RDS first, then in-memory storage.
    If patient_user_id is provided, ensures the analysis belongs to that user.
    """
    print(f"[Debug] get_analysis_result called: analysis_id={analysis_id}, patient_user_id={patient_user_id}")
    
    # Try RDS first
    try:
        if os.environ.get('USE_RDS_LOGIN', 'true').lower() in {'1','true','yes'}:
            from rds_repository import get_clinical_analysis_result_from_rds
            rds_result = get_clinical_analysis_result_from_rds(analysis_id=analysis_id, patient_user_id=patient_user_id)
            
            if rds_result:
                print(f"[Debug] Found result in RDS: analysis_id={rds_result.get('analysis_id')}")
                # Convert RDS dict to ClinicalAnalysisResult object
                result = ClinicalAnalysisResult()
                result.analysis_id = rds_result['analysis_id']
                result.timestamp = rds_result['timestamp']
                result.success = rds_result['success']
                result.error_message = rds_result.get('error_message')
                result.patient_name = rds_result.get('patient_name')
                result.document_type = rds_result.get('document_type')
                result.conditions = rds_result.get('conditions', [])
                result.medications = rds_result.get('medications', [])
                result.observations = rds_result.get('observations', [])
                result.procedures = rds_result.get('procedures', [])
                result.red_flags = rds_result.get('red_flags', [])
                result.risk_level = rds_result.get('risk_level', 'unknown')
                result.fhir_bundle = rds_result.get('fhir_bundle')
                result.explanation_text = rds_result.get('explanation_text')
                result.mistral_analysis = rds_result.get('mistral_analysis')
                result.safety_report = {'high_risk': [], 'moderate_risk': [], 'summary': 'No red flags detected'}
                result.file_path = rds_result.get('file_path')
                result.original_filename = rds_result.get('original_filename')
                
                # If file_path is missing but analysis exists, try to find the file in uploads folder
                if not result.file_path and analysis_id.startswith('CA-') and patient_user_id:
                    try:
                        # Files are stored in uploads/user_id_analysis_id/filename.pdf
                        # clinical_analysis_processor.py is in web_app/, so uploads is also in web_app/
                        current_file_dir = os.path.dirname(os.path.abspath(__file__))
                        upload_folder = os.path.join(current_file_dir, 'uploads')
                        
                        pattern_folder = f"{patient_user_id}_{analysis_id}"
                        pattern_path = os.path.join(upload_folder, pattern_folder)
                        if os.path.exists(pattern_path):
                            # Find any files in that folder
                            for f in os.listdir(pattern_path):
                                if f.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.txt', '.doc', '.docx')):
                                    result.file_path = os.path.join(pattern_folder, f)
                                    if not result.original_filename:
                                        result.original_filename = f
                                    print(f"[Get Result Debug] Found file on disk: {result.file_path}")
                                    break
                    except Exception as e:
                        print(f"[Get Result Debug] Error finding file for {analysis_id}: {e}")
                
                print(f"✓ Loaded analysis from AWS RDS: {analysis_id}")
                return result
            else:
                print(f"[Debug] No result found in RDS for analysis_id={analysis_id}")
    except Exception as e:
        print(f"⚠ Could not load from RDS: {e}")
        import traceback
        traceback.print_exc()
    
    # Fallback to in-memory storage
    print(f"[Debug] Trying in-memory storage for analysis_id={analysis_id}")
    in_memory_result = analysis_results_storage.get(analysis_id)
    if in_memory_result:
        print(f"[Debug] Found result in in-memory storage")
    else:
        print(f"[Debug] No result found in in-memory storage either")
    return in_memory_result


def get_user_analysis_history(user_id: str, limit: int = 20) -> List[ClinicalAnalysisResult]:
    """Get analysis history for a user - tries RDS first, then in-memory storage"""
    results = []
    
    # Try RDS first
    try:
        if os.environ.get('USE_RDS_LOGIN', 'true').lower() in {'1','true','yes'}:
            try:
                patient_user_id = int(str(user_id))
            except (ValueError, TypeError):
                patient_user_id = None
            
            if patient_user_id:
                try:
                    from rds_repository import get_clinical_analysis_history_for_user
                    rds_history = get_clinical_analysis_history_for_user(patient_user_id, limit=limit)
                    
                    # Convert RDS dicts to ClinicalAnalysisResult objects
                    for hist in rds_history:
                        result = ClinicalAnalysisResult()
                        result.analysis_id = hist['analysis_id']
                        result.timestamp = hist['timestamp']
                        result.success = hist['success']
                        result.patient_name = hist.get('patient_name')
                        result.document_type = hist.get('document_type')
                        result.conditions = hist.get('conditions', [])
                        result.medications = hist.get('medications', [])
                        result.risk_level = hist.get('risk_level', 'unknown')
                        result.red_flags = hist.get('red_flags', [])
                        result.file_path = hist.get('file_path')  # Store file path for future access
                        result.original_filename = hist.get('original_filename')  # Store original filename
                        
                        # If file_path is still missing, try to find file on disk (fallback from history query)
                        # This is already handled in get_clinical_analysis_history_for_user, but ensure it's set
                        if not result.file_path and result.analysis_id.startswith('CA-') and patient_user_id:
                            try:
                                current_file_dir = os.path.dirname(os.path.abspath(__file__))
                                upload_folder = os.path.join(current_file_dir, 'uploads')
                                pattern_folder = f"{patient_user_id}_{result.analysis_id}"
                                pattern_path = os.path.join(upload_folder, pattern_folder)
                                if os.path.exists(pattern_path):
                                    for f in os.listdir(pattern_path):
                                        if f.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.txt', '.doc', '.docx')):
                                            result.file_path = os.path.join(pattern_folder, f)
                                            if not result.original_filename:
                                                result.original_filename = f
                                            break
                            except Exception as e:
                                pass  # Silently fail if file discovery doesn't work
                        
                        results.append(result)
                    
                    if results:
                        print(f"✓ Loaded {len(results)} analyses from AWS RDS for user {patient_user_id}")
                        return results
                except Exception as e:
                    print(f"⚠ Could not load history from RDS: {e}")
    except Exception as e:
        print(f"⚠ RDS history fetch failed: {e}")
    
    # Fallback to in-memory storage
    memory_results = list(analysis_results_storage.values())[:limit]
    if memory_results:
        print(f"⚠ Loaded {len(memory_results)} analyses from in-memory storage (RDS unavailable)")
    return memory_results

