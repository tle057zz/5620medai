# 🧪 Complete Testing Guide - Insurance Quote Feature

**Last Updated:** October 27, 2025  
**Feature:** Request Insurance Quote with AI Medical Integration

---

## 📋 Prerequisites

### 1. Install Dependencies

```bash
cd /path/to/5620medai

# Install web app dependencies
pip install flask flask-login flask-wtf

# Install AI medical pipeline dependencies  
pip install pdfplumber pytesseract pdf2image Pillow
pip install spacy scispacy medspacy
pip install torch sentence-transformers
pip install pandas numpy

# Download SpaCy models
python -m spacy download en_core_sci_sm
python -m spacy download en_ner_bc5cdr_md

# Optional: For PDF generation
pip install reportlab
```

### 2. Verify Installation

```bash
# Check if modules are available
python -c "import flask; import spacy; import pdfplumber; print('✅ All dependencies installed!')"
```

---

## 🚀 Starting the Application

### Method 1: Direct Python

```bash
cd web_app
python3 app.py
```

### Method 2: Using Shell Script (if available)

```bash
cd web_app
./start_web.sh
```

### Expected Output:

```
============================================================
🏥 Clinical AI Assistance System - Web Application
============================================================

📋 Example Users:
------------------------------------------------------------
  Role: PATIENT    | Username: patient_john   | Password: password123
  Role: DOCTOR     | Username: doctor_smith   | Password: password123
  Role: ADMIN      | Username: admin          | Password: password123
------------------------------------------------------------

🌐 Server starting at: http://127.0.0.1:5000
Press CTRL+C to stop the server
```

---

## 🧪 Test Scenarios

### **TEST 1: Basic Manual Entry (Without Document Upload)**

**Purpose:** Test original functionality without AI medical pipeline

**Steps:**
1. Open browser: `http://127.0.0.1:5000`
2. Login:
   - Username: `patient_john`
   - Password: `password123`
3. Click: **"Request Quote"** button on dashboard
4. Fill form manually:
   - **Health Conditions:** `diabetes, hypertension`
   - **Medications:** `Metformin, Lisinopril, Atorvastatin`
   - **BMI:** `28.5`
   - **Blood Pressure:** `145/92`
   - **Smoking Status:** `Never Smoked`
   - **Annual Income:** `65000`
   - **Employment:** `Full-Time Employment`
5. Check both consent boxes
6. Click: **"Generate Insurance Quotes"**

**Expected Results:**
- ✅ Form submits successfully
- ✅ Redirects to quotes page
- ✅ Shows 3-5 ranked insurance quotes
- ✅ Each quote has scores (suitability, cost, coverage)
- ✅ Risk score calculated based on conditions
- ✅ Console shows: Basic risk assessment

**Success Indicators:**
- Overall score visible for each quote
- Top-ranked quote displayed first
- Download and Compare buttons visible

---

### **TEST 2: Document Upload & AI Processing**

**Purpose:** Test AI medical pipeline integration

**Preparation:**
```bash
# Generate sample PDFs (if ReportLab installed)
cd samples
python3 generate_sample_pdfs.py

# Or use existing text files:
# - sample_medical_report_1.txt
# - sample_prescription.txt
# - sample_lab_results.txt
```

**Steps:**
1. Login as `patient_john`
2. Navigate to: **Request Insurance Quote**
3. Locate: **"Upload Medical Document (Optional)"** section
4. Click: **"Choose File"**
5. Select: `samples/sample_medical_report_1.pdf` (or .txt)
6. Click: **"Generate Insurance Quotes"** (form submission processes document)
7. Wait for processing (5-30 seconds depending on document)

**Expected Results:**
- ✅ Success message: "✓ Document processed! Extracted X conditions and Y medications."
- ✅ Console output shows:
  ```
  ✓ Processing uploaded document: sample_medical_report_1.pdf
  Step 1: Running OCR...
  Step 2: Sectionizing document...
  Step 3: Extracting medical entities...
  Step 4: Linking entities to medical ontologies...
  Step 5: Parsing extracted data...
  ✓ Extracted: ['diabetes', 'hypertension'], ['Metformin', 'Lisinopril']
  ```
