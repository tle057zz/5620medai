# Insurance Quote Feature - Implementation Documentation

**Feature Designer:** Chadwick Ng  
**Implementation Date:** October 26, 2025  
**Status:** ✅ Complete

---

## 📋 Overview

The **Request Insurance Quote** feature is an AI-powered system that generates personalized insurance quotes for users based on their health data, medical history, and income details. The system uses sophisticated risk assessment algorithms to match users with the most suitable insurance products, ranked by suitability, cost, and coverage.

---

## 🎯 Feature Capabilities

### User Workflow
1. **Data Collection**: User enters or updates:
   - Health data (conditions, medications, vitals)
   - Past medical history (surgeries, hospitalizations, family history)
   - Income and employment details
   - Required consent agreements

2. **AI Processing**: System orchestrates:
   - Data normalization (standardizes medical codes, units)
   - Risk assessment (calculates health risk score 0-100)
   - Eligibility filtering (applies insurance product rules)
   - Quote generation (creates personalized quotes with scores)

3. **Results Display**: System presents:
   - Ranked insurance quotes (by overall score)
   - Score breakdown (suitability, cost, coverage)
   - Detailed rationale (why each plan was recommended)
   - Coverage details and exclusions
   - Comparison tools

4. **Fallback Handling**:
   - No results → Human advisor referral
   - Missing data → Validation errors with retry
   - Save draft for later review

---

## 🏗️ Architecture

### Components Created

#### 1. **Backend Models** (`insurance_models.py`)
```
Classes:
- HealthData: Current health information
- MedicalHistory: Past medical records
- IncomeDetails: Financial information
- InsuranceProduct: Insurance plan definition
- InsuranceQuote: Generated quote with scores
- QuoteRequest: Complete request container

Functions:
- get_sample_insurance_products(): Returns 5 sample insurance plans
- save_quote_request(): Persists request to in-memory storage
- get_quote_request(): Retrieves request by ID
- get_user_quote_requests(): Gets all requests for a user
```

#### 2. **AI Engine** (`insurance_engine.py`)
```
Class: InsuranceQuoteEngine
Main Methods:
- process_quote_request(): Orchestrates entire AI pipeline
- _normalize_data(): Standardizes input data
- _assess_risk(): Calculates 0-100 risk score
- _filter_eligible_products(): Applies eligibility rules
- _generate_quote(): Creates scored quote for each product
- _calculate_suitability(): Matches plan to user needs (0-100)
- _calculate_cost_score(): Evaluates affordability (0-100)
- _calculate_coverage_score(): Assesses comprehensiveness (0-100)
- _generate_rationale(): Creates human-readable explanation

Risk Factors:
- Diabetes: 2.5x multiplier
- Heart disease: 3.0x multiplier
- Cancer: 3.5x multiplier
- Smoking: 2.0x multiplier
- High BMI: 1.5x multiplier
- Age-based risk: Progressive increase
```

#### 3. **Web Forms** (`forms.py`)
```
Class: InsuranceQuoteForm (Flask-WTF)
Sections:
- Health Data (9 fields)
- Medical History (4 fields)
- Income & Employment (4 fields)
- Consent (2 checkboxes)

Validation:
- Required fields: annual_income, employment_status, consents
- Optional fields: All health metrics (can be empty)
- Number ranges: BMI (10-60), income (≥0), dependents (0-20)
```

#### 4. **Flask Routes** (`app.py`)
```
Routes:
- GET/POST /insurance/request-quote: Main form
- GET /insurance/quotes/<request_id>: Display results
- GET /insurance/no-results/<request_id>: No matches found
- GET /insurance/history: User's quote history
- GET /insurance/download/<request_id>: Download as JSON

Access Control:
- All routes require @login_required
- Users can only view their own quotes (or admin)
```

#### 5. **Templates**
```
insurance_quote_form.html:
- Multi-section form with progress indicators
- Responsive design (Bootstrap 5)
- Field validation hints
- Consent section with privacy notice

insurance_quotes_display.html:
- Ranked quote cards with scores
- Progress bars for score visualization
- Cost breakdown (premium, deductible, OOP)
- Coverage details and exclusions
- Rationale explanations
- Action buttons (contact, compare, download)

insurance_no_results.html:
- No matches found message
- Request summary
- Human advisor contact option
- Retry with updated data option

insurance_history.html:
- Table of all user requests
- Status badges
- Quick actions (view, download)
- Empty state for new users
```

---

## 🔍 AI Risk Assessment Algorithm

### Risk Score Calculation (0-100 scale)

```
Base Risk: 20 points

Age Factors:
- Age > 60: +30 points
- Age 45-60: +20 points
- Age 30-45: +10 points

Condition Multipliers:
- Each condition multiplies by risk factor (1.5x to 3.5x)

BMI Factors:
- BMI > 30 (obese): 1.5x multiplier
- BMI > 25 (overweight): 1.2x multiplier
- BMI < 18.5 (underweight): 1.3x multiplier

Lifestyle:
- Smoking: 2.0x multiplier
- Family history: 1.3x multiplier
- 2+ hospitalizations: 1.4x multiplier

Final score capped at 100
```

