# 🏥 Clinical AI Assistance System

**A comprehensive web-based platform for AI-driven clinical document analysis, insurance quote matching, and medical data management.**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-AWS%20RDS-blue)
![FHIR](https://img.shields.io/badge/FHIR-R4-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📖 Overview

The **Clinical AI Assistance System** is a full-stack web application that combines:
- **AI-Powered Medical Document Analysis** - 8-stage clinical pipeline (OCR → FHIR → Safety)
- **Insurance Quote Matching** - AI-driven health insurance recommendations
- **Doctor-Patient Workflow** - Review, approval, and collaboration tools
- **Financial Assistance** - Loan matching and financial aid recommendations
- **Role-Based Access Control** - Secure multi-role authentication

Built with **Flask**, **PostgreSQL (AWS RDS)**, and integrated with local LLM models via **Ollama**.

---

## ✨ Key Features

### 🔬 AI Clinical Document Analysis (Use Case 2)
- **8-Stage Medical Pipeline**:
  1. OCR - Extract text from PDFs/images
  2. Sectionizer - Segment document into medical sections
  3. NER - Named Entity Recognition (conditions, medications, allergies)
  4. Entity Linking - Map to SNOMED-CT, RxNorm, ICD-10-AM
  5. FHIR Mapping - Generate FHIR R4 compliant resources
  6. Explanation Generation - Patient-friendly summaries
  7. Safety Checker - Detect red flags and contraindications
  8. Mistral LLM Analysis - AI-powered clinical insights
- **Real-time Progress Tracking** - Live progress bars with step-by-step updates
- **History Management** - View past analyses with file downloads
- **Doctor Recommendations** - AI suggests suitable doctors for review

### 💊 Insurance Quote Generation (Use Case 3)
- **AI-Powered Matching** - 30+ Australian private health insurance funds
- **Medical History Integration** - Personalized quotes based on health data
- **Cost Breakdown Analysis** - Detailed premium and coverage comparisons
- **AI Explanations** - "Why This Plan?" insights using Mistral:7b-instruct
- **Quote History** - View and compare past quote requests
- **PDF/HTML Export** - Download quote summaries

### 👨‍⚕️ Doctor-Patient Collaboration
- **Review Workflow** - Patients request doctor reviews of AI analysis
- **Approval System** - Doctors approve/reject/escalate clinical findings
- **Pending Reviews Dashboard** - Track all review requests
- **Review History** - Complete audit trail of all decisions
- **Digital Signatures** - Secure approval tracking

### 💰 Financial Assistance (Use Case 4)
- **Loan Matching** - AI-powered loan recommendations
- **Financial Profile Analysis** - Income and expense assessment
- **Assistance Eligibility** - Government and private aid matching

### 🔐 User Management
- **Multi-Role System** - Patients, Doctors, Admins
- **User Registration** - Self-service signup with role selection
- **Doctor Approval Workflow** - Admin approval required for doctor accounts
- **Session Persistence** - Remember-me functionality across restarts

---

## 🚀 Quick Start

> **📌 FOR GRADERS**: The application **MUST** be run from the `web_app/` directory. See [🚀 Running the Application](#-running-the-application) section for detailed instructions.

### Prerequisites

- **Python 3.10+**
- **PostgreSQL** (or AWS RDS access)
- **System Dependencies** (for OCR):
  - Tesseract OCR: `brew install tesseract` (macOS) or `apt-get install tesseract-ocr` (Linux)
  - Poppler: `brew install poppler` (macOS) or `apt-get install poppler-utils` (Linux)
- **Optional**: Ollama for AI explanations (see [Ollama Setup](#-ollama-setup) below)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd 5620medai
   ```

2. **Create virtual environment**
```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Install SpaCy models**
```bash
python -m spacy download en_core_sci_sm
python -m spacy download en_ner_bc5cdr_md
```

5. **Configure database** (see [Database Setup](#-database-setup))

6. **Run the application** (see detailed instructions in [🚀 Running the Application](#-running-the-application) section)
   
   **⚠️ CRITICAL FOR GRADERS**: 
   ```bash
   # You MUST navigate to web_app directory first
   cd web_app
   
   # Then run the application
   python app.py
   ```
   
   See the [Running the Application](#-running-the-application) section below for complete details.

7. **Set up Ollama (Optional, for AI explanations)**
   ```bash
   # See detailed instructions in "Ollama Setup" section below
   ```

---

## 🚀 Running the Application

### ⚠️ CRITICAL: How to Start the Web Application

**FOR GRADERS**: Follow these exact steps to run the application:

1. **Navigate to the `web_app` directory** (this is REQUIRED):
   ```bash
   cd web_app
   ```

2. **Start the Flask server**:
   ```bash
   python app.py
   ```
   
   **OR if using Python 3 explicitly:**
   ```bash
   python3 app.py
   ```

3. **Look for this output** confirming the server started:
   ```
   🌐 Server starting at: http://127.0.0.1:5000
   * Debugger is active!
   * Running on http://127.0.0.1:5000
   Press CTRL+C to stop the server
   ```

4. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

5. **Login** with demo credentials (see [Demo Credentials](#-demo-credentials) below)

---

### ⚠️ Common Mistakes

❌ **WRONG**: Running from project root
```bash
# DON'T DO THIS:
cd /path/to/5620medai
python app.py  # ❌ This will fail with import errors
```

✅ **CORRECT**: Running from web_app directory
```bash
# DO THIS:
cd /path/to/5620medai/web_app
python app.py  # ✅ This works!
```

### Troubleshooting

**Issue**: `ModuleNotFoundError` or `ImportError` when running `python app.py`
- **Solution**: Make sure you're in the `web_app/` directory
- Check: `pwd` should show `.../5620medai/web_app`

**Issue**: `No module named 'flask'`
- **Solution**: Activate your virtual environment first
- Run: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)

**Issue**: Port 5000 already in use
- **Solution**: Kill the process using port 5000 or use a different port
- Change port: Edit `web_app/app.py` line `app.run(port=5001)` (or any available port)

---

## 🤖 Ollama Setup (Optional)

**Ollama** is required for AI-powered explanations in insurance quotes and clinical analysis. The application will work without Ollama, but will use fallback text instead of AI-generated explanations.

### Installation

#### macOS
```bash
# Using Homebrew (recommended)
brew install ollama

# Or download from website
# Visit: https://ollama.ai/download
```

#### Linux
```bash
# Using the installation script
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from website
# Visit: https://ollama.ai/download
```

#### Windows
```bash
# Download the installer from:
# https://ollama.ai/download

# Run the installer and follow the setup wizard
```

### Start Ollama Service

After installation, start the Ollama service:

```bash
# macOS/Linux - start as background service
ollama serve

# Or on macOS with Homebrew, it may auto-start as a service
# Check with: brew services list | grep ollama
```

### Pull Mistral Model

Download the `mistral:7b-instruct` model used by the application:

```bash
# Pull the model (this will download ~4GB)
ollama pull mistral:7b-instruct

# Verify installation
ollama list

# Test the model
ollama run mistral:7b-instruct "Hello, this is a test."
```

### Verify Installation

Test that Ollama is working:

```bash
# Check if ollama is in PATH
which ollama

# Check Ollama version
ollama --version

# List available models
ollama list

# Verify mistral:7b-instruct is available
ollama show mistral:7b-instruct
```

### Configuration

The application automatically detects Ollama if it's in your system PATH. To specify a custom path:

```bash
# In web_app/.env file
OLLAMA_BIN=/custom/path/to/ollama
```

### Troubleshooting

**Issue**: `ollama: command not found`
- **Solution**: Ensure Ollama is installed and in your system PATH
- Add Ollama to PATH if needed: `export PATH=$PATH:/path/to/ollama`

**Issue**: Model not found when running the app
- **Solution**: Ensure you've run `ollama pull mistral:7b-instruct`
- Verify with: `ollama list | grep mistral`

**Issue**: Ollama service not running
- **Solution**: Start the service: `ollama serve` (or restart if already running)
- Check if port 11434 is available: `lsof -i :11434`

**Issue**: Slow or timeout errors
- **Solution**: Ensure you have sufficient RAM (7B model needs ~8GB+)
- Try a smaller model: `ollama pull mistral:7b-instruct-q4_0` (quantized, smaller)

### Performance Notes

- **First Run**: Model loading may take 30-60 seconds
- **RAM Requirements**: Mistral 7B requires ~8GB RAM minimum
- **GPU Acceleration**: If you have a compatible GPU, Ollama will use it automatically
- **Network**: Model download happens only once (~4GB)

---

## 🗄️ Database Setup

### AWS RDS PostgreSQL

The application uses PostgreSQL on AWS RDS. Configure connection in `web_app/.env`:

```bash
DB_HOST=your-rds-endpoint.amazonaws.com
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
```

### Local PostgreSQL (Development)

1. **Create database**
   ```sql
   CREATE DATABASE clinical_ai;
   ```

2. **Run schema migration**
   ```bash
   cd database
   python aws_database.py
   ```

3. **Load sample data** (optional)
   ```bash
   python create_mock_data.py
   ```

### Schema Files

- `database/elec5620_schema_postgres_v1.sql` - Complete PostgreSQL schema
- Includes: users, doctors, patients, medical_records, clinical_analysis_data, ai_approvals, quote_requests, etc.

---

## 👥 Demo Credentials

### Default Password (All Users)
```
password123
```

### User Accounts

| Role | Username | Description |
|------|----------|-------------|
| **Patient** | `patient1` | John Doe (MRN-001234) |
| **Patient** | `patient2` | Jane Wilson (MRN-005678) |
| **Patient** | `patient16` | Test patient |
| **Doctor** | `dr.alice` | Dr. Alice Smith (Approved) |
| **Doctor** | `dr.smith` | Cardiology specialist |
| **Doctor** | `dr.jones` | Neurology specialist |
| **Admin** | `admin` | System administrator |
| **Admin** | `it.admin` | IT administrator |

**Note**: 20+ mock doctors are available with various specializations. All use password `password123`.

### Admin Access - View All Users

To view all users in the system:

1. **Login as admin**:
   - Username: `admin`
   - Password: `password123`

2. **Access User Management**:
   - After logging in, navigate to the **Admin Dashboard**
   - Click on the **"Users"** menu item in the navigation bar
   - Or go directly to: `http://127.0.0.1:5000/admin/users`

3. **Features Available**:
   - View all registered users (patients, doctors, admins)
   - View complete doctor profiles (specialization, AHPRA number, approval status)
   - Approve/reject doctor registrations
   - See user statistics and system overview

**Alternative Admin Account**: You can also use `it.admin` with password `password123` for admin access.

---

## 📁 Project Structure

```
5620medai/
│
├── web_app/                    # Main Flask application
│   ├── app.py                 # Flask routes and main application
│   ├── models.py              # User models and in-memory storage
│   ├── forms.py              # Flask-WTF forms (login, signup, insurance, clinical)
│   ├── db_auth.py            # Database authentication utilities
│   ├── rds_repository.py     # AWS RDS database operations
│   ├── database_config.py    # SQLAlchemy database configuration
│   │
│   ├── clinical_analysis_processor.py  # Clinical pipeline orchestrator
│   ├── doctor_recommender.py           # AI doctor recommendation
│   ├── insurance_engine.py            # Insurance quote matching engine
│   ├── insurance_models.py            # Insurance data models
│   ├── insurance_utils.py             # Insurance utilities
│   ├── ai_explainer.py                # Ollama LLM integration
│   ├── financial_assistance.py        # Financial aid matching
│   ├── approval_models.py             # Doctor review/approval models
│   ├── patient_history_analyzer.py    # Patient history analysis
│   │
│   ├── UC2_models/            # Clinical AI pipeline modules
│   │   ├── ocr/               # Optical Character Recognition
│   │   ├── sectionizer/       # Document section segmentation
│   │   ├── ner/              # Named Entity Recognition
│   │   ├── linker/           # Entity linking (SNOMED, RxNorm)
│   │   ├── fhir_mapper/      # FHIR R4 bundle generation
│   │   ├── explain/          # Explanation generation
│   │   └── safety/           # Safety checker
│   │
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html        # Base layout
│   │   ├── login.html       # Login page
│   │   ├── signup.html      # User registration
│   │   ├── dashboard_patient.html
│   │   ├── dashboard_doctor.html
│   │   ├── dashboard_admin.html
│   │   ├── clinical_analysis_*.html  # Clinical analysis pages
│   │   ├── insurance_*.html          # Insurance quote pages
│   │   └── review_*.html             # Doctor review pages
│   │
│   └── static/               # Static assets
│       └── css/
│           └── style.css     # Custom styles
│
├── database/                 # Database scripts
│   ├── elec5620_schema_postgres_v1.sql  # PostgreSQL schema
│   ├── aws_database.py       # Schema migration script
│   └── create_mock_data.py   # Sample data generator
│
├── ai_medical/               # Original AI pipeline (legacy)
│   ├── ocr/
│   ├── sectionizer/
│   ├── ner/
│   ├── linker/
│   ├── fhir_mapper/
│   ├── explain/
│   └── safety/
│
├── requirements.txt          # Complete Python dependencies
└── README.md                 # This file
```

---

## 🔧 Configuration

### Environment Variables

Create `web_app/.env`:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration (AWS RDS)
DB_HOST=your-rds-endpoint.amazonaws.com
DB_PORT=5432
DB_NAME=clinical_ai
DB_USER=your_username
DB_PASSWORD=your_password

# Session Configuration
SESSION_COOKIE_NAME=clinical_ai_session
SESSION_COOKIE_SAMESITE=Lax

# Optional: Ollama Configuration
OLLAMA_BIN=ollama  # Path to ollama binary (default: 'ollama')
```

### Application Settings

- **File Upload**: Maximum 16MB per file
- **Session Duration**: 7 days (30 days with "Remember Me")
- **Upload Storage**: `web_app/uploads/user_id_analysis_id/`

---

## 🎯 Use Cases Implemented

### ✅ Use Case 1: AI-Assisted Clinical Record Analysis (Saahir Khan)
- **Status**: ✅ Complete
- **Features**: 8-stage pipeline, real-time progress, history management, file downloads
- **Route**: `/clinical-analysis`

### ✅ Use Case 2: Review AI Output & Approve (Thanh Le)
- **Status**: ✅ Complete
- **Features**: Doctor review workflow, approval decisions, review history
- **Route**: `/review/pending`, `/review/<analysis_id>`

### ✅ Use Case 3: Request Insurance Quote (Venkatesh Badri Narayanan)
- **Status**: ✅ Complete
- **Features**: AI-powered matching, 30+ insurance funds, cost breakdown, AI explanations
- **Route**: `/insurance/quote`

### ✅ Use Case 4: Financial Assistance with Loan Matching (Venkatesh Badri Narayanan)
- **Status**: ✅ Commming soon
- **Features**: Loan matching, financial profile analysis
- **Route**: `/financial-assistance`

### 🚧 Use Case 5: Patient History Documentation (Sarvadnya Kamble)
- **Status**: 🚧 Coming Soon
- **Note**: Marked as "Coming Soon" in doctor dashboard

---

## 🔐 Security Features

- **Password Hashing**: Werkzeug secure password hashing
- **Session Management**: Flask-Login with persistent sessions
- **CSRF Protection**: Flask-WTF forms with CSRF tokens
- **Role-Based Access Control**: Decorators for route protection
- **Secure Cookies**: HTTPOnly, SameSite, Secure flags
- **File Upload Validation**: Secure filename handling, file type checks
- **Database Parameterization**: SQL injection prevention via psycopg2

---

## 🧠 AI Pipeline Integration

### Pipeline Stages

| Stage | Module | Description | Output |
|-------|--------|-------------|--------|
| 1 | OCR | Extract text from PDFs/images | `extracted_text.txt` |
| 2 | Sectionizer | Segment into medical sections | `sections.json` |
| 3 | NER | Extract clinical entities | `entities.json` |
| 4 | Entity Linking | Map to medical ontologies | `linked_entities.json` |
| 5 | FHIR Mapper | Generate FHIR R4 bundles | `fhir_bundle.json` |
| 6 | Explanation | Patient-friendly summaries | `explanation.json` |
| 7 | Safety Check | Detect red flags | `safety_report.json` |
| 8 | Mistral LLM | AI-powered clinical analysis | `mistral_analysis.txt` |

### AI Models Used

- **SpaCy**: `en_core_sci_sm`, `en_ner_bc5cdr_md` (Clinical NER)
- **Sentence Transformers**: SapBERT (Entity linking)
- **Ollama**: `mistral:7b-instruct` (Explanations and clinical analysis)

---

## 🔌 API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET/POST /signup` - User registration
- `GET /logout` - User logout

### Patient Routes
- `GET /dashboard/patient` - Patient dashboard
- `GET/POST /insurance/quote` - Request insurance quote
- `GET /insurance/history` - Quote history
- `GET /clinical-analysis` - Upload clinical document
- `GET /clinical-analysis/history` - Analysis history
- `GET /clinical-analysis/results/<analysis_id>` - View results
- `GET /clinical-analysis/recommend-doctors/<analysis_id>` - Find doctors
- `POST /clinical-analysis/request-review/<analysis_id>/<doctor_id>` - Request review

### Doctor Routes
- `GET /dashboard/doctor` - Doctor dashboard
- `GET /review/pending` - Pending reviews
- `GET /review/<analysis_id>` - Review analysis
- `POST /review/<analysis_id>` - Submit review decision
- `GET /review/history` - Review history
- `GET /doctor/profile/<doctor_id>` - Doctor profile

### Admin Routes
- `GET /dashboard/admin` - Admin dashboard
- `GET /admin/users` - User management
- `GET /admin/view-doctor/<doctor_id>` - View doctor profile
- `POST /admin/approve-doctor/<doctor_id>` - Approve doctor registration
- `POST /admin/reject-doctor/<doctor_id>` - Reject doctor registration

---

## 🧪 Testing

### Manual Testing Checklist

- [x] User authentication (login, signup, logout)
- [x] Role-based access control
- [x] Clinical document upload and processing
- [x] Insurance quote generation
- [x] Doctor review workflow
- [x] File download/view functionality
- [x] Database persistence
- [x] Session management

### Running Tests

```bash
# Install test dependencies (optional)
pip install pytest pytest-flask

# Run tests (when test suite is added)
pytest tests/
```

---

## 📊 Database Schema

### Key Tables

- **users** - User accounts (patients, doctors, admins)
- **doctors** - Doctor-specific information (specialization, AHPRA, approval status)
- **patients** - Patient-specific information
- **medical_records** - Uploaded documents and metadata
- **clinical_analysis_data** - Complete pipeline outputs (JSONB)
- **ai_approvals** - Doctor review decisions
- **quote_requests** - Insurance quote requests
- **quote_recommendations** - Generated quotes and AI scores
- **fhir_bundles** - FHIR R4 compliant medical data
- **safety_flags** - Safety check results

See `database/elec5620_schema_postgres_v1.sql` for complete schema.

---

## 🚧 Known Limitations & Coming Soon

### Coming Soon Features
- ❌ Patient History Documentation (Use Case 5) - Timeline and trends analysis
- ❌ Insurance Quote Reviews - Doctor review of insurance quotes
- ❌ Compare Quotes - Side-by-side quote comparison

### Current Limitations
- File size limit: 16MB per upload
- OCR quality depends on document clarity
- LLM explanations require Ollama installation
- Some features may require database schema updates

---

## 🛠️ Development

### Adding New Features

1. **Create route** in `app.py`
2. **Add form** in `forms.py` (if needed)
3. **Create template** in `templates/`
4. **Update database** via `database/aws_database.py` (if schema changes)
5. **Add tests** (when test suite is established)

### Code Style

- Follow PEP 8
- Use type hints where possible
- Document functions with docstrings
- Use meaningful variable names

---

## 📝 License & Credits

**ELEC5620 – Medical AI & ML Engineering Project (2025)**  
**University of Sydney – Group 7 (HACKERJEE)**  

### Team Members
- **Saahir Khan** - Clinical Record Analysis (Use Case 2)
- **Thanh Le** - Review & Approval System (Use Case 2)
- **Venkatesh Badri Narayanan** - Insurance Quotes & Financial Assistance (Use Cases 3 & 4)
- **Sarvadnya Kamble** - Patient History (Use Case 5 - Coming Soon)

### Technologies
- Flask 3.0.0
- PostgreSQL (AWS RDS)
- SpaCy, Sentence Transformers
- Ollama (Mistral:7b-instruct)
- Bootstrap 5
- Chart.js

---

## 📞 Support & Documentation

- **Main Documentation**: See `web_app/README.md` for detailed feature docs
- **AI Pipeline**: See `ai_medical/README.md`
- **Insurance Feature**: See `web_app/INSURANCE_QUOTE_FEATURE.md`
- **Clinical Analysis**: See `web_app/CLINICAL_ANALYSIS_FEATURE.md`

---

## ⚠️ Production Deployment Notes

**DO NOT deploy to production without:**

1. ✅ Change all default passwords
2. ✅ Set strong `SECRET_KEY` in environment
3. ✅ Use HTTPS (set `SESSION_COOKIE_SECURE=True`)
4. ✅ Configure AWS RDS with proper security groups
5. ✅ Enable audit logging
6. ✅ Add rate limiting
7. ✅ Implement backup strategy
8. ✅ Follow HIPAA compliance guidelines (if handling PHI)
9. ✅ Enable CSRF protection (already implemented)
10. ✅ Regular security updates

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Status**: Active Development
