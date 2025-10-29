# 🚀 Setup Local Environment for Web App

## Quick Setup - Create venv in /Users/thanhle

### Step 1: Create Virtual Environment

```bash
# Create venv in your home directory (fast, not on Google Drive)
cd /Users/thanhle
python3.11 -m venv venv_web_local

# Activate it
source /Users/thanhle/venv_web_local/bin/activate
```

### Step 2: Install Essential Web App Packages

```bash
# Core web framework
pip install flask==3.0.0
pip install flask-login==0.6.3
pip install flask-wtf==1.2.1
pip install flask-sqlalchemy==3.1.1
pip install wtforms==3.1.1

# Database
pip install sqlalchemy==2.0.23

# Security
pip install werkzeug==3.0.1

# Essential only (skip heavy ML libs for now)
pip install pandas==2.1.4

# Optional: If you want document processing to work
# pip install pdfplumber==0.11.4
# pip install pytesseract==0.3.13
# pip install pdf2image==1.17.0
# pip install pillow==10.1.0
# pip install pymupdf==1.23.8
```

### Step 3: Run Web App from Google Drive

```bash
# Stay in your project directory
cd /Users/thanhle/Library/CloudStorage/GoogleDrive-lenhothanh.nsl@gmail.com/.shortcut-targets-by-id/1Je2GU6cAmriwQ_9lhORCt8JeHBjH-2Yq/ELEC5620/Code/5620medai/web_app

# But use the local venv
source /Users/thanhle/venv_web_local/bin/activate

# Run the app
python app.py
```

### Step 4: Access the Web App

```
http://127.0.0.1:5000

Login:
- patient1 / password123
- dr.smith / password123
- admin / password123
```

---

## What This Does

**Benefits:**
- ✅ Virtual environment on LOCAL drive (fast)
- ✅ Only essential packages (no heavy ML libs)
- ✅ App starts in 5-10 seconds (not 60+ seconds)
- ✅ No segmentation faults
- ✅ All web features work

**Trade-offs:**
- ⚠️ AI document processing disabled (but rest works)
- ⚠️ Insurance quotes work (simulated data)
- ⚠️ All dashboards, forms, databases work perfectly

---

## Alternative: Minimal requirements.txt

Create `web_app/requirements_minimal.txt`:

```txt
# Minimal Web App Requirements (No ML)
flask==3.0.0
flask-login==0.6.3
flask-wtf==1.2.1
flask-sqlalchemy==3.1.1
wtforms==3.1.1
werkzeug==3.0.1
sqlalchemy==2.0.23
pandas==2.1.4
```

Then install:
```bash
source /Users/thanhle/venv_web_local/bin/activate
pip install -r web_app/requirements_minimal.txt
```

---

## Quick Test

After setup:
```bash
source /Users/thanhle/venv_web_local/bin/activate
cd web_app
python app.py
```

Should see:
```
⚠ AI Medical Pipeline unavailable: ...
(This is OK - web app still works!)

============================================================
🏥 Clinical AI Assistance System - Web Application
============================================================
🌐 Server starting at: http://127.0.0.1:5000
```

---

## Full AI Features (Optional)

If you need AI document processing later:
```bash
source /Users/thanhle/venv_web_local/bin/activate

# Add ML packages (will take longer to install)
pip install torch==2.1.1
pip install numpy==1.26.2
pip install scispacy==0.5.1
pip install spacy==3.5.4

# Download SpaCy models
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_core_sci_sm-0.5.1.tar.gz
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.1/en_ner_bc5cdr_md-0.5.1.tar.gz
```

But for demo/testing, the minimal setup is enough!

