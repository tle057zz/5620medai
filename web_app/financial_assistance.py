"""
UC-04: Financial Assistance with Loan Matching (Venkatesh Badri Narayanan)
Subsidy eligibility calculation and financial assistance matching

This module provides:
- Income-based subsidy calculation (ACA, Medicare, Medicaid)
- Financial assistance program matching
- Affordability scoring
- Plan comparison with subsidies
- Loan/payment plan recommendations
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class SubsidyType(Enum):
    """Types of government subsidies"""
    ACA_PREMIUM = "aca_premium"  # Affordable Care Act premium tax credit
    ACA_COST_SHARING = "aca_cost_sharing"  # Cost-sharing reduction
    MEDICARE = "medicare"  # Medicare eligibility
    MEDICAID = "medicaid"  # Medicaid eligibility
    STATE_PROGRAM = "state_program"  # State-specific assistance
    NONE = "none"


class EligibilityStatus(Enum):
    """Subsidy eligibility status"""
    ELIGIBLE = "eligible"
    PARTIALLY_ELIGIBLE = "partially_eligible"
    NOT_ELIGIBLE = "not_eligible"
    PENDING_VERIFICATION = "pending_verification"


@dataclass
class FinancialProfile:
    """User's financial profile for subsidy calculation"""
    annual_income: float
    household_size: int
    state: str = "NSW"  # Australian state (NSW, VIC, QLD, etc.)
    employment_status: str = "employed"
    dependents: int = 0
    has_medicare_card: bool = False
    has_health_care_card: bool = False
    pensioner: bool = False
    student: bool = False
    
    # Additional financial info
    assets: float = 0.0
    debts: float = 0.0
    credit_score: Optional[int] = None
    
    def federal_poverty_level_percentage(self) -> float:
        """
        Calculate income as percentage of Federal Poverty Level (FPL)
        Using Australian equivalent - median household income thresholds
        """
        # Australian median household income baseline (2024): ~$92,000
        # Adjust by household size
        baseline_income = 92000
        adjusted_baseline = baseline_income + (self.household_size - 1) * 15000
        
        fpl_percentage = (self.annual_income / adjusted_baseline) * 100
        return round(fpl_percentage, 1)


@dataclass
class SubsidyCalculation:
    """Result of subsidy eligibility calculation"""
    subsidy_type: SubsidyType
    eligibility_status: EligibilityStatus
    monthly_subsidy_amount: float
    annual_subsidy_amount: float
    income_threshold_percentage: float
    rationale: str
    requirements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'subsidy_type': self.subsidy_type.value,
            'eligibility_status': self.eligibility_status.value,
            'monthly_subsidy': self.monthly_subsidy_amount,
            'annual_subsidy': self.annual_subsidy_amount,
            'income_threshold_pct': self.income_threshold_percentage,
            'rationale': self.rationale,
            'requirements': self.requirements
        }


@dataclass
class AffordabilityScore:
    """Affordability assessment for a plan"""
    score: int  # 0-100
    rating: str  # "Excellent", "Good", "Fair", "Poor"
    monthly_cost_after_subsidy: float
    percentage_of_income: float
    is_affordable: bool
    concerns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class FinancialAssistanceOption:
    """Financial assistance or loan option"""
    option_id: str
    option_type: str  # "subsidy", "payment_plan", "loan", "charity"
    provider: str
    amount: float
    terms: str
    eligibility_criteria: List[str]
    application_process: str
    approval_likelihood: float  # 0.0-1.0
    interest_rate: Optional[float] = None
    repayment_period_months: Optional[int] = None