- ✅ Green alert banner appears with "Auto-Fill Form" button
- ✅ Extracted data stored in session

**Success Indicators:**
- No errors during OCR → NER → Entity Linking pipeline
- Extracted conditions and medications shown in alert
- Form still editable for user review

---

### **TEST 3: Auto-Fill from Extracted Data**

**Purpose:** Test auto-population of form fields

**Prerequisites:** Complete TEST 2 first

**Steps:**
1. After successful document processing (see green banner)
2. Click: **"Auto-Fill Form"** button in the green alert
3. Review pre-filled fields

**Expected Results:**
- ✅ **Current Conditions** field populated: `diabetes, hypertension, hyperlipidemia`
- ✅ **Current Medications** field populated: `Metformin, Lisinopril, Atorvastatin, Aspirin`
- ✅ **BMI** field populated: `30.1` (if extracted)
- ✅ **Blood Pressure** field populated: `145/92` (if extracted)
- ✅ **Glucose** field populated: `165 mg/dL` (if extracted)
- ✅ Flash message: "✓ Form pre-filled with data from your medical document!"

**Success Indicators:**
- Fields contain comma-separated values
- User can still edit all fields
- Original manual entry still works

---

### **TEST 4: Enhanced Risk Assessment**

**Purpose:** Test Safety Checker integration for risk scoring

**Steps:**
1. Fill form with high-risk combination:
   - **Conditions:** `diabetes, chronic kidney disease`
   - **Medications:** `warfarin, ibuprofen`
   - **Income:** `50000`
2. Submit form

**Expected Results:**
- ✅ Console output shows:
  ```
  ✓ Enhanced Safety Assessment: HIGH RISK - 2 factors detected
  ```
- ✅ Risk factors detected:
  - Comorbidity: Diabetes + CKD
  - Drug interaction: Anticoagulant (warfarin) + NSAID (ibuprofen)
- ✅ Risk score increased by 1.5x (HIGH severity)
- ✅ Higher-tier insurance plans recommended
- ✅ Quotes emphasize comprehensive coverage needs

**Success Indicators:**
- WellCare Comprehensive or PremiumCare Gold ranked higher
- Budget plans excluded or ranked lower
- Rationale mentions medical monitoring requirements

---

### **TEST 5: Cost Breakdown Feature**

**Purpose:** Test detailed cost simulation

**Steps:**
1. Generate quotes (any method)
2. On quotes page, click: **"See Cost Breakdown"** on any quote
3. Navigate through scenario tabs

**Expected Results:**
- ✅ Redirects to cost breakdown page
- ✅ Shows 4 tabs: Minimal, Typical, Heavy, Catastrophic
- ✅ Each tab shows:
  - Total annual cost
  - Annual premium
  - Estimated out-of-pocket
  - Usage details table (doctor visits, ER, prescriptions, etc.)
- ✅ Chart.js bar chart compares all scenarios
- ✅ Cost projections realistic

**Success Indicators:**
- Chart renders properly
- Switching tabs updates content
- Costs increase from Minimal → Catastrophic

---

### **TEST 6: Compare Quotes**

**Purpose:** Test side-by-side comparison feature

**Steps:**
1. Generate quotes
2. Click: **"Compare Quotes"** button
3. Review comparison table

**Expected Results:**
- ✅ Side-by-side comparison table
- ✅ Shows all metrics: scores, costs, coverage
- ✅ Trophy icons (🏆) mark best values
- ✅ Green highlights for winners
- ✅ Checkmarks (✓) for covered items
- ✅ X marks for excluded items
- ✅ Legend at bottom

**Success Indicators:**
- Table scrolls horizontally if needed
- All quotes visible
- Icons render properly

---

### **TEST 7: Doctor Review Workflow**

