# 🔧 Advanced Technologies Incorporated in Web Application

This document lists all advanced IT technologies utilized in the prototype, organized by category as per the "Incorporation of Advanced Technologies" requirements.

---

## 1. Application Frameworks

### Backend Frameworks
- **Flask** (Python)
  - Main web application framework
  - RESTful API endpoints
  - Route handling and request processing
  - Session management
  - File upload handling
  
- **FastAPI** (Python)
  - Optional API framework for external integrations
  - High-performance async API support
  - Automatic OpenAPI documentation

### Frontend Frameworks
- **Bootstrap 5**
  - Responsive UI components
  - Grid system and layout utilities
  - Modern CSS framework
  - Mobile-first design approach
  
- **Chart.js / Canvas API**
  - Interactive data visualization
  - Cost breakdown charts
  - Trend analysis graphs
  - Patient timeline visualizations

- **jQuery** (via Bootstrap dependencies)
  - DOM manipulation
  - AJAX requests
  - Event handling

### Database Frameworks
- **SQLAlchemy ORM**
  - Object-relational mapping
  - Database abstraction layer
  - Model definition and migrations
  
- **psycopg2**
  - PostgreSQL database adapter
  - Direct database connections
  - Query execution and result handling

---

## 2. Cloud Services

### AWS (Amazon Web Services)
- **Amazon RDS (Relational Database Service)**
  - PostgreSQL database hosting
  - Managed database service
  - Automatic backups and maintenance
  - Connection: `elec5620-as02-database.c38ki6o4abha.ap-southeast-2.rds.amazonaws.com`
  - Region: ap-southeast-2 (Sydney)
  
- **AWS S3** (via dependencies)
  - SciSpacy model distribution
  - Model downloads from S3 buckets:
    - `s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/`
    - Hosting of medical NLP models

### Database Cloud Services
- **PostgreSQL Cloud Database**
  - Fully managed PostgreSQL instance
  - Remote connection support
  - Multi-user concurrent access
  - Schema versioning and migrations

### Cloud Storage Patterns
- **Environment-based Configuration**
  - Environment variables for cloud credentials
  - Secure credential management
  - Multi-environment deployment support (dev/staging/prod)

---

## 3. Deployment Systems

### Application Deployment
- **Virtual Environment Management**
  - Python `venv` for isolated dependencies
  - `venv_ai` environment for AI-specific packages
  - Environment activation scripts (`activate.sh`)
  
- **Process Management**
  - Shell scripts for application startup (`start_web.sh`)
  - Background process support
  - Configuration management via environment variables

### Database Deployment
- **Schema Migration System**
  - SQL schema versioning (`elec5620_schema_postgres_v1.sql`)
  - Automated migration scripts
  - Idempotent schema updates
  - Enum type management

### Infrastructure as Code Patterns
- **Configuration Files**
  - `requirements.txt` - Python dependency management
  - `requirements_working.txt` - Validated dependency versions
  - Database connection configuration
  - Environment variable-based configuration

### Future-Ready Deployment
- **Container-Ready Architecture**
  - Modular code structure
  - Environment variable injection points
  - Stateless application design
  - Separation of concerns (app/db/static files)

---

## 4. New AI Tools & Techniques

### Advanced NLP & Medical AI

#### **OCR & Document Processing**
- **Tesseract OCR** (`pytesseract`)
  - Optical Character Recognition
  - Handles scanned documents and images
  - Multi-language support
  
- **pdfplumber**
  - Advanced PDF text extraction
  - Preserves document structure
  - Handles both native and scanned PDFs
  
- **pdf2image** + **Pillow**
  - PDF to image conversion
  - Image preprocessing for OCR
  - Multi-format image support

#### **Clinical Named Entity Recognition (NER)**
- **SpaCy** (General NLP)
  - Text processing pipeline
  - Tokenization and parsing
  
- **SciSpacy** (Biomedical NLP)
  - Medical domain-specific NLP
  - Biomedical text processing
  - Clinical terminology recognition
  
- **en_core_sci_sm** Model
  - Scientific/medical language model
  - Pre-trained biomedical embeddings
  - Entity recognition for medical text
  
- **en_ner_bc5cdr_md** Model
  - Disease and chemical entity recognition
  - BC5CDR dataset trained model
  - Clinical NER specialization
  - 114MB medical NER model

#### **Entity Linking & Ontology Mapping**
- **Sentence Transformers** (`sentence-transformers`)
  - Semantic similarity embeddings
  - Medical entity matching
  
- **SapBERT** (via transformers)
  - Biomedical entity embeddings
  - SNOMED-CT linking
  - RxNorm medication mapping
  - LOINC lab code linking
  
- **QuickUMLS**
  - Unified Medical Language System
  - Medical concept linking

#### **Deep Learning & Embeddings**
- **PyTorch** (`torch`)
  - Deep learning framework
  - Neural network models
  - Model inference and training support
  
- **Transformers Library**
  - Pre-trained transformer models
  - BERT-based architectures
  - Medical domain embeddings

