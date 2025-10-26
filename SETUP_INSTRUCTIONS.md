# Environment Setup Instructions

## Issue

Python 3.13 is too new for some of the medical NLP packages in this project. The packages with C++ extensions (leveldb, nmslib, PyRuSH, etc.) haven't been updated yet to support Python 3.13.

## Recommended Solution: Use Python 3.10 or 3.11

### Option 1: Using Conda (Recommended)

```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install miniforge (includes conda)
brew install --cask miniforge

# Initialize conda
conda init zsh

# Restart your terminal, then:
cd /Users/thanhle/Library/CloudStorage/GoogleDrive-lenhothanh.nsl@gmail.com/.shortcut-targets-by-id/1Je2GU6cAmriwQ_9lhORCt8JeHBjH-2Yq/ELEC5620/Code/5620medai

# Create environment with Python 3.10
conda create -n medai python=3.10 -y
conda activate medai

# Install dependencies
pip install -r requirements.txt

# Download SpaCy models
python -m spacy download en_core_sci_sm
python -m spacy download en_ner_bc5cdr_md
```

### Option 2: Install Python 3.10 with Homebrew

```bash
# Install Python 3.10
brew install python@3.10

# Remove existing venv
rm -rf venv

# Create new venv with Python 3.10
/opt/homebrew/opt/python@3.10/bin/python3.10 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Option 3: Install System Dependencies for C++ Compilation

If you want to try with Python 3.13, you need Xcode Command Line Tools:

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Then try the installation again
source venv/bin/activate
pip install -r requirements_updated.txt
```

## Required System Tools

Don't forget to install these system dependencies:

```bash
# Install Tesseract OCR
brew install tesseract

# Install Poppler (for PDF processing)
brew install poppler
```

## After Setup

Once your environment is set up, you can run the pipeline modules:

```bash
# Activate environment
source venv/bin/activate  # for venv
# OR
conda activate medai  # for conda

# Run pipeline
cd ai_medical
python ocr/extract_text.py
python sectionizer/sectionize_text.py
python ner/extract_entities.py
python linker/entity_linking.py
python fhir_mapper/fhir_mapping.py
python explain/generate_explanation.py
python safety/safety_check.py
```