**Purpose:** Test Extension Path 1 from use case

**Steps:**

**As Patient:**
1. Login: `patient_john` / `password123`
2. Generate quotes
3. Click: **"Share with Doctor"** button
4. Confirm action

**As Doctor:**
1. Logout
2. Login: `doctor_smith` / `password123`
3. Click: **"Pending Reviews"** button on doctor dashboard
4. Click: **"Review"** on pending request
5. Review AI recommendations
6. Enter doctor notes: `"Patient needs comprehensive coverage for chronic conditions. Recommend WellCare plan."`
7. Optional: Check "Override ranking"
8. Click: **"Approve & Complete Review"**

**Expected Results:**
- ✅ Patient sees "Shared with Doctor" status
- ✅ Doctor sees request in queue
- ✅ Doctor review form shows patient profile
- ✅ Doctor review form shows AI-generated quotes
- ✅ Doctor can add notes
- ✅ Status changes to "completed" after review
- ✅ Doctor notes saved to request

**Success Indicators:**
- Request appears in doctor's pending queue
- All patient data visible to doctor
- Review persists after submission

---

### **TEST 8: PDF Export**

**Purpose:** Test PDF download functionality

**Steps:**
1. Generate quotes
2. Click: **"Export as PDF"** button
3. Save file

**Expected Results:**
- ✅ HTML file downloads (named `insurance_quotes_<request_id>.html`)
- ✅ File contains:
  - Request summary
  - Patient profile
  - All quotes with scores
  - Rationales
  - Coverage details
- ✅ Professional formatting
- ✅ Can be opened in browser or converted to PDF

**Success Indicators:**
- File downloads successfully
- Opens in browser
- All content visible
- Print-ready format

---

### **TEST 9: Favorites System**

**Purpose:** Test save/favorite functionality

**Steps:**
1. Generate quotes
2. Click: **"Add to Favorites"** (star button) on a quote
3. Observe button change
4. Click again to unfavorite

**Expected Results:**
- ✅ Button changes color (yellow warning → green success)
- ✅ Text changes: "Add to Favorites" → "Unfavorite"
- ✅ AJAX request succeeds
- ✅ No page reload
- ✅ Favorite status persists

**Success Indicators:**
- Button toggles correctly
- No console errors
- Favorites stored in quote request

---

### **TEST 10: Quote History**

**Purpose:** Test request tracking

**Steps:**
1. Generate multiple quote requests (2-3)
2. Click: **"View History"** button
3. Review table

**Expected Results:**
- ✅ All past requests listed
- ✅ Table shows:
  - Request ID
  - Date submitted
  - Status (completed/processing)
  - Number of quotes
  - Income
  - Health conditions count
- ✅ Action buttons: View, Download
- ✅ Clicking "View" opens quotes
- ✅ Clicking "Download" exports JSON

**Success Indicators:**
- All requests visible
- Status badges correct
- Links functional

---

### **TEST 11: No Results Scenario**

**Purpose:** Test failure path 6a.2 from use case

**Steps:**
1. Fill form with extreme high-risk profile:
   - **Conditions:** `cancer, heart failure, kidney failure, liver disease, stroke`
   - **Medications:** `many high-cost medications`
   - **Income:** `15000` (very low)
2. Submit

**Expected Results:**
- ✅ Redirects to "No Suitable Products Found" page
- ✅ Shows warning message
- ✅ Displays request summary
- ✅ Offers options:
  - Contact human advisor (email link)
  - Update information & retry
  - Back to dashboard
- ✅ Request still saved with ID

**Success Indicators:**
- No crash or error
- Graceful handling
- User has clear next steps

---

### **TEST 12: Fallback (No AI Medical Modules)**

**Purpose:** Test graceful degradation if ai_medical not available

**Simulation:**
```bash
# Temporarily rename ai_medical folder
cd /path/to/5620medai
mv ai_medical ai_medical_backup
```

**Steps:**
1. Restart server
2. Try uploading document
3. Try manual entry

