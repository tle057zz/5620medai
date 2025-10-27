# ⚡ Quick Testing Guide - 5 Minutes to Test Everything!

**Goal:** Test the AI Medical Integration in 5 minutes

---

## 🚀 Step 1: Start the Server (30 seconds)

```bash
cd web_app
python3 app.py
```

**Expected output:**
```
🏥 Clinical AI Assistance System - Web Application
🌐 Server starting at: http://127.0.0.1:5000
```

---

## 🔐 Step 2: Login (10 seconds)

1. Open browser: `http://127.0.0.1:5000`
2. Login credentials:
   - **Username:** `patient_john`
   - **Password:** `password123`

---

## 📝 Step 3: Request Quote (10 seconds)

1. Click the big blue **"Request Quote"** button
2. You'll see the insurance quote form

---

## 📤 Step 4: Upload Document (2 minutes)

### Option A: Quick Test (No AI Pipeline)
**Skip document upload**, fill form manually:
- Conditions: `diabetes, hypertension`
- Medications: `Metformin, Lisinopril`
- BMI: `28.5`
- Income: `65000`
- Check both consent boxes
- Click **"Generate Insurance Quotes"**

**Time:** 30 seconds  
**Expected:** 3-5 insurance quotes displayed

---

### Option B: Full AI Test (With Document)
1. Scroll to **"Upload Medical Document"** section
2. Click **"Choose File"**
3. Navigate to: `samples/sample_medical_report_1.txt`
4. Click **"Generate Insurance Quotes"**
5. Wait 30-60 seconds for AI processing

**Expected output in console:**
```
✓ Processing uploaded document: sample_medical_report_1.pdf
Step 1: Running OCR...
Step 2: Sectionizing document...
Step 3: Extracting medical entities...
✓ Extracted: ['diabetes', 'hypertension'], ['Metformin', 'Lisinopril']
```

6. After processing, click **"Auto-Fill Form"** button
7. Review pre-filled fields
8. Submit form

**Time:** 2 minutes  
**Expected:** Form auto-filled + insurance quotes

---

## 🎯 Step 5: Explore Features (2 minutes)

On the quotes page, try:

✅ **Click "See Cost Breakdown"** → See detailed cost projections  
✅ **Click "Compare Quotes"** → Side-by-side comparison  
✅ **Click "Add to Favorites"** → Save preferred plans  
✅ **Click "Export as PDF"** → Download HTML report  
✅ **Click "Share with Doctor"** → Request doctor review  

---

## 🧪 Step 6: Test Doctor Review (1 minute)

1. Logout (top right)
2. Login as doctor:
   - **Username:** `doctor_smith`
   - **Password:** `password123`
3. Click **"Pending Reviews"** button
4. Click **"Review"** on the shared request
5. Add notes and approve

---

## ✅ Success Checklist

After testing, you should have seen:

- [x] Login successful
- [x] Form loads properly
- [x] Document upload works (if tested)
- [x] AI extraction works (if tested)
- [x] Auto-fill populates fields (if tested)
- [x] Insurance quotes generated
- [x] Quotes ranked by score
- [x] Cost breakdown displays
- [x] Comparison table works
- [x] Doctor review works
- [x] No errors in console

---

## 🐛 Common Issues

### "command not found: python"
```bash
python3 app.py  # Use python3 instead
```

### "Module not found" errors
```bash
cd ..
pip install -r web_app/requirements_flask.txt
```

### Document processing takes too long
- Normal for first run (loading models)
- Subsequent uploads faster
- Text files faster than PDFs

---

## 📊 Expected Results Summary

| Test | Expected Result |
|------|----------------|
| Manual Entry | 3-5 quotes, ~5 seconds |
| Document Upload | Auto-filled form, ~60 seconds |
| Enhanced Risk | HIGH risk detected for drug interactions |
| Cost Breakdown | 4 scenarios with charts |
| Comparison | Side-by-side table with winners |
| Doctor Review | Review form with patient data |

---

## 🎉 That's it!

You've just tested:
- ✅ Complete insurance quote workflow
- ✅ AI medical document processing
- ✅ Auto-fill from extracted data
- ✅ Enhanced risk assessment
- ✅ All extension features
- ✅ Doctor review workflow

**Total Time:** 5 minutes

---

## 📚 Next Steps

For detailed testing:
- Read: `samples/TESTING_GUIDE.md` (12 comprehensive test scenarios)
- Review: `web_app/AI_MEDICAL_INTEGRATION.md` (technical details)
- Check: `samples/README.md` (sample file descriptions)

---

**Happy Testing!** 🧪✨