### Eligibility Rules

```
Rule 1: High-risk patients (score > 70) excluded from budget plans
Rule 2: Low-income users limited to affordable plans (< $400/month)
Rule 3: Cancer patients require high coverage (≥ $500K)
Rule 4: Chronic conditions benefit from management programs
```

### Scoring System

Each quote receives three scores (0-100):

**Suitability Score:**
- Plan type match (PPO/EPO for high-risk, HMO for low-risk): +15-20
- Condition-specific coverage match: +15-25
- Income bracket alignment: +10-15

**Cost Score (inverse):**
- Annual cost as % of income:
  - < 5%: 100 points
  - 5-10%: 80 points
  - 10-15%: 60 points
  - 15-20%: 40 points
  - > 20%: 20 points

**Coverage Score:**
- Coverage amount: 5-30 points
- Number of coverage details: up to 30 points
- Exclusions penalty: -3 points each
- Low deductible: +15 points
- Low out-of-pocket max: +20 points

**Overall Score:** Average of all three scores

---

## 📊 Sample Insurance Products

The system includes 5 sample insurance products:

1. **HealthGuard Premium Plan** (PPO)
   - $450/month, $2K deductible
   - $500K coverage
   - Comprehensive benefits

2. **MediCare Essential** (HMO)
   - $280/month, $3K deductible
   - $250K coverage
   - Basic coverage, referral required

3. **WellCare Comprehensive** (EPO)
   - $620/month, $1.5K deductible
   - $750K coverage
   - Includes chronic disease management

4. **Budget Shield Basic** (HMO)
   - $180/month, $5K deductible
   - $150K coverage
   - Minimal benefits, high cost-sharing

5. **PremiumCare Gold** (PPO)
   - $850/month, $1K deductible
   - $1M coverage
   - Premium benefits, worldwide coverage

---

## 🎨 User Interface Features

### Form Design
- **Progress indicators**: Visual steps for each section
- **Contextual help**: Tooltips and examples for each field
- **Smart defaults**: Sensible default values where applicable
- **Responsive layout**: Mobile-friendly Bootstrap 5 grid

### Results Display
- **Visual ranking**: Clear #1, #2, #3 badges
- **Score visualization**: Progress bars for each score type
- **Cost breakdown**: Easy-to-read financial summary
- **Rationale cards**: AI-generated explanations
- **Coverage comparison**: Side-by-side benefits vs exclusions

### Dashboard Integration
- **Patient dashboard**: Prominent card with feature description
- **Doctor dashboard**: Quick access for helping patients
- **History tracking**: View all past requests
- **Download option**: Export as JSON for records

---

## 🔒 Security & Privacy

### Access Control
- Login required for all insurance routes
- Users can only access their own quotes
- Admin users have full visibility

### Data Protection
- Explicit consent required before processing
- Two-part consent: data use + privacy policy
- No data processing without consent
- In-memory storage (production should use database)

### HIPAA Considerations
- Health data handled with care
- Consent form includes HIPAA notice
- Data use limited to quote generation
- Option to download personal data

---

## 🚀 Usage Examples

### Example 1: Healthy Young Professional
```
Input:
- Age: 28
- Conditions: None
- Income: $60,000
- Smoking: Never

Result:
- Risk score: ~25
- Top match: Budget Shield Basic (cost-effective)
- Rationale: Low risk profile, good income, minimal needs
```

### Example 2: Middle-aged with Chronic Conditions
```
Input:
- Age: 52
- Conditions: Diabetes, Hypertension
- Income: $80,000
- Smoking: Former

Result:
- Risk score: ~65
- Top match: WellCare Comprehensive
- Rationale: Chronic disease management included, moderate cost
```

### Example 3: High-risk Cancer Patient
```
Input:
- Age: 58
- Conditions: Cancer, Heart disease
- Income: $100,000
- Smoking: Never

Result:
- Risk score: ~88
- Top match: PremiumCare Gold
- Rationale: High coverage needed, comprehensive cancer treatment
```

---

## 🧪 Testing

### Manual Testing Steps

1. **Start the web application:**
   ```bash
   cd web_app
   python app.py
   ```

2. **Login as patient:**
   - Username: `patient_john`
   - Password: `password123`

3. **Navigate to Insurance Quote:**
   - Click "Request Quote" button on dashboard

4. **Fill out form:**
   - Enter health conditions (e.g., "diabetes, hypertension")
   - Enter medications
   - Fill in BMI, vitals
   - Select smoking status
   - Enter past medical history
   - Enter income (e.g., $50,000)
   - Check both consent boxes

5. **Submit and verify:**
   - Should redirect to quotes display
   - Verify quotes are ranked
   - Check score breakdowns
   - Read rationales
   - Download JSON

