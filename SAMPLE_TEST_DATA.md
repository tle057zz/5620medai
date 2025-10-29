# 📋 Sample Test Data for Demo

## 🎯 Use This Data to Test Insurance Quote

**URL**: http://127.0.0.1:5000/insurance/request-quote

**Important**: DON'T upload a document - fill the form manually!

---

## 📝 Test Scenario 1: Diabetic Patient (High Risk)

### Current Health Data
```
BMI: 32.5
Blood Pressure: 145/95
Cholesterol: 240 mg/dL
Glucose: 185 mg/dL
Smoking Status: Never
Alcohol Consumption: Occasional
```

### Current Conditions
```
Type 2 Diabetes Mellitus, Essential Hypertension, Hyperlipidemia, Obesity
```

### Current Medications
```
Metformin 1000mg twice daily, Lisinopril 10mg daily, Atorvastatin 20mg daily
```

### Past Medical History
```
Type 2 Diabetes diagnosed 2020, Hypertension since 2019, Family history of heart disease
```

### Surgeries
```
None
```

### Family History
```
Father: Heart disease, diabetes; Mother: Hypertension
```

### Income Details
```
Annual Income: $65,000
Employment Status: Employed
Occupation: Office Worker
Dependents: 2
```

**Expected Result**: 4-5 quotes, higher premiums due to chronic conditions

---

## 📝 Test Scenario 2: Healthy Young Adult (Low Risk)

### Current Health Data
```
BMI: 23.5
Blood Pressure: 118/75
Cholesterol: 170 mg/dL
Glucose: 90 mg/dL
Smoking Status: Never
Alcohol Consumption: Never
```

### Current Conditions
```
None
```

### Current Medications
```
Multivitamin daily
```

### Past Medical History
```
No chronic conditions
```

### Income Details
```
Annual Income: $85,000
Employment Status: Employed
Dependents: 0
```

**Expected Result**: 5+ quotes, lower premiums, best suitability scores

---

## 📝 Test Scenario 3: Senior with Multiple Conditions (Very High Risk)

### Current Health Data
```
BMI: 29.0
Blood Pressure: 150/92
Cholesterol: 260 mg/dL
Glucose: 195 mg/dL
Smoking Status: Former (quit 5 years ago)
Alcohol Consumption: Never
```

### Current Conditions
```
Type 2 Diabetes, Hypertension, Chronic Kidney Disease Stage 3, Coronary Artery Disease, COPD
```

### Current Medications
```
Metformin 1000mg, Lisinopril 20mg, Atorvastatin 40mg, Aspirin 81mg, Albuterol inhaler, Furosemide 40mg
```

### Past Medical History
```
MI (heart attack) 2018, Diabetes since 2015, COPD since 2017
```

### Surgeries
```
Coronary angioplasty with stent placement 2018
```

### Hospitalizations
```
Heart attack 2018, Pneumonia 2019, COVID-19 2021
```

### Income Details
```
Annual Income: $45,000
Employment Status: Retired
Dependents: 1
```

**Expected Result**: Fewer quotes, higher premiums, may trigger "no suitable options" or human advisor recommendation

---

## 💰 Financial Assistance Test Data

After getting quotes, click "Get Financial Assistance" and use:

### Scenario A: Low Income with Benefits
```
Annual Income: $35,000
Household Size: 4
State: NSW
Employment: Employed
Dependents: 2
Has Medicare Card: ✓
Has Health Care Card: ✓
Pensioner: ✗
Student: ✗
Credit Score: 650
Monthly Premium: $400
```

**Expected**: 40-50% subsidy, Affordability Score: 60-70

### Scenario B: Middle Income
```
Annual Income: $75,000
Household Size: 2
Has Medicare Card: ✓
Has Health Care Card: ✗
Monthly Premium: $350
```

**Expected**: 15-25% subsidy, Affordability Score: 75-85

### Scenario C: Student
```
Annual Income: $25,000
Household Size: 1
Student: ✓
Monthly Premium: $250
```

**Expected**: 20-30% subsidy, Affordability Score: 50-60

---

## 🎬 Quick Demo Script

### 5-Minute Insurance + Financial Assistance Demo:

1. **Login**: `patient1` / `password123`

2. **Request Insurance Quote**:
   - Use **Test Scenario 1** (Diabetic Patient)
   - Fill form (skip document upload!)
   - Click "Generate Insurance Quotes"
   - **Result**: See 4-5 ranked quotes

3. **View Quote Details**:
   - Click "See Details" on top quote
   - Show premium, coverage, exclusions

4. **Get Financial Assistance**:
   - Click yellow "Get Financial Assistance" button
   - Use **Scenario A** (Low Income)
   - Click "Calculate Subsidies"
   - **Result**: See $160/month savings!

5. **Show Affordability**:
   - Point out affordability gauge
   - Show breakdown of subsidies
   - Explain assistance options

**Total Time**: 5 minutes
**Impact**: High - shows complete patient journey

---

## ✅ Checklist for Demo

Before demo:
- [ ] Server running at http://127.0.0.1:5000
- [ ] Can login as patient1
- [ ] Have this test data ready
- [ ] Know to SKIP document upload
- [ ] Explain AI is simulated (OK for demo)

During demo:
- [ ] Show manual form input
- [ ] Generate quotes successfully
- [ ] Show financial assistance
- [ ] Explain subsidy calculator
- [ ] Show affordability score

After demo:
- [ ] Explain AI would extract from documents
- [ ] All backend logic still works
- [ ] Real deployment would have full AI

---

## 🎯 Key Points to Emphasize

1. **"The AI risk assessment engine analyzes your health data..."**
   - (It's simulated but logic is real)

2. **"Quotes are ranked by suitability, cost, and coverage..."**
   - (Algorithm works, just without document processing)

3. **"Financial assistance calculator checks 5 subsidy types..."**
   - (This is REAL - full working feature!)

4. **"Affordability scoring helps patients understand costs..."**
   - (100% functional!)

---

**Use this data and your demo will be perfect! 🚀**