**Expected Results:**
- ✅ Server starts normally
- ✅ Warning in console: "AI Medical modules not available"
- ✅ Document upload field shows but may have warning
- ✅ Manual entry works perfectly
- ✅ Basic risk assessment (no enhancement)
- ✅ Quotes still generated

**Restore:**
```bash
mv ai_medical_backup ai_medical
```

**Success Indicators:**
- No crashes
- Feature still usable
- Clear error messages

---

## 🔍 Testing Checklist

### Pre-Flight Check:
- [ ] All dependencies installed
- [ ] SpaCy models downloaded
- [ ] Sample files generated
- [ ] Server starts without errors

### Core Features:
- [ ] Login works (patient, doctor, admin)
- [ ] Manual form entry works
- [ ] Form validation works
- [ ] Consent required
- [ ] Quote generation works
- [ ] Quotes displayed correctly

### AI Medical Integration:
- [ ] Document upload works
- [ ] OCR extraction works
- [ ] NER entity extraction works
- [ ] Entity linking works
- [ ] Auto-fill works
- [ ] Enhanced risk assessment works

### Extension Features:
- [ ] Cost breakdown works
- [ ] Comparison works
- [ ] Doctor review works
- [ ] PDF export works
- [ ] Favorites work
- [ ] History tracking works

### Error Handling:
- [ ] Invalid file rejected
- [ ] Missing fields caught
- [ ] No results handled gracefully
- [ ] Fallback mode works

---

## 📊 Performance Expectations

| Feature | Expected Time |
|---------|--------------|
| Form load | < 1 second |
| Document upload | Immediate |
| OCR processing | 5-30 seconds |
| NER extraction | 10-20 seconds |
| Entity linking | 10-30 seconds |
| Quote generation | 1-2 seconds |
| Total (with document) | 30-90 seconds |
| Total (manual entry) | 2-5 seconds |

---

## 🐛 Common Issues & Solutions

### Issue 1: "command not found: python"
**Solution:**
```bash
python3 app.py  # Use python3 instead of python
```

### Issue 2: OCR fails with "pytesseract not found"
**Solution:**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Verify
tesseract --version
```

### Issue 3: SpaCy model not found
**Solution:**
```bash
python3 -m spacy download en_core_sci_sm
python3 -m spacy download en_ner_bc5cdr_md
```

### Issue 4: File upload size limit exceeded
**Solution:** Files over 16MB are rejected. Use smaller documents or increase limit in `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

### Issue 5: "No module named 'reportlab'"
**Solution:** For PDF generation:
```bash
pip install reportlab
```

---

## 📝 Sample Test Data

Use these values for consistent testing:

### Low-Risk Profile:
- Conditions: (none)
- Medications: (none)
- BMI: 22.5
- Income: $60,000
- Expected: Budget Shield Basic

### Moderate-Risk Profile:
- Conditions: diabetes, hypertension
- Medications: Metformin, Lisinopril
- BMI: 28.5
- Income: $75,000
- Expected: WellCare Comprehensive

### High-Risk Profile:
- Conditions: cancer, heart disease, diabetes
- Medications: Chemotherapy, Insulin, Aspirin
- BMI: 24.0
- Income: $120,000
- Expected: PremiumCare Gold

---

## 🎯 Success Criteria

The feature is working correctly if:

✅ **All 12 test scenarios pass**  
✅ **No console errors**  
✅ **Forms submit successfully**  
✅ **Quotes display correctly**  
✅ **AI pipeline processes documents**  
✅ **Auto-fill populates fields**  
✅ **Enhanced risk assessment runs**  
✅ **All extension features work**  
✅ **Error handling graceful**  
✅ **Performance acceptable**  

---

## 📞 Support

If tests fail:
1. Check console for errors
2. Verify all dependencies installed
3. Check sample files exist
4. Review logs in terminal
5. Consult `AI_MEDICAL_INTEGRATION.md`

---

**Happy Testing!** 🧪🎉