6. **Test edge cases:**
   - Empty conditions → Should still work
   - Very high risk → Should exclude budget plans
   - Low income → Should exclude expensive plans
   - No consent → Should show error

### Expected Behaviors

✅ **Success Case:**
- Form submits successfully
- AI processes in < 2 seconds
- 1-5 quotes displayed
- Quotes ranked by overall score
- Rationales are coherent
- Download works

✅ **No Results Case:**
- Shows "No suitable products" page
- Offers human advisor contact
- Allows retry with updated data
- Request ID saved

❌ **Error Cases:**
- Missing required fields → Validation error
- No consent → Error message
- Invalid request ID → 404 redirect

---

## 📈 Future Enhancements

### Phase 2 Features (Recommended)
1. **Real Insurance API Integration**
   - Connect to actual insurance providers
   - Real-time pricing
   - Policy availability checks

2. **Advanced Risk Models**
   - Machine learning risk prediction
   - Integration with FHIR clinical data
   - Predictive analytics

3. **Enhanced Comparisons**
   - Side-by-side comparison tool
   - Filtering and sorting options
   - Scenario analysis (what-if)

4. **Database Persistence**
   - PostgreSQL or MongoDB
   - Quote history analytics
   - User preferences storage

5. **Email Notifications**
   - Quote generation complete
   - New products available
   - Price changes alerts

6. **PDF Export**
   - Professional quote documents
   - Shareable with family/advisors
   - Print-ready format

7. **Human Advisor Integration**
   - Schedule consultation
   - Chat with advisor
   - Review quotes together

8. **Mobile App**
   - Native iOS/Android
   - Push notifications
   - Photo upload for medical documents

---

## 🐛 Known Limitations

1. **Sample Data Only**
   - Uses 5 hardcoded insurance products
   - Not connected to real insurance providers
   - Prices are illustrative

2. **In-Memory Storage**
   - Data lost on server restart
   - Not suitable for production
   - No concurrent user support at scale

3. **Simple Risk Model**
   - Rule-based (not ML)
   - Limited condition mapping
   - No genetic factors

4. **No Real-time Updates**
   - Products don't change
   - Prices don't fluctuate
   - No availability checks

5. **Basic Validation**
   - Text-based condition entry (not coded)
   - Limited medical terminology support
   - No duplicate detection

---

## 📝 Developer Notes

### Adding New Insurance Products

Edit `insurance_models.py`:

```python
def get_sample_insurance_products():
    return [
        InsuranceProduct(
            product_id='INS-006',
            name='Your New Plan',
            provider='Insurance Co',
            plan_type='PPO',
            coverage_amount=300000,
            monthly_premium=350,
            annual_deductible=2500,
            copay=25,
            coinsurance=20,
            max_out_of_pocket=6500,
            coverage_details=['Coverage 1', 'Coverage 2'],
            exclusions=['Exclusion 1']
        ),
        # ... existing products
    ]
```

### Modifying Risk Factors

Edit `insurance_engine.py`:

```python
self.risk_factors = {
    'diabetes': 2.5,
    'your_new_condition': 2.0,  # Add here
    # ... existing factors
}
```

### Adjusting Eligibility Rules

Edit `insurance_engine.py` → `_filter_eligible_products()`:

```python
# Add your custom rule
if your_condition and product.some_requirement:
    continue  # Skip this product
```

---

## 🎓 Educational Value

This feature demonstrates:

- **Full-stack development**: Backend (Flask) + Frontend (HTML/CSS/JS)
- **AI/ML concepts**: Risk scoring, recommendation engines
- **Healthcare domain**: Medical data, insurance concepts
- **UX design**: Multi-step forms, progressive disclosure
- **Software architecture**: MVC pattern, modular design
- **Data modeling**: OOP, JSON serialization
- **Security**: Authentication, authorization, consent

---

## 📞 Support

For questions or issues with this feature:

1. Check this documentation
2. Review the flowchart (provided by Chadwick Ng)
3. Examine the code comments
4. Test with sample data first

---

## ✅ Implementation Checklist

- [x] Backend models created (`insurance_models.py`)
- [x] AI engine implemented (`insurance_engine.py`)
- [x] Web forms defined (`forms.py`)
- [x] Flask routes added (`app.py`)
- [x] Request form template (`insurance_quote_form.html`)
- [x] Results display template (`insurance_quotes_display.html`)
- [x] No results template (`insurance_no_results.html`)
- [x] History template (`insurance_history.html`)
- [x] Dashboard integration (patient + doctor)
- [x] Access control (login required, user ownership)
- [x] Consent validation
- [x] JSON download feature
- [x] Documentation (this file)
- [x] Code linting (no errors)
- [x] Sample insurance products (5 plans)
- [x] Risk assessment algorithm
- [x] Score calculation formulas
- [x] Rationale generation

---

**End of Documentation**