#### **Large Language Models (LLM)**
- **Ollama**
  - Local LLM deployment
  - GPT-OSS model support
  - Mistral 7B integration
  - Document sectionization with LLM
  - Patient-friendly explanation generation
  
- **Mistral 7B Instruct**
  - Medical text summarization
  - Insurance quote rationales
  - Clinical explanation generation
  - Safety report summaries

#### **FHIR & Healthcare Standards**
- **FHIR R4 Mapper**
  - HL7 FHIR R4 bundle generation
  - Healthcare interoperability standard
  - Structured medical data output
  - Resource type generation (Patient, Condition, Medication, etc.)

#### **Medical Ontology Integration**
- **SNOMED-CT** Integration
  - International clinical terminology
  - Condition code mapping
  - Standardized medical concepts
  
- **RxNorm** Integration
  - Medication standardization
  - Drug code mapping
  - Prescription terminology
  
- **LOINC** Integration
  - Laboratory test identification
  - Observation code mapping
  - Lab result standardization
  
- **ICD-10-AM** Support
  - Australian modification of ICD-10
  - Disease classification
  - Diagnosis code mapping

### AI-Powered Features

#### **Clinical Decision Support**
- **Safety Checker Engine**
  - Drug-drug interaction detection
  - Contraindication analysis
  - Comorbidity risk assessment
  - Clinical safety rules engine
  
- **Risk Assessment Algorithm**
  - Multi-factor risk scoring
  - Insurance risk calculation
  - Health risk stratification

#### **Document Intelligence Pipeline**
- **7-Stage AI Processing Pipeline:**
  1. **OCR** - Text extraction from documents
  2. **Sectionizer** - Clinical section identification
  3. **NER** - Medical entity extraction
  4. **Entity Linking** - Ontology code mapping
  5. **FHIR Mapper** - Standard format conversion
  6. **Explanation Generator** - Patient-friendly summaries
  7. **Safety Checker** - Red flag detection

#### **Natural Language Generation**
- **Patient-Friendly Explanations**
  - Plain language medical summaries
  - Automatic glossary generation
  - Structured text output
  - LLM-enhanced readability

#### **Code Generation (AI-Assisted)**
- **Automated Rationale Generation**
  - Insurance quote explanations
  - AI-generated recommendations
  - Context-aware reasoning outputs

---

## Summary Statistics

### Technology Count by Category

| Category | Count | Technologies |
|---------|-------|--------------|
| **Application Frameworks** | 8 | Flask, FastAPI, Bootstrap 5, Chart.js, jQuery, SQLAlchemy, psycopg2 |
| **Cloud Services** | 3+ | AWS RDS, AWS S3, PostgreSQL Cloud |
| **Deployment Systems** | 5+ | venv, Shell scripts, Migration system, Config management |
| **AI Tools & Techniques** | 25+ | OCR, NLP models, LLMs, Transformers, FHIR, Ontologies, Safety engine |

### Total Advanced Technologies: **40+**

---

## Justification & Innovation

### Why These Technologies Demonstrate Innovation:

1. **Medical AI Pipeline**
   - Integration of multiple specialized medical NLP models
   - End-to-end clinical document processing
   - FHIR R4 standard compliance for healthcare interoperability

2. **Hybrid AI Architecture**
   - Combination of rule-based and ML-based systems
   - Deterministic safety checks + probabilistic entity recognition
   - Local LLM deployment (Ollama) for privacy-preserving AI

3. **Cloud-Native Architecture**
   - Scalable database infrastructure
   - Environment-based configuration
   - Production-ready deployment patterns

4. **Advanced NLP Stack**
   - Specialized biomedical models (not general-purpose)
   - Multiple ontology linking systems
   - Semantic similarity for entity matching

5. **Real-World Healthcare Integration**
   - FHIR R4 standard compliance
   - Multiple medical coding systems (SNOMED, RxNorm, LOINC, ICD-10-AM)
   - Clinical decision support algorithms

6. **Modern Web Architecture**
   - RESTful API design
   - Responsive frontend
   - Role-based access control
   - Session management and security

---

## Implementation Evidence

### Code Locations:

- **Application Frameworks:**
  - `web_app/app.py` - Flask application (3000+ lines)
  - `web_app/templates/*.html` - Bootstrap 5 UI
  - `web_app/database_config.py` - SQLAlchemy models

- **Cloud Services:**
  - `database/aws_database.py` - AWS RDS connection
  - `web_app/rds_repository.py` - Cloud database queries

- **Deployment:**
  - `requirements.txt` - Dependency management
  - `activate.sh`, `start_web.sh` - Deployment scripts

- **AI Tools:**
  - `ai_medical/ocr/` - OCR implementation
  - `ai_medical/ner/` - NER with SpaCy models
  - `ai_medical/linker/` - Entity linking
  - `ai_medical/safety/` - Safety checker
  - `ai_medical/explain/` - LLM explanations
  - `ai_medical/sectionizer/sectionize_with_ollama.py` - LLM sectionization

---

**Last Updated:** January 2025  
**Status:** ✅ All technologies actively implemented and operational