@dataclass
class AssistanceRecommendation:
    """Complete financial assistance recommendation"""
    request_id: str
    user_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Input data
    financial_profile: FinancialProfile
    selected_plan_id: Optional[str] = None
    original_monthly_cost: float = 0.0
    
    # Calculated subsidies
    subsidies: List[SubsidyCalculation] = field(default_factory=list)
    total_monthly_subsidy: float = 0.0
    total_annual_subsidy: float = 0.0
    
    # Adjusted costs
    monthly_cost_after_subsidy: float = 0.0
    annual_cost_after_subsidy: float = 0.0
    
    # Affordability
    affordability_score: Optional[AffordabilityScore] = None
    
    # Additional assistance options
    assistance_options: List[FinancialAssistanceOption] = field(default_factory=list)
    
    # Recommendations
    recommended: bool = True
    recommendation_rationale: str = ""
    next_steps: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'financial_profile': {
                'annual_income': self.financial_profile.annual_income,
                'household_size': self.financial_profile.household_size,
                'fpl_percentage': self.financial_profile.federal_poverty_level_percentage()
            },
            'subsidies': [s.to_dict() for s in self.subsidies],
            'total_monthly_subsidy': self.total_monthly_subsidy,
            'monthly_cost_after_subsidy': self.monthly_cost_after_subsidy,
            'affordability_score': self.affordability_score.__dict__ if self.affordability_score else None,
            'assistance_options': [opt.__dict__ for opt in self.assistance_options],
            'recommended': self.recommended,
            'recommendation_rationale': self.recommendation_rationale,
            'next_steps': self.next_steps
        }


# In-memory storage
assistance_recommendations_storage: Dict[str, AssistanceRecommendation] = {}


def calculate_subsidies(financial_profile: FinancialProfile, monthly_premium: float) -> List[SubsidyCalculation]:
    """
    Calculate all applicable subsidies based on financial profile
    Uses Australian healthcare system eligibility rules
    """
    subsidies = []
    fpl_percentage = financial_profile.federal_poverty_level_percentage()
    
    # 1. Medicare Levy Surcharge Exemption (Australian system)
    if financial_profile.has_medicare_card or financial_profile.annual_income < 90000:
        subsidy_amount = monthly_premium * 0.15  # 15% reduction
        subsidies.append(SubsidyCalculation(
            subsidy_type=SubsidyType.MEDICARE,
            eligibility_status=EligibilityStatus.ELIGIBLE,
            monthly_subsidy_amount=subsidy_amount,
            annual_subsidy_amount=subsidy_amount * 12,
            income_threshold_percentage=fpl_percentage,
            rationale="Medicare card holder or income below threshold",
            requirements=["Valid Medicare card", "Annual income verification"]
        ))
    
    # 2. Low Income Health Care Card Benefits
    if financial_profile.has_health_care_card or financial_profile.annual_income < 60000:
        subsidy_amount = monthly_premium * 0.25  # 25% reduction
        subsidies.append(SubsidyCalculation(
            subsidy_type=SubsidyType.STATE_PROGRAM,
            eligibility_status=EligibilityStatus.ELIGIBLE,
            monthly_subsidy_amount=subsidy_amount,
            annual_subsidy_amount=subsidy_amount * 12,
            income_threshold_percentage=fpl_percentage,
            rationale="Health Care Card holder or low income",
            requirements=["Valid Health Care Card", "Income verification"]
        ))
    
    # 3. Pensioner/Senior Discount
    if financial_profile.pensioner:
        subsidy_amount = monthly_premium * 0.30  # 30% reduction
        subsidies.append(SubsidyCalculation(
            subsidy_type=SubsidyType.STATE_PROGRAM,
            eligibility_status=EligibilityStatus.ELIGIBLE,
            monthly_subsidy_amount=subsidy_amount,
            annual_subsidy_amount=subsidy_amount * 12,
            income_threshold_percentage=fpl_percentage,
            rationale="Pensioner or senior citizen discount",
            requirements=["Pensioner Concession Card", "Age verification"]
        ))
    
    # 4. Student Discount
    if financial_profile.student and financial_profile.annual_income < 40000:
        subsidy_amount = monthly_premium * 0.20  # 20% reduction
        subsidies.append(SubsidyCalculation(
            subsidy_type=SubsidyType.STATE_PROGRAM,
            eligibility_status=EligibilityStatus.ELIGIBLE,
            monthly_subsidy_amount=subsidy_amount,
            annual_subsidy_amount=subsidy_amount * 12,
            income_threshold_percentage=fpl_percentage,
            rationale="Full-time student discount",
            requirements=["Valid student ID", "Enrollment verification"]
        ))
    
    # 5. Family/Household Size Adjustment
    if financial_profile.household_size >= 3:
        subsidy_amount = monthly_premium * 0.10 * (financial_profile.household_size - 2)
        subsidy_amount = min(subsidy_amount, monthly_premium * 0.30)  # Cap at 30%
        subsidies.append(SubsidyCalculation(
            subsidy_type=SubsidyType.STATE_PROGRAM,
            eligibility_status=EligibilityStatus.ELIGIBLE,
            monthly_subsidy_amount=subsidy_amount,
            annual_subsidy_amount=subsidy_amount * 12,
            income_threshold_percentage=fpl_percentage,
            rationale=f"Large household discount ({financial_profile.household_size} members)",
            requirements=["Household composition verification"]
        ))
    
    return subsidies


