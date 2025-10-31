"""
Insurance Quote Models and Data Structures
For the Request Insurance Quote feature (by Chadwick Ng)
"""

from datetime import datetime
from typing import List, Dict, Optional
import json


class HealthData:
    """User's current health data"""
    def __init__(self):
        self.conditions = []  # List of current conditions
        self.medications = []  # Current medications
        self.bmi = None
        self.blood_pressure = None
        self.cholesterol = None
        self.glucose = None
        self.smoking_status = None
        self.alcohol_consumption = None
        
    def to_dict(self):
        return {
            'conditions': self.conditions,
            'medications': self.medications,
            'bmi': self.bmi,
            'blood_pressure': self.blood_pressure,
            'cholesterol': self.cholesterol,
            'glucose': self.glucose,
            'smoking_status': self.smoking_status,
            'alcohol_consumption': self.alcohol_consumption
        }


class MedicalHistory:
    """Past medical history"""
    def __init__(self):
        self.past_conditions = []
        self.surgeries = []
        self.hospitalizations = []
        self.family_history = []
        
    def to_dict(self):
        return {
            'past_conditions': self.past_conditions,
            'surgeries': self.surgeries,
            'hospitalizations': self.hospitalizations,
            'family_history': self.family_history
        }


class IncomeDetails:
    """User's income and financial information"""
    def __init__(self, annual_income=0, employment_status='', occupation=''):
        self.annual_income = annual_income
        self.employment_status = employment_status
        self.occupation = occupation
        self.dependents = 0
        
    def to_dict(self):
        return {
            'annual_income': self.annual_income,
            'employment_status': self.employment_status,
            'occupation': self.occupation,
            'dependents': self.dependents
        }


class InsuranceProduct:
    """Insurance product definition"""
    def __init__(self, product_id, name, provider, plan_type, coverage_amount,
                 monthly_premium, annual_deductible, copay, coinsurance,
                 max_out_of_pocket, coverage_details, exclusions):
        self.product_id = product_id
        self.name = name
        self.provider = provider
        self.plan_type = plan_type  # HMO, PPO, EPO, POS
        self.coverage_amount = coverage_amount
        self.monthly_premium = monthly_premium
        self.annual_deductible = annual_deductible
        self.copay = copay
        self.coinsurance = coinsurance
        self.max_out_of_pocket = max_out_of_pocket
        self.coverage_details = coverage_details
        self.exclusions = exclusions
        
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'provider': self.provider,
            'plan_type': self.plan_type,
            'coverage_amount': self.coverage_amount,
            'monthly_premium': self.monthly_premium,
            'annual_deductible': self.annual_deductible,
            'copay': self.copay,
            'coinsurance': self.coinsurance,
            'max_out_of_pocket': self.max_out_of_pocket,
            'coverage_details': self.coverage_details,
            'exclusions': self.exclusions
        }


class InsuranceQuote:
    """Generated insurance quote with suitability ranking"""
    def __init__(self, product: InsuranceProduct, suitability_score, 
                 cost_score, coverage_score, rationale):
        self.product = product
        self.suitability_score = suitability_score  # 0-100
        self.cost_score = cost_score  # 0-100
        self.coverage_score = coverage_score  # 0-100
        self.overall_score = (suitability_score + cost_score + coverage_score) / 3
        self.rationale = rationale
        self.generated_at = datetime.now()
        
    def to_dict(self):
        return {
            'product': self.product.to_dict(),
            'suitability_score': self.suitability_score,
            'cost_score': self.cost_score,
            'coverage_score': self.coverage_score,
            'overall_score': round(self.overall_score, 2),
            'rationale': self.rationale,
            'generated_at': self.generated_at.isoformat()
        }


class QuoteRequest:
    """Complete insurance quote request"""
    def __init__(self, user_id):
        self.request_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.user_id = user_id
        self.health_data = HealthData()
        self.medical_history = MedicalHistory()
        self.income_details = IncomeDetails()
        self.consent_given = False
        self.created_at = datetime.now()
        self.status = 'draft'  # draft, processing, completed, failed, pending_doctor_review
        self.quotes = []
        self.doctor_review_requested = False
        self.doctor_id = None
        self.doctor_notes = None
        self.reviewed_at = None
        self.favorites = []  # List of product_ids marked as favorite
        self.shared_with_doctor = False
        
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'health_data': self.health_data.to_dict(),
            'medical_history': self.medical_history.to_dict(),
            'income_details': self.income_details.to_dict(),
            'consent_given': self.consent_given,
            'created_at': self.created_at.isoformat(),
            'status': self.status,
            'quotes': [q.to_dict() for q in self.quotes]
        }


# ================================
# Australian Private Health Funds (2025)
# ================================

