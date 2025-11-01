"""
AI Insurance Quote Engine
Processes health data and generates tailored insurance quotes
NOW WITH ENHANCED MEDICAL SAFETY ASSESSMENT!
"""

from typing import List, Tuple
import re
import os
import html as _html
from insurance_models import (
    QuoteRequest, InsuranceQuote, InsuranceProduct,
    get_sample_insurance_products, get_au_insurance_products
)

# Try to import medical safety assessment
try:
    from medical_document_processor import assess_medical_safety
    SAFETY_AVAILABLE = True
except:
    SAFETY_AVAILABLE = False
    assess_medical_safety = None


class InsuranceQuoteEngine:
    """AI-powered insurance quote matching engine"""
    
    def __init__(self):
        self.progress_cb = None
        self.total_products = 1
        self.idx = 0
        # Prefer Australian fund catalog products; fallback to sample if import fails
        try:
            products = get_au_insurance_products()
            if not products:
                raise ValueError('empty products')
            self.products = products
        except Exception:
            self.products = get_sample_insurance_products()
        self.risk_factors = {
            'diabetes': 2.5,
            'hypertension': 1.8,
            'heart disease': 3.0,
            'cancer': 3.5,
            'copd': 2.2,
            'asthma': 1.5,
            'obesity': 1.6,
            'smoking': 2.0,
            'chronic kidney disease': 2.8
        }
    
    def process_quote_request(self, request: QuoteRequest) -> List[InsuranceQuote]:
        """
        Main orchestration function for AI processing
        Returns ranked list of insurance quotes
        """
        # Step 1: Normalize input data
        normalized_data = self._normalize_data(request)
        
        # Step 2: Calculate risk assessment
        risk_score = self._assess_risk(normalized_data)
        
        # Step 3: Apply eligibility rules
        eligible_products = self._filter_eligible_products(
            self.products, normalized_data, risk_score
        )
        
        # Step 4: Generate quotes for eligible products
        quotes = []
        for product in eligible_products:
            quote = self._generate_quote(product, normalized_data, risk_score)
            quotes.append(quote)
        
        # Step 5: Rank quotes by overall score
        quotes.sort(key=lambda q: q.overall_score, reverse=True)
        
        # Step 6: Decide how many to show (AI-assisted with fallback)
        top_k = None
        use_ai_topk = normalized.get('use_ai_explainer') or os.environ.get('USE_AI_TOPK', 'false').lower() in {'1','true','yes'}
        if use_ai_topk:
            try:
                from ai_explainer import decide_top_k
                top_k = decide_top_k(normalized, risk_score, len(quotes), progress_cb=progress_cb)
            except Exception:
                top_k = None
        if top_k is None:
            # Fallback heuristic
            top_k = 10
            if risk_score >= 70:
                top_k = 6
            elif risk_score >= 55:
                top_k = 8
            elif risk_score <= 35:
                top_k = 12
        
        return quotes[:max(1, min(top_k, len(quotes)))]
    
    def _normalize_data(self, request: QuoteRequest) -> dict:
        """
        Normalize and standardize input data
        - Convert conditions to standard codes
        - Normalize vital signs
        - Categorize income brackets
        """
        normalized = {
            'age': self._estimate_age(request),
            'conditions': self._normalize_conditions(request.health_data.conditions),
            'past_conditions': self._normalize_conditions(request.medical_history.past_conditions),
            'medications': request.health_data.medications,
            'bmi': request.health_data.bmi or 25,  # Default if not provided
            'smoking': request.health_data.smoking_status == 'smoker',
            'income_bracket': self._categorize_income(request.income_details.annual_income),
            'employment_stable': request.income_details.employment_status in ['full-time', 'self-employed'],
            'family_history': request.medical_history.family_history,
            'surgeries_count': len(request.medical_history.surgeries),
            'hospitalizations_count': len(request.medical_history.hospitalizations),
            'request_id': getattr(request, 'request_id', 'REQ'),
            'use_ai_explainer': getattr(request, 'use_ai_explainer', False)
        }
        return normalized
    
    def _normalize_conditions(self, conditions: List[str]) -> List[str]:
        """Normalize condition names to standard terms"""
        normalized = []
        for condition in conditions:
            condition_lower = condition.lower().strip()
            # Simple normalization - in production, use proper medical ontology
            if 'diabet' in condition_lower:
                normalized.append('diabetes')
            elif 'hypertens' in condition_lower or 'high blood pressure' in condition_lower:
                normalized.append('hypertension')
            elif 'heart' in condition_lower or 'cardiac' in condition_lower:
                normalized.append('heart disease')
            elif 'cancer' in condition_lower or 'tumor' in condition_lower:
                normalized.append('cancer')
            elif 'asthma' in condition_lower:
                normalized.append('asthma')
            elif 'copd' in condition_lower or 'emphysema' in condition_lower:
                normalized.append('copd')
            elif 'kidney' in condition_lower or 'renal' in condition_lower:
                normalized.append('chronic kidney disease')
            elif 'obes' in condition_lower:
                normalized.append('obesity')
            else:
                normalized.append(condition_lower)
        return normalized
    
    def _estimate_age(self, request: QuoteRequest) -> int:
        """Estimate user age (in production, use actual DOB)"""
        # For demo, estimate based on conditions
        # In production, calculate from user's date of birth
        return 35  # Default age
    
    def _categorize_income(self, annual_income: float) -> str:
        """Categorize income into brackets"""
        if annual_income < 30000:
            return 'low'
        elif annual_income < 75000:
            return 'middle'
        elif annual_income < 150000:
            return 'upper-middle'
        else:
            return 'high'
    
    def _assess_risk(self, normalized_data: dict) -> float:
        """
        Calculate risk score based on health data
        Returns score from 0 (low risk) to 100 (high risk)
        NOW WITH ENHANCED MEDICAL SAFETY ASSESSMENT!
        """
        base_risk = 20  # Everyone has some baseline risk
        
        # Enhanced risk assessment using AI Medical Safety Checker
        if SAFETY_AVAILABLE and assess_medical_safety:
            try:
                safety_result = assess_medical_safety(
                    normalized_data.get('conditions', []),
                    normalized_data.get('medications', [])
                )
                
                # Adjust risk based on safety assessment
                if safety_result['severity'] == 'high':
                    base_risk *= 1.5
                    print(f"✓ Enhanced Safety Assessment: HIGH RISK - {len(safety_result['risk_factors'])} factors detected")
                elif safety_result['severity'] == 'moderate':
                    base_risk *= 1.3
                    print(f"✓ Enhanced Safety Assessment: MODERATE RISK")
                
                # Store safety recommendations for later use
                normalized_data['_safety_recommendations'] = safety_result['recommendations']
            except Exception as e:
                print(f"⚠ Safety assessment failed: {e}")
        
        # Age-based risk
        age = normalized_data['age']
        if age > 60:
            base_risk += 30
        elif age > 45:
            base_risk += 20
        elif age > 30:
            base_risk += 10
        
        # Condition-based risk
        for condition in normalized_data['conditions']:
            risk_multiplier = self.risk_factors.get(condition, 1.2)
            base_risk *= risk_multiplier
        
        # BMI-based risk
        bmi = normalized_data['bmi']
        if bmi > 30:  # Obese
            base_risk *= 1.5
        elif bmi > 25:  # Overweight
            base_risk *= 1.2
        elif bmi < 18.5:  # Underweight
            base_risk *= 1.3
        
        # Smoking risk
        if normalized_data['smoking']:
            base_risk *= 2.0
        
        # Family history
        if len(normalized_data['family_history']) > 0:
            base_risk *= 1.3
        
        # Past hospitalizations
        if normalized_data['hospitalizations_count'] > 2:
            base_risk *= 1.4
        elif normalized_data['hospitalizations_count'] > 0:
            base_risk *= 1.2
        
        # Cap at 100
        return min(base_risk, 100)
    
    def _filter_eligible_products(self, products: List[InsuranceProduct],
                                  normalized_data: dict, risk_score: float) -> List[InsuranceProduct]:
        """
        Apply eligibility rules to filter products
        """
        eligible = []
        
        # Avoid restricted membership funds by default (unless explicitly allowed)
        restricted_names = {
            'Defence Health', 'Police Health', 'Teachers Health', 'Navy Health',
            "Doctors' Health Fund", 'CBHS Health Fund', 'Reserve Bank Health Society',
            'ACA Health Benefits Fund', 'RT Health Fund', 'Transport Health / Union Health'
        }
        allow_restricted = os.environ.get('ALLOW_RESTRICTED_FUNDS', 'false').lower() in {'1','true','yes'}

        for product in products:
            if not allow_restricted and product.provider in restricted_names:
                continue
            # Rule 1: High-risk patients may not qualify for budget plans
            if risk_score > 70 and product.plan_type == 'HMO' and product.monthly_premium < 250:
                continue
            
            # Rule 2: Low-income users should have access to basic plans
            if normalized_data['income_bracket'] == 'low' and product.monthly_premium > 400:
                continue
            
            # Rule 2b: Very high cost plans are filtered out based on income affordability
            annual_income_map = {
                'low': 25000,
                'middle': 50000,
                'upper-middle': 100000,
                'high': 200000,
            }
            est_income = annual_income_map.get(normalized_data['income_bracket'], 50000)
            est_cost = product.monthly_premium * 12 + product.annual_deductible * 0.5
            cost_ratio = est_cost / est_income if est_income else 1.0
            # Filter out plans that would exceed ~25% of income (typical affordability threshold)
            if cost_ratio > 0.25:
                continue

            # Rule 3: Cancer patients need comprehensive coverage
            if 'cancer' in normalized_data['conditions']:
                if product.coverage_amount < 500000:
                    continue
            
            # Rule 4: Chronic conditions require certain coverage types
            chronic_conditions = {'diabetes', 'hypertension', 'heart disease', 'copd', 'chronic kidney disease'}
            has_chronic = any(c in normalized_data['conditions'] for c in chronic_conditions)
            if has_chronic and 'Chronic disease management' not in product.coverage_details:
                # Still eligible, but will score lower
                pass
            
            eligible.append(product)
        
        return eligible
    
    def _generate_quote(self, product: InsuranceProduct,
                       normalized_data: dict, risk_score: float) -> InsuranceQuote:
        """
        Generate a quote for a specific product
        Calculate scores and rationale
        """
        # Calculate suitability score (0-100)
        suitability_score = self._calculate_suitability(product, normalized_data, risk_score)
        
        # Calculate cost score (0-100, higher = more affordable)
        cost_score = self._calculate_cost_score(product, normalized_data)
        
        # Calculate coverage score (0-100)
        coverage_score = self._calculate_coverage_score(product, normalized_data)
        
        # Optional AI re-scoring and blending
        suitability_score, cost_score, coverage_score = self._maybe_rescore_with_ai(
            product, normalized_data, risk_score,
            suitability_score, cost_score, coverage_score
        )
        
        # Generate rationale
        rationale = self._generate_rationale(
            product, normalized_data, risk_score,
            suitability_score, cost_score, coverage_score
        )
        # Optionally augment with local LLM explanations and persist
        rationale = self._maybe_augment_with_ai(rationale, product, normalized_data, risk_score)
        
        return InsuranceQuote(
            product=product,
            suitability_score=suitability_score,
            cost_score=cost_score,
            coverage_score=coverage_score,
            rationale=rationale
        )

    def _maybe_augment_with_ai(self, baseline: str, product: InsuranceProduct,
                                normalized_data: dict, risk_score: float) -> str:
        """Append AI-generated explanations (llama & mistral) when enabled.

        Controlled by env USE_LLM_EXPLAINER in {1,true,yes}. Saves outputs to
        web_app/UC1_models/reason.
        """
        if not normalized_data.get('use_ai_explainer'):
            return baseline
        try:
            from ai_explainer import generate_ai_rationales
            save_dir = os.path.join(os.path.dirname(__file__), 'UC1_models', 'reason')
            req_id = normalized_data.get('request_id', 'REQ')
            product_id = getattr(product, 'product_id', 'PID')
            ration = generate_ai_rationales(
                product=product.to_dict(),
                profile=normalized_data,
                risk_score=risk_score,
                save_dir=save_dir,
                request_id=req_id,
                product_id=product_id,
                progress_cb=self.progress_cb,
                provider=product.provider,
                current=self.idx + 1,
                total=self.total_products,
            )
            mistral_txt = (ration.get('mistral:7b-instruct') or '').strip()
            pieces = [baseline]
            if mistral_txt:
                safe_txt = _html.escape(mistral_txt)
                ai_html = (
                    f"<div class=\"mt-1\">"
                    f"<span class=\"badge bg-info text-dark\">AI</span> "
                    f"<span class=\"text-primary\"><strong><em>{safe_txt}</em></strong></span> "
                    f"<small class=\"text-muted\">— analyzed by AI</small>"
                    f"</div>"
                )
                pieces.append(ai_html)
            # update progress proportionally for explanation stage (75→90)
            if self.progress_cb and self.total_products:
                try:
                    pct = 75 + int(15 * (self.idx + 1) / self.total_products)
                    self.progress_cb(pct, f"AI analyzer: explanation for {product.provider} ({self.idx + 1}/{self.total_products})")
                except Exception:
                    pass
            return "<br/>".join(pieces)
        except Exception:
            return baseline
    
    def _calculate_suitability(self, product: InsuranceProduct,
                              normalized_data: dict, risk_score: float) -> float:
        """Calculate how suitable the product is for the user"""
        score = 50  # Start at middle
        
        # Match plan type to user needs
        if risk_score > 60:
            # High-risk users benefit from PPO/EPO with more flexibility
            if product.plan_type in ['PPO', 'EPO']:
                score += 20
        else:
            # Low-risk users can use HMO for cost savings
            if product.plan_type == 'HMO':
                score += 15
        
        # Match coverage to conditions
        conditions = normalized_data['conditions']
        if 'diabetes' in conditions or 'hypertension' in conditions:
            if 'Chronic disease management' in product.coverage_details:
                score += 15
        
        if 'cancer' in conditions:
            if 'Advanced cancer treatment' in product.coverage_details:
                score += 25
            elif product.coverage_amount >= 500000:
                score += 15
        
        # Mental health consideration
        if len(conditions) > 2:  # Multiple conditions may need mental health support
            if 'Mental health services' in product.coverage_details:
                score += 10
        
        # Income match
        income_bracket = normalized_data['income_bracket']
        if income_bracket == 'low' and product.monthly_premium < 300:
            score += 15
        elif income_bracket == 'high' and product.coverage_amount > 750000:
            score += 10
        
        return min(max(score, 0), 100)

    def _maybe_rescore_with_ai(self, product: InsuranceProduct, normalized_data: dict, risk_score: float,
                                suit: float, cost: float, cov: float) -> Tuple[float, float, float]:
        """Blend AI scores with rule-based scores when enabled.

        Enabled when user checked AI analyzer or env USE_AI_SCORER=true.
        Blend weights default to 0.6 rule / 0.4 AI. Adds small diversity jitter.
        """
        if not (normalized_data.get('use_ai_explainer') or os.environ.get('USE_AI_SCORER', 'false').lower() in {'1','true','yes'}):
            return suit, cost, cov
        try:
            from ai_explainer import score_plan_with_ai
            scores = score_plan_with_ai(product.to_dict(), normalized_data, risk_score, progress_cb=self.progress_cb)
            if not scores:
                return suit, cost, cov
            w_rule, w_ai = 0.6, 0.4
            new_suit = w_rule * suit + w_ai * scores.get('suitability', suit)
            new_cost = w_rule * cost + w_ai * scores.get('cost', cost)
            new_cov = w_rule * cov + w_ai * scores.get('coverage', cov)
            # diversity jitter based on feature richness
            richness = len(product.coverage_details) - len(product.exclusions)
            jitter = max(-3, min(3, richness // 4))
            new_suit += jitter * 0.5
            new_cov += jitter * 0.5
            # update progress proportionally for scoring stage (55→75)
            if self.progress_cb and self.total_products:
                try:
                    pct = 55 + int(20 * (self.idx + 1) / self.total_products)
                    self.progress_cb(pct, f"AI analyzer: scoring {product.provider} ({self.idx + 1}/{self.total_products})")
                except Exception:
                    pass
            return float(max(0, min(100, round(new_suit, 1)))), float(max(0, min(100, round(new_cost, 1)))), float(max(0, min(100, round(new_cov, 1))))
        except Exception:
            return suit, cost, cov
    
    def _calculate_cost_score(self, product: InsuranceProduct,
                             normalized_data: dict) -> float:
        """Calculate affordability score (higher = more affordable)"""
        annual_income = {
            'low': 25000,
            'middle': 50000,
            'upper-middle': 100000,
            'high': 200000
        }.get(normalized_data['income_bracket'], 50000)
        
        # Calculate annual cost
        annual_premium = product.monthly_premium * 12
        estimated_annual_cost = annual_premium + (product.annual_deductible * 0.5)  # Assume 50% of deductible used
        
        # Cost as percentage of income
        cost_ratio = estimated_annual_cost / annual_income
        
        # Score based on affordability (inverse relationship)
        if cost_ratio < 0.05:
            score = 100
        elif cost_ratio < 0.10:
            score = 80
        elif cost_ratio < 0.15:
            score = 60
        elif cost_ratio < 0.20:
            score = 40
        else:
            score = 20
        
        return score
    
    def _calculate_coverage_score(self, product: InsuranceProduct,
                                 normalized_data: dict) -> float:
        """Calculate how comprehensive the coverage is"""
        score = 0
        
        # Base score from coverage amount
        if product.coverage_amount >= 1000000:
            score += 30
        elif product.coverage_amount >= 500000:
            score += 25
        elif product.coverage_amount >= 250000:
            score += 15
        else:
            score += 5
        
        # Score from coverage details count
        coverage_count = len(product.coverage_details)
        score += min(coverage_count * 5, 30)  # Max 30 points
        
        # Penalty for exclusions
        exclusion_count = len(product.exclusions)
        score -= min(exclusion_count * 3, 15)  # Max -15 points
        
        # Out-of-pocket maximum (lower is better)
        if product.max_out_of_pocket < 5000:
            score += 20
        elif product.max_out_of_pocket < 7500:
            score += 15
        else:
            score += 5
        
        # Deductible (lower is better)
        if product.annual_deductible < 2000:
            score += 15
        elif product.annual_deductible < 3500:
            score += 10
        else:
            score += 5
        
        return min(max(score, 0), 100)
    
    def _generate_rationale(self, product: InsuranceProduct,
                          normalized_data: dict, risk_score: float,
                          suitability_score: float, cost_score: float,
                          coverage_score: float) -> str:
        """Generate human-readable explanation for the quote"""
        rationale_parts = []
        
        # Opening statement
        rationale_parts.append(
            f"This {product.plan_type} plan from {product.provider} "
            f"has been matched to your profile with an overall score of "
            f"{round((suitability_score + cost_score + coverage_score) / 3, 1)}/100."
        )
        
        # Suitability explanation
        if suitability_score >= 70:
            rationale_parts.append(
                f"This plan is highly suitable for your health profile (risk level: {round(risk_score, 1)}/100). "
            )
        elif suitability_score >= 50:
            rationale_parts.append(
                f"This plan is moderately suitable for your needs. "
            )
        else:
            rationale_parts.append(
                f"This plan may not fully match your requirements. "
            )
        
        # Cost explanation
        if cost_score >= 70:
            rationale_parts.append(
                f"The monthly premium of ${product.monthly_premium} is highly affordable for your income bracket. "
            )
        elif cost_score >= 50:
            rationale_parts.append(
                f"The monthly premium of ${product.monthly_premium} is manageable for your budget. "
            )
        else:
            rationale_parts.append(
                f"The monthly premium of ${product.monthly_premium} may be challenging for your budget. "
            )
        
        # Coverage highlights
        key_coverages = product.coverage_details[:3]
        rationale_parts.append(
            f"Key benefits include: {', '.join(key_coverages)}. "
        )
        
        # Condition-specific recommendations
        conditions = normalized_data['conditions']
        if 'diabetes' in conditions or 'hypertension' in conditions:
            if 'Chronic disease management' in product.coverage_details:
                rationale_parts.append(
                    "This plan includes chronic disease management, which is important for your ongoing care. "
                )
        
        if 'cancer' in conditions:
            if product.coverage_amount >= 500000:
                rationale_parts.append(
                    f"With ${product.coverage_amount:,} in coverage, this plan provides substantial protection for cancer treatment. "
                )
        
        # Out-of-pocket summary
        rationale_parts.append(
            f"Your maximum annual out-of-pocket cost would be ${product.max_out_of_pocket:,} "
            f"(including ${product.annual_deductible:,} deductible)."
        )
        
        return ' '.join(rationale_parts)


# ================================
# Main Processing Function
# ================================

def process_insurance_quote_request(request: QuoteRequest, progress_cb=None) -> Tuple[bool, List[InsuranceQuote], str]:
    """
    Process insurance quote request through AI engine
    Returns: (success, quotes, message)
    """
    try:
        if progress_cb:
            try:
                progress_cb(10, 'Normalizing data')
            except Exception:
                pass
        engine = InsuranceQuoteEngine()
        # Manual step-wise progress
        normalized = engine._normalize_data(request)
        if progress_cb:
            try:
                progress_cb(30, 'Assessing risk and safety')
            except Exception:
                pass
        risk_score = engine._assess_risk(normalized)
        if progress_cb:
            try:
                progress_cb(55, 'Applying eligibility rules')
            except Exception:
                pass
        eligible = engine._filter_eligible_products(engine.products, normalized, risk_score)
        engine.progress_cb = progress_cb
        engine.total_products = max(1, len(eligible))
        if progress_cb:
            try:
                progress_cb(56, 'Scoring plans')
            except Exception:
                pass
        quotes = []
        for i, product in enumerate(eligible):
            engine.idx = i
            quotes.append(engine._generate_quote(product, normalized, risk_score))
        if progress_cb:
            try:
                progress_cb(75, 'Ranking plans')
            except Exception:
                pass
        quotes.sort(key=lambda q: q.overall_score, reverse=True)

        # Decide result set size (AI-assisted)
        top_k = None
        if normalized.get('use_ai_explainer'):
            try:
                if progress_cb:
                    try:
                        progress_cb(78, 'Selecting number of results')
                    except Exception:
                        pass
                from ai_explainer import decide_top_k
                top_k = decide_top_k(normalized, risk_score, len(quotes), progress_cb=progress_cb)
            except Exception:
                top_k = None
        if top_k is None:
            # Fallback heuristic
            top_k = 10
            if risk_score >= 70:
                top_k = 6
            elif risk_score >= 55:
                top_k = 8
            elif risk_score <= 35:
                top_k = 12
        quotes = quotes[:max(1, min(top_k, len(quotes)))]

        if not quotes:
            return False, [], "No suitable insurance products found for your profile. Please consult with a human advisor."
        
        # Update request status
        request.status = 'completed'
        request.quotes = quotes
        if progress_cb:
            try:
                progress_cb(100, f"Completed — showing top {len(quotes)} plans")
            except Exception:
                pass
        
        return True, quotes, f"Successfully generated {len(quotes)} insurance quotes."
        
    except Exception as e:
        request.status = 'failed'
        return False, [], f"Error processing quote request: {str(e)}"

