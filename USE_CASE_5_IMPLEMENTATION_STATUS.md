# Use Case 5 (UC-04): Financial Assistance with Loan Matching
## Implementation Status Document
**Author**: Venkatesh Badri Narayanan  
**Status**: Backend Complete (60%) - Templates Pending  
**Last Updated**: 2025-10-28

---

## 📋 Overview

UC-04 enables patients to find suitable financial assistance and loan options based on their income, household composition, and insurance needs. This extends the Insurance Quote feature with subsidy eligibility calculations and affordability assessments.

### Key Features
- ✅ Income-based subsidy calculation (Australian healthcare system)
- ✅ Multiple subsidy types (Medicare, Health Care Card, Pensioner, Student, Family)
- ✅ Affordability scoring (0-100 scale)
- ✅ Additional assistance options (payment plans, loans, charity)
- ✅ Integration with insurance quotes
- ⏳ UI templates (pending)

---

## 🏗️ Architecture

### Components Created

#### 1. **financial_assistance.py** ✅ (450+ lines)
Complete backend logic for subsidy calculation and financial assistance.

**Data Models**:
```python
- SubsidyType (Enum): ACA_PREMIUM, MEDICARE, MEDICAID, STATE_PROGRAM
- EligibilityStatus (Enum): ELIGIBLE, PARTIALLY_ELIGIBLE, NOT_ELIGIBLE
- FinancialProfile (dataclass): User's financial data (income, household, cards)
- SubsidyCalculation (dataclass): Individual subsidy with amount and rationale
- AffordabilityScore (dataclass): 0-100 score with rating and concerns
- FinancialAssistanceOption (dataclass): Loan/payment plan details
- AssistanceRecommendation (dataclass): Complete recommendation package
```

**Key Functions**:
- ✅ `calculate_subsidies()` - Calculates all applicable subsidies
- ✅ `calculate_affordability_score()` - Scores plan affordability (0-100)
- ✅ `generate_assistance_options()` - Creates payment plans/loans/charity options
- ✅ `create_assistance_recommendation()` - Generates complete recommendation
- ✅ `get_assistance_recommendation()` - Retrieves by ID

**Subsidy Types Implemented** (Australian Healthcare Context):
1. **Medicare Card Holder**: 15% premium reduction
2. **Health Care Card**: 25% premium reduction
3. **Pensioner/Senior**: 30% premium reduction
4. **Student Discount**: 20% premium reduction
5. **Family/Household Size**: 10% per additional member (capped at 30%)

**Affordability Scoring**:
- **95+ (Excellent)**: ≤5% of income
- **80+ (Good)**: 5-8% of income
- **60+ (Fair)**: 8-12% of income
- **40+ (Borderline)**: 12-15% of income
- **<40 (Poor)**: >15% of income

#### 2. **Flask Routes (app.py)** ✅ (3 new routes)

| Route | Method | Purpose |
|-------|--------|---------|
| `/financial-assistance/<request_id>` | GET | Entry from insurance quote |
| `/financial-assistance/request` | GET, POST | Assistance request form |
| `/financial-assistance/recommendation/<id>` | GET | View results |
| `/financial-assistance/export/<id>` | GET | Export as JSON |

**Security**:
- All routes require `@login_required`
- Restricted to `@role_required('patient')`
- User verification on all data access

---

## 🎯 Use Case Mapping

### Main Scenario
| Step | Description | Implementation Status |
|------|-------------|----------------------|
| 1 | Start Assistance Flow | ✅ Route: `/financial-assistance/<request_id>` |
| 2 | Check Subsidy Eligibility | ✅ `calculate_subsidies()` |
| 3 | Compare and Recommend Plans | ✅ `calculate_affordability_score()` |
| 4 | Display Cost Breakdown | ✅ Backend complete, template pending |
| 5 | Plan Selection | ⏳ To be integrated with enrollment |
| 6 | Export and Audit | ✅ JSON export available |

### Extension Path 1: Human Advisor Consultation
⏳ **Placeholder**:
- Link to request advisor
- Integration point defined
- To be connected with advisor scheduling system

### Extension Path 2: Doctor Review of Plan Selection
⏳ **Placeholder**:
- Link to share with doctor
- Integration with UC-05 (Review & Approve)
- To be connected with doctor workflow

### Extension Path 3: Family Plan Coordination
✅ **Implemented**:
- Family size subsidy calculation
- Household member discounts
- Dependent tracking

---