def get_au_health_funds() -> List[Dict[str, str]]:
    """Return catalog of Australian health funds (open and restricted).

    Fields: name, type (open|restricted), not_for_profit (bool), notes
    """
    catalog: List[Dict[str, str]] = [
        # Open membership (anyone can join)
        {"name": "Bupa Australia", "type": "open", "nfp": False, "notes": "Large national network"},
        {"name": "Medibank Private", "type": "open", "nfp": False, "notes": "Owns ahm brand"},
        {"name": "ahm (by Medibank)", "type": "open", "nfp": False, "notes": "Budget-focused"},
        {"name": "HCF", "type": "open", "nfp": True, "notes": "Largest NFP; strong extras"},
        {"name": "nib Health Funds", "type": "open", "nfp": False, "notes": "Popular with young singles"},
        {"name": "HBF Health", "type": "open", "nfp": True, "notes": "WA based"},
        {"name": "Australian Unity Health", "type": "open", "nfp": True, "notes": "Member-owned mutual"},
        {"name": "GMHBA Health Insurance", "type": "open", "nfp": True, "notes": "Owns Frank and MyOwn"},
        {"name": "Health Partners", "type": "open", "nfp": True, "notes": "SA based; dental & optical"},
        {"name": "HIF", "type": "open", "nfp": True, "notes": "Flexible extras"},
        {"name": "St Lukes Health", "type": "open", "nfp": True, "notes": "TAS based"},
        {"name": "Latrobe Health Services", "type": "open", "nfp": True, "notes": "VIC based"},
        {"name": "Westfund Health Insurance", "type": "open", "nfp": True, "notes": "Regional NSW & QLD"},
        {"name": "Phoenix Health Fund", "type": "open", "nfp": True, "notes": "NSW; small member focus"},
        {"name": "AIA Health Insurance", "type": "open", "nfp": False, "notes": "With Vitality rewards"},
        {"name": "MyOwn Health Insurance", "type": "open", "nfp": False, "notes": "GMHBA & AIA"},
        {"name": "Health Care Insurance (HCI)", "type": "open", "nfp": True, "notes": "TAS small fund"},
        {"name": "Queensland Country Health", "type": "open", "nfp": True, "notes": "Regional QLD"},
        {"name": "Mildura Health Fund", "type": "open", "nfp": True, "notes": "Regional VIC"},
        {"name": "National Health Benefits Australia (onemedifund)", "type": "open", "nfp": True, "notes": "Online first"},
        # Restricted membership (eligibility required)
        {"name": "Defence Health", "type": "restricted", "nfp": True, "notes": "ADF personnel & family"},
        {"name": "Police Health", "type": "restricted", "nfp": True, "notes": "Police & families"},
        {"name": "Teachers Health", "type": "restricted", "nfp": True, "notes": "Education sector; incl. UniHealth & NMH"},
        {"name": "Navy Health", "type": "restricted", "nfp": True, "notes": "Defence sector"},
        {"name": "Doctors' Health Fund", "type": "restricted", "nfp": True, "notes": "Medical professionals"},
        {"name": "CBHS Health Fund", "type": "restricted", "nfp": True, "notes": "Commonwealth Bank group"},
        {"name": "Reserve Bank Health Society", "type": "restricted", "nfp": True, "notes": "RBA & finance sector"},
        {"name": "ACA Health Benefits Fund", "type": "restricted", "nfp": True, "notes": "Adventist community"},
        {"name": "RT Health Fund", "type": "restricted", "nfp": True, "notes": "Transport workers; part of Police Health Group"},
        {"name": "Transport Health / Union Health", "type": "restricted", "nfp": True, "notes": "Union/transport; QLD"},
    ]
    return catalog


def get_au_insurance_products() -> List[InsuranceProduct]:
    """Build InsuranceProduct entries from AU health fund catalog.

    Since real premiums/benefits vary, this function generates representative
    plans using heuristics so the quote engine can rank providers sensibly.
    """
    funds = get_au_health_funds()
    products: List[InsuranceProduct] = []

    for f in funds:
        name = f["name"]
        is_nfp = bool(f["nfp"])
        is_restricted = f["type"] == "restricted"

        # Derive a plan profile
        if "ahm" in name.lower():
            plan_type = 'HMO'
            premium = 260
            coverage_amount = 250000
            deductible = 3500
            max_oop = 7500
            details = ['Hospitalization coverage', 'Outpatient services', 'Prescription drugs']
        elif any(k in name for k in ['Bupa', 'Medibank', 'nib', 'AIA']):
            plan_type = 'PPO'
            premium = 420
            coverage_amount = 750000
            deductible = 2000
            max_oop = 6000
            details = ['Hospitalization coverage', 'Outpatient services', 'Prescription drugs', 'Preventive care', 'Mental health services']
        elif is_restricted:
            plan_type = 'EPO'
            premium = 320
            coverage_amount = 750000
            deductible = 1800
            max_oop = 5000
            details = ['Hospitalization coverage', 'Outpatient services', 'Prescription drugs', 'Maternity care', 'Chronic disease management']
        else:
            plan_type = 'EPO' if is_nfp else 'HMO'
            premium = 300 if is_nfp else 340
            coverage_amount = 500000
            deductible = 2500
            max_oop = 6500
            details = ['Hospitalization coverage', 'Outpatient services', 'Prescription drugs', 'Preventive care']

        exclusions = ['Cosmetic procedures', 'Experimental treatments']
        if plan_type == 'HMO':
            exclusions.append('Out-of-network services')

        products.append(
            InsuranceProduct(
                product_id=f"AU-{len(products)+1:03}",
                name=f"{name} Standard Hospital + Extras",
                provider=name,
                plan_type=plan_type,
                coverage_amount=coverage_amount,
                monthly_premium=premium,
                annual_deductible=deductible,
                copay=25,
                coinsurance=20,
                max_out_of_pocket=max_oop,
                coverage_details=details + ['Chronic disease management' if is_nfp or is_restricted else 'Telemedicine services'],
                exclusions=exclusions,
            )
        )

    return products