def calculate_affordability_score(
    financial_profile: FinancialProfile,
    monthly_cost_after_subsidy: float
) -> AffordabilityScore:
    """
    Calculate affordability score based on income and costs
    """
    monthly_income = financial_profile.annual_income / 12
    cost_percentage = (monthly_cost_after_subsidy / monthly_income) * 100
    
    concerns = []
    recommendations = []
    
    # Scoring logic
    if cost_percentage <= 5:
        score = 95
        rating = "Excellent"
        is_affordable = True
    elif cost_percentage <= 8:
        score = 80
        rating = "Good"
        is_affordable = True
    elif cost_percentage <= 12:
        score = 60
        rating = "Fair"
        is_affordable = True
        concerns.append("Premium is 8-12% of income - monitor budget carefully")
        recommendations.append("Consider setting up automatic savings for premiums")
    elif cost_percentage <= 15:
        score = 40
        rating = "Borderline"
        is_affordable = False
        concerns.append("Premium exceeds 12% of income - may strain budget")
        recommendations.append("Explore payment plans or additional subsidies")
        recommendations.append("Consider higher deductible plans to lower premiums")
    else:
        score = 20
        rating = "Poor"
        is_affordable = False
        concerns.append("Premium exceeds 15% of income - high financial burden")
        concerns.append("May be unaffordable without additional assistance")
        recommendations.append("Seek human advisor consultation")
        recommendations.append("Explore charity care programs")
        recommendations.append("Consider catastrophic coverage plans")
    
    return AffordabilityScore(
        score=score,
        rating=rating,
        monthly_cost_after_subsidy=monthly_cost_after_subsidy,
        percentage_of_income=round(cost_percentage, 1),
        is_affordable=is_affordable,
        concerns=concerns,
        recommendations=recommendations
    )


def generate_assistance_options(
    financial_profile: FinancialProfile,
    remaining_monthly_cost: float
) -> List[FinancialAssistanceOption]:
    """
    Generate additional financial assistance options (payment plans, loans, charity)
    """
    options = []
    
    # 1. Payment Plan (always available)
    options.append(FinancialAssistanceOption(
        option_id=str(uuid.uuid4()),
        option_type="payment_plan",
        provider="Insurer Payment Plan",
        amount=remaining_monthly_cost,
        terms="Spread monthly premium over bi-weekly or weekly payments",
        eligibility_criteria=["Active insurance policy"],
        application_process="Automatic - request through insurer portal",
        approval_likelihood=0.95,
        interest_rate=0.0,
        repayment_period_months=1
    ))
    
    # 2. Medical Loan (for low-income)
    if financial_profile.annual_income < 70000:
        loan_amount = remaining_monthly_cost * 12  # Annual premium
        options.append(FinancialAssistanceOption(
            option_id=str(uuid.uuid4()),
            option_type="loan",
            provider="Healthcare Finance Australia",
            amount=loan_amount,
            terms=f"Low-interest loan for health insurance premiums (5% APR)",
            eligibility_criteria=[
                "Annual income below $70,000",
                "Australian citizen or permanent resident",
                "Credit score above 600"
            ],
            application_process="Online application - 3-5 business days",
            approval_likelihood=0.70 if financial_profile.credit_score and financial_profile.credit_score > 600 else 0.40,
            interest_rate=5.0,
            repayment_period_months=12
        ))
    
    # 3. Charity Care Program (for very low income)
    if financial_profile.annual_income < 45000:
        options.append(FinancialAssistanceOption(
            option_id=str(uuid.uuid4()),
            option_type="charity",
            provider="Australian Healthcare Assistance Foundation",
            amount=remaining_monthly_cost * 6,  # 6 months coverage
            terms="Partial or full premium coverage for up to 6 months",
            eligibility_criteria=[
                "Annual income below $45,000",
                "Demonstrated financial hardship",
                "No other insurance options"
            ],
            application_process="Application with financial documentation - 2 weeks",
            approval_likelihood=0.50,
            interest_rate=None,
            repayment_period_months=None
        ))
    
    # 4. Government Hardship Program
    if financial_profile.annual_income < 50000 and financial_profile.household_size >= 2:
        options.append(FinancialAssistanceOption(
            option_id=str(uuid.uuid4()),
            option_type="subsidy",
            provider="State Government Hardship Fund",
            amount=remaining_monthly_cost * 0.50 * 12,  # 50% of annual cost
            terms="State-sponsored premium assistance for financial hardship",
            eligibility_criteria=[
                "Household income below threshold",
                "Dependents in household",
                "Australian citizen"
            ],
            application_process="Application through Services Australia - 4 weeks",
            approval_likelihood=0.60,
            interest_rate=None,
            repayment_period_months=None
        ))
    
    return options