## 💰 Subsidy Calculation Logic

### Australian Healthcare System Subsidies

#### 1. Medicare Card Benefits
```python
if has_medicare_card or annual_income < $90,000:
    subsidy = 15% of monthly premium
    requirements = ["Valid Medicare card", "Income verification"]
```

#### 2. Health Care Card
```python
if has_health_care_card or annual_income < $60,000:
    subsidy = 25% of monthly premium
    requirements = ["Valid Health Care Card"]
```

#### 3. Pensioner Discount
```python
if pensioner:
    subsidy = 30% of monthly premium
    requirements = ["Pensioner Concession Card", "Age verification"]
```

#### 4. Student Discount
```python
if student and annual_income < $40,000:
    subsidy = 20% of monthly premium
    requirements = ["Valid student ID", "Enrollment verification"]
```

#### 5. Family Size Adjustment
```python
if household_size >= 3:
    subsidy_per_member = 10% * (household_size - 2)
    subsidy = min(subsidy_per_member, 30%)  # capped
    requirements = ["Household composition verification"]
```

### Federal Poverty Level (FPL) Calculation
```python
baseline_income = $92,000  # Australian median household income
adjusted_baseline = baseline + (household_size - 1) * $15,000
fpl_percentage = (annual_income / adjusted_baseline) * 100
```

---

## 🤝 Additional Assistance Options

### 1. Payment Plan (Always Available)
- **Provider**: Insurer Payment Plan
- **Terms**: Spread premium over bi-weekly/weekly payments
- **Eligibility**: Active insurance policy
- **Approval**: 95% likelihood
- **Interest**: 0%

### 2. Medical Loan (Low Income < $70K)
- **Provider**: Healthcare Finance Australia
- **Amount**: Full annual premium
- **Terms**: 5% APR, 12-month repayment
- **Eligibility**: Income < $70K, credit score > 600
- **Approval**: 40-70% likelihood

### 3. Charity Care (Very Low Income < $45K)
- **Provider**: Australian Healthcare Assistance Foundation
- **Amount**: 6 months coverage
- **Terms**: Partial/full premium coverage
- **Eligibility**: Income < $45K, demonstrated hardship
- **Approval**: 50% likelihood

### 4. Government Hardship Fund (< $50K + Dependents)
- **Provider**: State Government Hardship Fund
- **Amount**: 50% of annual premium
- **Terms**: State-sponsored assistance
- **Eligibility**: Household income + dependents
- **Approval**: 60% likelihood

---

## 📊 Data Flow

```
Insurance Quote Request
         ↓
Extract Financial Profile (income, dependents)
         ↓
User Confirms/Updates Financial Data
         ↓
calculate_subsidies() [5 subsidy types]
         ↓
calculate_affordability_score() [0-100]
         ↓
generate_assistance_options() [if not affordable]
         ↓
create_assistance_recommendation()
         ↓
Display Results + Export
```

---

## 🚧 Pending Implementation

### Templates Required (2-3 files needed)
1. **financial_assistance_form.html** (~200 lines) ⏳
   - Financial profile input form
   - Pre-filled from insurance quote
   - Medicare/Health Care Card checkboxes
   - Pensioner/Student status
   - Monthly premium input
   - Submit button

2. **financial_assistance_results.html** (~350 lines) ⏳
   - Original cost vs. subsidized cost comparison
   - List of applicable subsidies with details
   - Affordability score display (with color-coded rating)
   - Additional assistance options (if not affordable)
   - Cost breakdown charts
   - Next steps guidance
   - Export button

### Integration Points
1. **Insurance Quote Display** ⏳
   - Add "Get Financial Assistance" button to quote results
   - Link to `/financial-assistance/<request_id>`
   - Show subsidy eligibility preview

2. **Patient Dashboard** ⏳
   - Add "Financial Assistance" card
   - Direct access to request form
   - History of assistance calculations

---

## 🧪 Testing Scenarios

### Test 1: Medicare Card Holder
```python
profile = FinancialProfile(
    annual_income=75000,
    household_size=2,
    has_medicare_card=True
)
monthly_premium = 400
# Expected: 15% subsidy = $60/month
```

### Test 2: Low Income + Health Care Card
```python
profile = FinancialProfile(
    annual_income=45000,
    household_size=1,
    has_health_care_card=True
)
monthly_premium = 350
# Expected: 25% subsidy = $87.50/month
# Affordability: Good (6.5% of income)
```

