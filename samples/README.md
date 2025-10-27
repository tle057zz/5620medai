# 📁 Sample Medical Documents for Testing

This folder contains sample medical documents for testing the **Insurance Quote Document Upload** feature.

---

## 📄 Available Sample Files

### 1. **sample_medical_report_1.txt** (Text Format)
**Patient:** John Smith  
**Type:** Complete medical record  
**Contains:**
- Patient demographics
- Chief complaint
- Vital signs (BP: 145/92, BMI: 30.1)
- Medical history (Diabetes, Hypertension, Hyperlipidemia)
- Current medications (Metformin, Lisinopril, Atorvastatin, Aspirin)
- Lab results (Glucose, HbA1c, Cholesterol, Creatinine)
- Assessment & plan

**Good for testing:** Basic document processing, multiple conditions and medications

---

### 2. **sample_prescription.txt** (Text Format)
**Patient:** Maria Garcia  
**Type:** Prescription record  
**Contains:**
- Patient allergies (Penicillin)
- Current diagnoses (COPD, CAD, GERD)
- 6 prescriptions with dosage instructions
- Vital signs
- Instructions and follow-up

**Good for testing:** Medication extraction, multiple drug interactions

---

### 3. **sample_lab_results.txt** (Text Format)
**Patient:** Robert Taylor  
**Type:** Comprehensive lab report  
**Contains:**
- Complete Blood Count (CBC)
- Comprehensive Metabolic Panel
- Lipid Panel
- HbA1c
- Critical values (High glucose, elevated creatinine, low eGFR)
- Stage 3 Chronic Kidney Disease indicators
- Dyslipidemia markers

**Good for testing:** Lab value extraction, critical findings, comorbidity detection

---

## 🎨 Generating PDF Versions

To create PDF versions of these documents:

```bash
cd samples
python3 generate_sample_pdfs.py
```

**Requirements:**
```bash
pip install reportlab
```

**Output:**
- `sample_medical_report_1.pdf`
- `sample_prescription.pdf`
- `sample_lab_results.pdf`

---

## 🧪 How to Use These Files

### Method 1: Text Files (Always Work)
1. Upload `.txt` files directly to the web app
2. OCR will extract text (fast processing)
3. NER will identify entities

### Method 2: PDF Files (Requires ReportLab)
1. Generate PDFs using the script above
2. Upload `.pdf` files to the web app
3. Full OCR → NER → Entity Linking pipeline runs

---

## 📊 Expected Extraction Results

### From `sample_medical_report_1.txt`:
**Conditions:**
- Type 2 Diabetes Mellitus
- Hypertension
- Hyperlipidemia

**Medications:**
- Metformin
- Lisinopril
- Atorvastatin
- Aspirin

**Observations:**
- BMI: 30.1
- Blood Pressure: 145/92 mmHg
- Glucose: 165 mg/dL
- Cholesterol: 220 mg/dL

---

### From `sample_prescription.txt`:
**Conditions:**
- COPD
- Coronary Artery Disease
- GERD

**Medications:**
- Albuterol
- Tiotropium (Spiriva)
- Clopidogrel (Plavix)
- Metoprolol
- Omeprazole
- Prednisone

**Observations:**
- Blood Pressure: 138/86 mmHg
- O2 Saturation: 94%

**Risk Factors:**
- Drug interaction: Clopidogrel (anticoagulant) present
- COPD + CAD comorbidity

---

### From `sample_lab_results.txt`:
**Conditions:**
- Type 2 Diabetes Mellitus (poorly controlled)
- Chronic Kidney Disease Stage 3
- Dyslipidemia

**Lab Values:**
- Glucose: 185 mg/dL (HIGH)
- Creatinine: 1.8 mg/dL (HIGH)
- eGFR: 42 mL/min (LOW)
- HbA1c: 8.9% (HIGH)
- Cholesterol: 245 mg/dL (HIGH)

**Risk Profile:** HIGH RISK
- Multiple comorbidities
- Reduced kidney function
- Poor diabetes control

---

## 🎯 Testing Scenarios

### Scenario 1: Low-Risk Patient
**File:** Create a custom document with minimal conditions
**Expected:** Budget insurance plans recommended

### Scenario 2: Moderate-Risk Patient
**File:** `sample_medical_report_1.txt`
**Expected:** Comprehensive plans with chronic disease management

### Scenario 3: High-Risk Patient
**File:** `sample_lab_results.txt`
**Expected:** Premium plans, nephrology coverage recommended

### Scenario 4: Drug Interaction Detection
**File:** `sample_prescription.txt`
**Expected:** Enhanced risk assessment flags anticoagulant

---

## 📝 Creating Custom Test Files

To create your own test files:

1. **Copy a template:**
   ```bash
   cp sample_medical_report_1.txt my_custom_test.txt
   ```

2. **Edit the file:**
   - Change patient demographics
   - Add/remove conditions
   - Modify medications
   - Adjust lab values

3. **Upload and test:**
   - The AI pipeline will process any medical text
   - More structured documents yield better results

---

## 🔍 What the AI Pipeline Extracts

### Entity Types Detected:
- **DISEASE/CONDITION:** Diabetes, Hypertension, COPD, Cancer, etc.
- **MEDICATION/DRUG:** Metformin, Lisinopril, Aspirin, etc.
- **PROCEDURE:** Surgeries, treatments
- **OBSERVATION:** Vital signs, lab values (BP, BMI, glucose, cholesterol)

### Ontology Linking:
- Conditions → SNOMED-CT codes
- Medications → RxNorm codes
- Lab tests → LOINC codes

---

## 🚀 Quick Test Command

```bash
# Start the server
cd web_app
python3 app.py

# In browser:
# 1. Visit: http://127.0.0.1:5000
# 2. Login: patient_john / password123
# 3. Click: Request Quote
# 4. Upload: samples/sample_medical_report_1.txt
# 5. Wait for processing
# 6. Click: Auto-Fill Form
# 7. Submit for quotes!
```

---

## 📖 Related Documentation

- `TESTING_GUIDE.md` - Complete testing instructions
- `../web_app/AI_MEDICAL_INTEGRATION.md` - Technical integration details
- `../web_app/QUICKSTART_INSURANCE.md` - Quick start guide

---

## ⚠️ Important Notes

1. **These are fictional patients** - Use only for testing
2. **Not real medical data** - Generated for demonstration
3. **HIPAA compliant** - No actual patient information
4. **Processing time** - Text files: 10-30 seconds, PDFs: 30-90 seconds
5. **File size limit** - Maximum 16MB per file

---

**Ready to test!** 🧪  
Start with `sample_medical_report_1.txt` for best results.