def create_assistance_recommendation(
    financial_profile: FinancialProfile,
    user_id: str,
    original_monthly_cost: float,
    selected_plan_id: Optional[str] = None
) -> AssistanceRecommendation:
    """
    Create complete financial assistance recommendation
    """
    # Calculate subsidies
    subsidies = calculate_subsidies(financial_profile, original_monthly_cost)
    total_monthly_subsidy = sum(s.monthly_subsidy_amount for s in subsidies)
    
    # Calculate adjusted costs
    monthly_cost_after_subsidy = max(0, original_monthly_cost - total_monthly_subsidy)
    annual_cost_after_subsidy = monthly_cost_after_subsidy * 12
    
    # Calculate affordability
    affordability = calculate_affordability_score(financial_profile, monthly_cost_after_subsidy)
    
    # Generate additional assistance options if needed
    assistance_options = []
    if not affordability.is_affordable:
        assistance_options = generate_assistance_options(financial_profile, monthly_cost_after_subsidy)
    
    # Generate recommendation
    recommended = affordability.is_affordable or len(assistance_options) > 0
    
    if affordability.is_affordable:
        rationale = f"Plan is affordable ({affordability.rating}) at {affordability.percentage_of_income}% of monthly income after ${total_monthly_subsidy:.2f} in subsidies."
    else:
        rationale = f"Plan requires additional assistance. After ${total_monthly_subsidy:.2f} in subsidies, remaining cost is {affordability.percentage_of_income}% of income. {len(assistance_options)} assistance options available."
    
    # Next steps
    next_steps = []
    if subsidies:
        next_steps.append("Apply for eligible subsidies (see list above)")
    if assistance_options:
        next_steps.append("Review and apply for additional assistance options")
    next_steps.append("Confirm enrollment with selected plan")
    next_steps.append("Set up automatic payment method")
    
    recommendation = AssistanceRecommendation(
        request_id=str(uuid.uuid4()),
        user_id=user_id,
        financial_profile=financial_profile,
        selected_plan_id=selected_plan_id,
        original_monthly_cost=original_monthly_cost,
        subsidies=subsidies,
        total_monthly_subsidy=total_monthly_subsidy,
        total_annual_subsidy=total_monthly_subsidy * 12,
        monthly_cost_after_subsidy=monthly_cost_after_subsidy,
        annual_cost_after_subsidy=annual_cost_after_subsidy,
        affordability_score=affordability,
        assistance_options=assistance_options,
        recommended=recommended,
        recommendation_rationale=rationale,
        next_steps=next_steps
    )
    
    # Save to storage
    assistance_recommendations_storage[recommendation.request_id] = recommendation
    
    return recommendation


def get_assistance_recommendation(request_id: str) -> Optional[AssistanceRecommendation]:
    """Retrieve assistance recommendation by ID"""
    return assistance_recommendations_storage.get(request_id)