# ================================
# Sample Insurance Products (Mock Data)
# ================================

def get_sample_insurance_products() -> List[InsuranceProduct]:
    """Return sample insurance products for demonstration"""
    return [
        InsuranceProduct(
            product_id='INS-001',
            name='HealthGuard Premium Plan',
            provider='HealthGuard Insurance',
            plan_type='PPO',
            coverage_amount=500000,
            monthly_premium=450,
            annual_deductible=2000,
            copay=30,
            coinsurance=20,
            max_out_of_pocket=6000,
            coverage_details=[
                'Hospitalization coverage',
                'Outpatient services',
                'Prescription drugs',
                'Preventive care',
                'Mental health services',
                'Emergency care'
            ],
            exclusions=[
                'Cosmetic procedures',
                'Experimental treatments',
                'Pre-existing conditions (first 6 months)'
            ]
        ),
        InsuranceProduct(
            product_id='INS-002',
            name='MediCare Essential',
            provider='MediCare Corp',
            plan_type='HMO',
            coverage_amount=250000,
            monthly_premium=280,
            annual_deductible=3000,
            copay=25,
            coinsurance=30,
            max_out_of_pocket=7500,
            coverage_details=[
                'Primary care',
                'Specialist referrals',
                'Hospital stays',
                'Lab tests',
                'Preventive screenings'
            ],
            exclusions=[
                'Out-of-network care',
                'Alternative medicine',
                'Dental and vision'
            ]
        ),
        InsuranceProduct(
            product_id='INS-003',
            name='WellCare Comprehensive',
            provider='WellCare Health',
            plan_type='EPO',
            coverage_amount=750000,
            monthly_premium=620,
            annual_deductible=1500,
            copay=20,
            coinsurance=15,
            max_out_of_pocket=5000,
            coverage_details=[
                'Comprehensive hospital coverage',
                'Prescription drug coverage',
                'Mental health & substance abuse',
                'Maternity care',
                'Chronic disease management',
                'Telemedicine services'
            ],
            exclusions=[
                'Cosmetic surgery',
                'Weight loss programs',
                'Long-term care'
            ]
        ),
        InsuranceProduct(
            product_id='INS-004',
            name='Budget Shield Basic',
            provider='Budget Insurance Co',
            plan_type='HMO',
            coverage_amount=150000,
            monthly_premium=180,
            annual_deductible=5000,
            copay=40,
            coinsurance=40,
            max_out_of_pocket=10000,
            coverage_details=[
                'Basic hospitalization',
                'Emergency services',
                'Generic prescriptions',
                'Annual checkup'
            ],
            exclusions=[
                'Specialist care (without referral)',
                'Brand-name drugs',
                'Out-of-network services',
                'Mental health services'
            ]
        ),
        InsuranceProduct(
            product_id='INS-005',
            name='PremiumCare Gold',
            provider='Premium Health Solutions',
            plan_type='PPO',
            coverage_amount=1000000,
            monthly_premium=850,
            annual_deductible=1000,
            copay=15,
            coinsurance=10,
            max_out_of_pocket=4000,
            coverage_details=[
                'Unlimited hospital coverage',
                'Worldwide emergency coverage',
                'Advanced cancer treatment',
                'Organ transplant coverage',
                'Home healthcare',
                'Alternative medicine (acupuncture)',
                'Wellness programs'
            ],
            exclusions=[
                'Cosmetic procedures',
                'Fertility treatments'
            ]
        )
    ]


# ================================
# In-Memory Storage for Quote Requests
# ================================

quote_requests_storage = {}


def save_quote_request(request: QuoteRequest):
    """Save quote request to storage"""
    quote_requests_storage[request.request_id] = request
    return request.request_id


def get_quote_request(request_id: str) -> Optional[QuoteRequest]:
    """Retrieve quote request from storage"""
    return quote_requests_storage.get(request_id)


def get_user_quote_requests(user_id: str) -> List[QuoteRequest]:
    """Get all quote requests for a user"""
    return [req for req in quote_requests_storage.values() if req.user_id == user_id]

