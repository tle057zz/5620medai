# 🧠 AI-Driven Medical Document Intelligence Pipeline  
### FHIR-Compliant Clinical AI System

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FHIR](https://img.shields.io/badge/FHIR-R4-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 🩺 Overview

The **AI-Driven Medical Document Intelligence Pipeline** automatically processes unstructured clinical PDFs into structured, FHIR-compliant medical data.  
It performs OCR, section segmentation, entity extraction, ontology linking, FHIR mapping, natural-language explanations, and red-flag safety checks — all locally, with deterministic outputs.

Built entirely in **Python**, this pipeline supports real-world clinical document analysis and interoperability without cloud dependencies.

---

## 📂 Folder Structure

```
ai_medical/
│
├── ocr/                → extract_text.py        # Day 1: OCR text extraction
├── sectionizer/        → sectionize_text.py     # Day 2: Logical text segmentation
├── ner/                → extract_entities.py    # Day 3: Clinical NER (SpaCy + BC5CDR)
├── linker/             → entity_linking.py      # Day 4: Ontology linking (SapBERT)
├── fhir_mapper/        → fhir_mapping.py        # Day 5: FHIR R4 Bundle generator
├── explain/            → generate_explanation.py# Day 6: Plain & fluent explanations
├── safety/             → safety_check.py        # Day 7: Safety & red-flag analyzer
└── requirements.txt
```

Each module runs independently or as part of the full end-to-end pipeline.

---

## ⚙️ Installation & Setup

### Prerequisites
- **Python:** 3.10+
- **System tools:** `tesseract-ocr`, `poppler` (for PDF to image conversion)

### 1️⃣ Create environment
```bash
conda create -n medai python=3.10
conda activate medai
```

### 2️⃣ Install dependencies
```bash
pip install -r ai_medical/requirements.txt
```

### 3️⃣ Optional models
```bash
python -m spacy download en_core_sci_sm
python -m spacy download en_ner_bc5cdr_md
```

---

## 🧩 Core Features

1. **End-to-End Clinical Pipeline** — from unstructured PDF → FHIR → Safety analysis  
2. **Deterministic JSON Outputs** — reproducible structured artifacts  
3. **Ontology-Aware Linking** — SNOMED-CT, RxNorm, and LOINC integration via SapBERT  
4. **FHIR-Compliant Mapping** — generates valid FHIR R4 bundles  
5. **Plain-Language Explanations** — readable summaries from clinical data  
6. **Safety & Risk Engine** — flags comorbidities, contraindications, and abnormal vitals  
7. **Grounded LLM Integration** — Mistral (Ollama) optional for factual summaries  

---

## 🧠 Pipeline Execution

Each module may be executed sequentially as follows:

| Step | Module | Command | Output |
|------|---------|----------|---------|
| 1 | **OCR** | `python ai_medical/ocr/extract_text.py` | `Sampleocr_output.txt` |
| 2 | **Sectionizer** | `python ai_medical/sectionizer/sectionize_text.py` | `sectionized_output.json` |
| 3 | **NER** | `python ai_medical/ner/extract_entities.py` | `ner_output_final.json` |
| 4 | **Entity Linking** | `python ai_medical/linker/entity_linking.py` | `linked_entities.json` |
| 5 | **FHIR Mapper** | `python ai_medical/fhir_mapper/fhir_mapping.py` | `fhir_bundle.json` |
| 6 | **Explanation Generator** | `python ai_medical/explain/generate_explanation.py` | `explanation.json`, `explanation.txt`, `explanation_fluent.txt` |
| 7 | **Safety Checker** | `python ai_medical/safety/safety_check.py` | `safety_report.json`, `safety_summary.txt`, `safety_fluent.txt` |

---

## 📖 Example Output Summary

| Module | Input | Output |
|---------|--------|--------|
| OCR | Clinical PDF | Extracted text |
| Sectionizer | OCR text | Structured sections JSON |
| NER | Section JSON | Entities with labels & confidence |
| Linker | NER JSON | Linked entities with ontology codes |
| FHIR Mapper | Linked JSON | FHIR R4 Bundle |
| Explanation | FHIR Bundle | Plain & fluent patient summaries |
| Safety | FHIR Bundle | Structured red-flag report |

---

## 🧬 Technical Highlights

- **Dual-Model NER Fusion:** combines SpaCy & BC5CDR results, merging spans and labels  
- **Clinical Filtering:** eliminates false positives for chemical and context terms  
- **FHIR Schema Construction:** auto-generates Patient, Practitioner, Condition, Observation, Procedure, Encounter  
- **Grounded LLM Summaries:** Mistral receives JSON-bounded facts, preventing hallucinations  
- **Safety Rules Engine:** detects  
  - *Stroke + Hypertension* → High risk  
  - *NSAID + CKD* → Nephrotoxicity risk (low-dose aspirin exception)  
  - *Beta-blocker + Asthma* → Bronchospasm risk  
  - *RAAS blocker + Hyperkalemia* → Arrhythmia risk  
- **Unit Normalization:** converts mg/dL → mmol/L for glucose, mg/dL → µmol/L for creatinine  
- **DetectedIssue Support:** ingests upstream FHIR warnings into safety notes  

---

## 🧪 Example: End-to-End Run

```bash
cd ai_medical
python ocr/extract_text.py
python sectionizer/sectionize_text.py
python ner/extract_entities.py
python linker/entity_linking.py
python fhir_mapper/fhir_mapping.py
python explain/generate_explanation.py
python safety/safety_check.py
```

**Resulting outputs:**
- `fhir_bundle.json` → Complete FHIR R4 patient record  
- `explanation.txt` → Human-readable factual summary  
- `safety_summary.txt` → Deterministic red-flag risk report  

---

## 🔒 Data Safety & Ethics

- No cloud APIs — runs entirely offline.  
- All data retained locally; no PHI transmission.  
- Deterministic LLM prompts prevent hallucination.  
- Complies with HL7 FHIR R4 structure for interoperability with EMRs.

---

## 🧱 Design Principles

- ✅ **Deterministic & Reproducible**  
- ✅ **Path-independent (OS-agnostic)**  
- ✅ **Modular JSON pipeline (no databases)**  
- ✅ **Explainable & Auditable outputs**  
- ✅ **FHIR-compliant interoperability**

---

## ⚡ Optional API Deployment

You can serve the pipeline via **FastAPI**:

```bash
pip install fastapi uvicorn
uvicorn ai_medical.api:app --reload
```

*(API router not included by default; add endpoints wrapping each module as needed.)*

---

## 📜 License & Citation

Developed as part of  
**ELEC5620 – Medical AI & ML Engineering Project (2025)**  
**University of Sydney – Group 7 (HACKERJEE)**  
**Author:** *Saahir Khan*

If used for academic or research purposes, please cite the associated  
Elsevier SSRN publication on *AI-Driven Meeting and Clinical Management Tools*.

---

## 🧾 Appendix

- Each sub-folder contains an `__init__.py` for import readiness.  
- Designed for offline execution and clinical transparency.  
- Tested on multiple PDF formats; deterministic across runs.

---

### 💬 Contact

For collaboration or inquiries, reach out via academic channels:  
**Saahir Khan – University of Sydney**
