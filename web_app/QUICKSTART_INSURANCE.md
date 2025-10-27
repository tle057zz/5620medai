# 🚀 Quick Start: Insurance Quote Feature

## Overview
This guide will help you quickly test the new **Request Insurance Quote** feature.

---

## Prerequisites

1. **Flask dependencies installed:**
   ```bash
   cd web_app
   pip install -r requirements_flask.txt
   ```

2. **Project structure:**
   ```
   web_app/
   ├── app.py (updated with insurance routes)
   ├── forms.py (updated with InsuranceQuoteForm)
   ├── insurance_models.py (NEW)
   ├── insurance_engine.py (NEW)
   └── templates/
       ├── insurance_quote_form.html (NEW)
       ├── insurance_quotes_display.html (NEW)
       ├── insurance_no_results.html (NEW)
       └── insurance_history.html (NEW)
   ```

---

## Start the Application

```bash
cd web_app
python app.py
```

Expected output:
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
```

---

## Test Scenarios

### 🟢 Scenario 1: Healthy Low-Risk User (Budget Plan Match)

1. **Login:** `patient_john` / `password123`

2. **Navigate:** Click "Request Quote" button on dashboard

3. **Fill Health Data:**
   - Current Conditions: *(leave empty)*
   - Current Medications: *(leave empty)*
   - BMI: `22.5`
   - Blood Pressure: `120/80`
   - Smoking Status: `Never Smoked`
   - Alcohol: `None`

4. **Fill Medical History:**
   - Past Conditions: *(leave empty)*
   - Surgeries: *(leave empty)*
   - Hospitalizations: *(leave empty)*
   - Family History: *(leave empty)*

5. **Fill Income Details:**
   - Annual Income: `40000`
   - Employment Status: `Full-Time Employment`
   - Occupation: `Teacher`
   - Dependents: `0`

6. **Consent:**
   - ✅ Check both consent boxes

7. **Submit**

**Expected Result:**
- ✅ 4-5 insurance quotes displayed
- ✅ Top match: Budget Shield Basic or MediCare Essential (affordable options)
- ✅ High cost scores (affordable for income)
- ✅ Rationale mentions low-risk profile

---

### 🟡 Scenario 2: Moderate-Risk with Chronic Conditions

1. **Login:** `patient_john` / `password123`

2. **Navigate:** Insurance → Request Quote

3. **Fill Health Data:**
   - Current Conditions: `diabetes, hypertension`
   - Current Medications: `Metformin, Lisinopril`
   - BMI: `28.5`
   - Blood Pressure: `140/90`
   - Smoking Status: `Former Smoker`
   - Alcohol: `Occasional`

4. **Fill Medical History:**
   - Past Conditions: `High cholesterol`
   - Surgeries: *(leave empty)*
   - Hospitalizations: `2022 - Emergency`
   - Family History: `Heart disease (father)`

5. **Fill Income Details:**
   - Annual Income: `75000`
   - Employment Status: `Full-Time Employment`
   - Occupation: `Software Engineer`
   - Dependents: `2`

6. **Consent:** ✅ Check both

7. **Submit**

**Expected Result:**
- ✅ 3-4 insurance quotes
- ✅ Top match: WellCare Comprehensive (includes chronic disease management)
- ✅ Moderate suitability scores
- ✅ Rationale mentions diabetes/hypertension management
- ✅ Risk score: ~60-70

---

### 🔴 Scenario 3: High-Risk Cancer Patient

1. **Login:** `patient_john` / `password123`

2. **Fill Health Data:**
   - Current Conditions: `cancer, heart disease, diabetes`
   - Current Medications: `Chemotherapy drugs, Insulin, Aspirin`
   - BMI: `24.0`
   - Smoking Status: `Never Smoked`

3. **Fill Medical History:**
   - Past Conditions: `Hypertension`
   - Surgeries: `2023 - Tumor removal`
   - Hospitalizations: `2023 - 2 weeks`

4. **Fill Income Details:**
   - Annual Income: `120000`
   - Employment Status: `Self-Employed`
   - Occupation: `Business Owner`

5. **Submit**

**Expected Result:**
- ✅ 1-3 insurance quotes (many plans excluded)
- ✅ Top match: PremiumCare Gold or WellCare Comprehensive
- ✅ High coverage amounts ($750K+)
- ✅ Rationale mentions cancer treatment coverage
- ✅ Risk score: ~80-95

---

### ⚠️ Scenario 4: No Suitable Products (Very High Risk + Low Income)

1. **Fill Health Data:**
   - Current Conditions: `cancer, heart disease, kidney disease, COPD`
   - Smoking Status: `Current Smoker`
   - BMI: `18.0` (underweight)

2. **Fill Income Details:**
   - Annual Income: `15000`
   - Employment Status: `Unemployed`

3. **Submit**

**Expected Result:**
- ⚠️ Redirected to "No Suitable Products Found" page
- ✅ Message: "No suitable insurance products matching your profile"
- ✅ Request ID saved
- ✅ Options: Contact human advisor, retry, back to dashboard

---

## Feature Navigation

### From Patient Dashboard:
1. Main card: "Insurance Quote Service (NEW)" → Click "Request Quote"
2. After submission → View ranked quotes
3. Dashboard → View History

### From Doctor Dashboard:
1. Card: "Insurance Quotes (NEW)" → Click "Request Quote"
2. Help patients generate quotes

### Quote History:
1. Navigate to `/insurance/history`
2. View all past requests
3. Click "View" to see quotes
4. Click "Download" for JSON export

---

## Validation Testing

### Test Missing Required Fields:

1. **Skip annual income** → Should show validation error
2. **Skip employment status** → Should show validation error
3. **Uncheck consent boxes** → Should show error: "You must provide consent"

### Test Edge Cases:

1. **Very low income + expensive preference** → Should filter out expensive plans
2. **All fields empty except required** → Should still generate quotes (use defaults)
3. **Invalid BMI (100)** → Should show validation error

---

## API Endpoint Testing

### Download Quotes as JSON:
```bash
# Login first, then visit:
http://127.0.0.1:5000/insurance/download/<request_id>
```

Returns:
```json
{
  "request_id": "REQ-20251026...",
  "user_id": "1",
  "health_data": { ... },
  "quotes": [ ... ],
  "status": "completed"
}
```

---

## Verify Dashboard Integration

### Patient Dashboard:
- ✅ 4 stat cards (including "Insurance Quotes")
- ✅ New insurance card with description
- ✅ "Request Quote" button
- ✅ "View History" button

### Doctor Dashboard:
- ✅ 3 action cards (including "Insurance Quotes (NEW)")
- ✅ Insurance features listed
- ✅ "Request Quote" button

---

## Troubleshooting

### Issue: ModuleNotFoundError
```bash
# Install missing dependencies
cd web_app
pip install flask flask-login flask-wtf wtforms
```

### Issue: Template not found
```bash
# Verify template files exist
ls templates/insurance_*.html
# Should show: insurance_quote_form.html, insurance_quotes_display.html, etc.
```

### Issue: No quotes generated
- Check console for error messages
- Verify `insurance_engine.py` is in web_app/ directory
- Ensure all consent boxes are checked

### Issue: Permission denied to view quotes
- Ensure you're logged in
- Verify you're viewing your own quotes (or logged in as admin)

---

## Success Indicators

✅ Form loads without errors  
✅ Validation works correctly  
✅ AI processes in < 2 seconds  
✅ Quotes display with scores  
✅ Rationales are coherent  
✅ Download works  
✅ History shows all requests  
✅ Dashboard cards appear  

---

## Next Steps After Testing

1. ✅ **Verify all 4 scenarios work**
2. 📝 **Document any bugs**
3. 🎨 **Customize insurance products** (optional)
4. 🔐 **Add database persistence** (production)
5. 🌐 **Integrate real insurance APIs** (future)

---

## Demo Script (5 minutes)

1. **Login** (30 sec)
2. **Navigate to insurance feature from dashboard** (15 sec)
3. **Fill form with Scenario 2 data** (2 min)
4. **Submit and show results** (30 sec)
5. **Explain scores and rationale** (1 min)
6. **Download JSON** (15 sec)
7. **Show history page** (30 sec)

---

**Ready to test? Start the server and follow Scenario 1!** 🚀

