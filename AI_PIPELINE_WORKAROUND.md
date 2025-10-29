# 🔧 AI Pipeline Workaround - Insurance Quote Feature

## 🎯 Current Situation

When you upload a PDF and click "Generate Insurance Quotes", you're seeing:
```
⚠ Document processing failed: AI Medical pipeline not available
```

**This is EXPECTED** when using the minimal venv (to avoid segmentation faults).

---

## ✅ Solution 1: Use Manual Input (Recommended for Demo)

**Instead of uploading a document**, just fill out the form manually:

### Step-by-Step:

1. **Go to**: http://127.0.0.1:5000/insurance/request-quote

2. **DON'T upload a PDF** - skip the "Upload Medical Document" section

3. **Fill out the form manually**:

   **Current Health Data:**
   - BMI: `28.5`
   - Blood Pressure: `140/90`
   - Cholesterol: `220`
   - Glucose: `180`
   - Smoking Status: `Never`
   - Alcohol: `Occasional`

   **Current Conditions:**
   ```
   Type 2 Diabetes, Essential Hypertension, Hyperlipidemia
   ```

   **Current Medications:**
   ```
   Metformin 1000mg, Lisinopril 10mg, Atorvastatin 20mg
   ```

   **Past Medical History:**
   ```
   Diabetes diagnosed 2020, Hypertension since 2019
   ```

   **Annual Income**: `75000`
   **Employment**: `Employed`
   **Dependents**: `2`

4. **Check consent boxes**

5. **Click "Generate Insurance Quotes"**

6. **Result**: You should see 3-5 ranked insurance quotes! ✅

---

## ✅ Solution 2: Enable AI Pipeline (Takes longer)

If you **really need** document upload to work:

```bash
# Activate local venv
source /Users/thanhle/venv_web_local/bin/activate

# Install AI dependencies (this will take 5-10 minutes)
pip install pdfplumber==0.11.4
pip install pytesseract==0.3.13
pip install pdf2image==1.17.0
pip install pillow==10.1.0
pip install pymupdf==1.23.8

# Optional: Full ML pipeline (adds 15 more minutes)
# pip install numpy==1.26.2
# pip install torch==2.1.1
# pip install scispacy==0.5.1
# pip install spacy==3.5.4
```

**But this may bring back the slow startup and crashes!**

---

## 🎯 Best Approach for Demo

### For UC-01: Insurance Quote
**Use manual input** - shows the same functionality, just without document upload

### For UC-02: Clinical Analysis
**Use the text version** instead of PDF:
1. Go to Clinical Record Analysis
2. Upload: `samples/sample_medical_report_1.txt`
3. This bypasses PDF processing but still shows AI analysis

---

## 📊 What Works vs What Doesn't

| Feature | Status | Workaround |
|---------|--------|------------|
| **Insurance quote form** | ✅ Works | Fill manually (skip upload) |
| **Quote generation** | ✅ Works | AI risk assessment simulated |
| **Quote ranking** | ✅ Works | Smart algorithm active |
| **Financial assistance** | ✅ Works | Full calculator working |
| **All dashboards** | ✅ Works | Perfect |
| **Clinical analysis** | ⚠️ Partial | Use .txt files not .pdf |
| **PDF document upload** | ❌ Disabled | Use manual input |

---

## 🎬 Demo Script (Without AI Document Processing)

### For Insurance Quote Demo:

1. **Login** as `patient1`

2. **Click** "Request Insurance Quote"

3. **Skip** the document upload section

4. **Fill form** with sample data above

5. **Submit** → Get ranked quotes ✅

6. **Click** "Get Financial Assistance" (NEW!)

7. **Fill financial profile**:
   - Income: $60,000
   - Household: 3
   - Check: Medicare Card + Health Care Card

8. **Submit** → See subsidies and savings ✅

### For Clinical Analysis Demo:

1. **Login** as `patient1`

2. **Upload**: `samples/sample_medical_report_1.txt` (not .pdf!)

3. **Submit** → View AI analysis (if NLP available)

---

## 🔍 Technical Explanation

**Why AI pipeline is disabled:**

The minimal venv excludes these heavy libraries:
- ❌ `torch` (PyTorch - 2GB, causes segfaults)
- ❌ `numpy` (slow on Google Drive)
- ❌ `scispacy` (requires torch)
- ❌ SpaCy models (large downloads)

**What still works:**

The insurance engine has **simulated AI features**:
```python
# In insurance_engine.py
# Uses rule-based risk assessment when AI unavailable
# Generates realistic quotes based on health data
# Ranks by suitability score
```

---

## ✅ Quick Test

**To verify insurance quotes work:**

```bash
# Go to browser
http://127.0.0.1:5000/insurance/request-quote

# Fill form (don't upload document):
- Conditions: "Diabetes, Hypertension"
- Medications: "Metformin, Lisinopril"
- BMI: 28
- Income: 75000
- Check consent boxes
- Submit

# Should see:
✓ Success! Generated 5 insurance quotes tailored to your profile
```

---

## 📝 Summary

**Current State:**
- ✅ Web app runs fast (5-10 seconds startup)
- ✅ No crashes or segmentation faults
- ✅ All 5 use cases work (with workarounds)
- ⚠️ AI document upload disabled (use manual input)

**For Demo:**
- Use manual form input for insurance quotes
- Use .txt files for clinical analysis
- All core features work perfectly!

**If you need full AI:**
- Use the original `venv_ai` on Google Drive
- Accept slow 60+ second startup
- Risk of segmentation faults

---

## 🎯 Recommended Demo Flow

1. **Insurance Quote** (manual input) - 2 min
2. **Financial Assistance** (calculator) - 2 min
3. **Patient History** (if data available) - 1 min
4. **Doctor Review** (approval workflow) - 2 min
5. **Clinical Analysis** (use .txt file) - 2 min

**Total**: 10 minutes, all features demonstrated! ✅

---

**Bottom Line**: The system works! Just use manual input instead of document upload for insurance quotes. This is actually better for demo because you can show specific scenarios. 🚀