### Test 3: Pensioner with Family
```python
profile = FinancialProfile(
    annual_income=55000,
    household_size=4,
    pensioner=True
)
monthly_premium = 600
# Expected: 30% (pensioner) + 20% (family) = 50% total
# Monthly subsidy: $300
# Affordability: Excellent
```

### Test 4: Unaffordable Plan
```python
profile = FinancialProfile(
    annual_income=35000,
    household_size=1
)
monthly_premium = 500
# Expected: Limited subsidies, high cost (17% of income)
# Affordability: Poor
# Additional options: 4 assistance programs offered
```

---

## 📈 Integration with Other Use Cases

### Dependencies
- **UC-01 (Insurance Quote)**: Source of financial data and premium costs
- **UC-05 (Review & Approve)**: Optional doctor review of plan selection
- **UC-03 (Patient History)**: Medical data for coverage adequacy assessment

### Data Flow
```
UC-01 Insurance Quote
    ↓ (provides)
Financial Profile + Selected Plan
    ↓ (triggers)
UC-04 Financial Assistance
    ↓ (calculates)
Subsidized Cost + Affordability
    ↓ (optionally)
UC-05 Doctor Review
    ↓ (confirms)
Final Plan Selection
```

---

## 🎨 UI/UX Design Notes

### Color Coding
- **Affordability Excellent (95+)**: Green
- **Affordability Good (80+)**: Light Green
- **Affordability Fair (60+)**: Yellow
- **Affordability Borderline (40+)**: Orange
- **Affordability Poor (<40)**: Red

### Key UI Elements
1. **Cost Comparison Card**: Before vs. After subsidies
2. **Subsidy List**: Each subsidy with icon, amount, requirements
3. **Affordability Gauge**: Visual 0-100 scale
4. **Assistance Options**: Cards for each additional option
5. **Next Steps Checklist**: Actionable items

---

## ✅ Completion Status

| Component | Status | Completion |
|-----------|--------|------------|
| Backend Models | ✅ Complete | 100% |
| Subsidy Calculator | ✅ Complete | 100% |
| Affordability Scorer | ✅ Complete | 100% |
| Assistance Options | ✅ Complete | 100% |
| Flask Routes | ✅ Complete | 100% |
| Templates | ⏳ Pending | 0% |
| Insurance Integration | ⏳ Partial | 30% |
| Dashboard Integration | ⏳ Pending | 0% |
| **Overall** | **🟡 Backend Complete** | **60%** |

---

## 💡 Design Decisions

### 1. **Australian Healthcare Focus**
Decision: Use Australian Medicare/Health Care Card system  
Rationale: Project context (ELEC5620 at USYD), realistic for target audience  
Alternative: US ACA system could be swapped in easily

### 2. **Multiple Stacking Subsidies**
Decision: Allow all eligible subsidies to stack  
Rationale: Maximize affordability for low-income users  
Limitation: In production, may need caps/limits

### 3. **Affordability Threshold: 15% of Income**
Decision: Plans >15% of income flagged as unaffordable  
Rationale: Industry standard for healthcare affordability  
Source: WHO and healthcare policy research

### 4. **Auto-Generated Assistance Options**
Decision: Automatically suggest loans/payment plans when unaffordable  
Rationale: Proactive UX, reduces user frustration  
Risk: May appear pushy - needs careful messaging

---

## 🔗 Related Files

**Backend**:
- `web_app/financial_assistance.py` (NEW) - Complete model logic
- `web_app/app.py` - 4 new routes (lines 1131-1296)
- `web_app/insurance_models.py` - Source of financial data

**Frontend** (pending):
- `web_app/templates/financial_assistance_form.html` (NEW)
- `web_app/templates/financial_assistance_results.html` (NEW)

**Documentation**:
- `use_cases/use_case5.html` - Original requirements
- `USE_CASES_IMPLEMENTATION_STATUS.md` - Overall progress

---

## 📝 Next Steps

### Immediate (Templates - 2-3 hours)
1. Create `financial_assistance_form.html`
2. Create `financial_assistance_results.html`
3. Add button to insurance quote display

### Short-term (Integration - 1-2 hours)
1. Update `insurance_quotes_display.html` with assistance button
2. Add financial assistance card to patient dashboard
3. Create assistance history page

### Long-term (Enhancements)
1. Add real-time subsidy API integration
2. Implement enrollment workflow
3. Add doctor review integration
4. Create advisor consultation scheduling

---

**END OF DOCUMENT**

