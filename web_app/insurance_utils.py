"""
Utility functions for insurance quote feature
Includes cost breakdown, cost simulation, comparison, and PDF generation
"""

from typing import List, Dict
from insurance_models import InsuranceQuote, InsuranceProduct


def generate_cost_breakdown(product: InsuranceProduct, usage_scenario: str = 'typical') -> Dict:
    """
    Generate detailed cost breakdown for an insurance product
    
    Args:
        product: Insurance product to analyze
        usage_scenario: 'minimal', 'typical', 'heavy', 'catastrophic'
    
    Returns:
        Dictionary with detailed cost projections
    """
    # Define usage scenarios
    scenarios = {
        'minimal': {
            'doctor_visits': 2,
            'specialist_visits': 0,
            'er_visits': 0,
            'hospital_days': 0,
            'prescriptions': 12,
            'lab_tests': 2
        },
        'typical': {
            'doctor_visits': 4,
            'specialist_visits': 2,
            'er_visits': 0,
            'hospital_days': 0,
            'prescriptions': 24,
            'lab_tests': 4
        },
        'heavy': {
            'doctor_visits': 8,
            'specialist_visits': 4,
            'er_visits': 1,
            'hospital_days': 2,
            'prescriptions': 48,
            'lab_tests': 8
        },
        'catastrophic': {
            'doctor_visits': 12,
            'specialist_visits': 6,
            'er_visits': 2,
            'hospital_days': 7,
            'prescriptions': 60,
            'lab_tests': 12
        }
    }
    
    usage = scenarios.get(usage_scenario, scenarios['typical'])
    
    # Calculate costs
    annual_premium = product.monthly_premium * 12
    
    # Estimate out-of-pocket costs based on usage
    doctor_cost = usage['doctor_visits'] * product.copay
    specialist_cost = usage['specialist_visits'] * (product.copay * 1.5)
    er_cost = usage['er_visits'] * 500 * (product.coinsurance / 100)
    hospital_cost = usage['hospital_days'] * 2000 * (product.coinsurance / 100)
    prescription_cost = usage['prescriptions'] * 25  # Average $25 per prescription
    lab_cost = usage['lab_tests'] * product.copay
    
    total_oop_before_deductible = (
        doctor_cost + specialist_cost + er_cost + 
        hospital_cost + prescription_cost + lab_cost
    )
    
    # Apply deductible
    if total_oop_before_deductible > product.annual_deductible:
        total_oop = min(total_oop_before_deductible, product.max_out_of_pocket)
    else:
        total_oop = total_oop_before_deductible
    
    total_annual_cost = annual_premium + total_oop
    
    return {
        'scenario': usage_scenario,
        'breakdown': {
            'annual_premium': annual_premium,
            'monthly_premium': product.monthly_premium,
            'deductible': product.annual_deductible,
            'max_out_of_pocket': product.max_out_of_pocket,
            'estimated_oop': round(total_oop, 2),
            'total_annual_cost': round(total_annual_cost, 2)
        },
        'usage_details': {
            'doctor_visits': {
                'count': usage['doctor_visits'],
                'cost_per_visit': product.copay,
                'total': doctor_cost
            },
            'specialist_visits': {
                'count': usage['specialist_visits'],
                'cost_per_visit': product.copay * 1.5,
                'total': specialist_cost
            },
            'er_visits': {
                'count': usage['er_visits'],
                'estimated_cost': er_cost
            },
            'hospital_days': {
                'count': usage['hospital_days'],
                'estimated_cost': hospital_cost
            },
            'prescriptions': {
                'count': usage['prescriptions'],
                'estimated_cost': prescription_cost
            },
            'lab_tests': {
                'count': usage['lab_tests'],
                'cost_per_test': product.copay,
                'total': lab_cost
            }
        }
    }


def simulate_cost_scenarios(product: InsuranceProduct) -> Dict:
    """
    Simulate costs across all usage scenarios
    
    Returns:
        Dictionary with all scenario projections
    """
    scenarios = {}
    for scenario_name in ['minimal', 'typical', 'heavy', 'catastrophic']:
        scenarios[scenario_name] = generate_cost_breakdown(product, scenario_name)
    
    return scenarios


def compare_quotes(quotes: List[InsuranceQuote]) -> Dict:
    """
    Generate comparison matrix for multiple quotes
    
    Args:
        quotes: List of InsuranceQuote objects to compare
    
    Returns:
        Dictionary with comparison data
    """
    if not quotes:
        return {'error': 'No quotes to compare'}
    
    comparison = {
        'products': [],
        'metrics': {
            'monthly_premium': {
                'label': 'Monthly Premium',
                'values': [],
                'best_index': None,
                'unit': '$'
            },
            'annual_deductible': {
                'label': 'Annual Deductible',
                'values': [],
                'best_index': None,
                'unit': '$'
            },
            'max_out_of_pocket': {
                'label': 'Max Out-of-Pocket',
                'values': [],
                'best_index': None,
                'unit': '$'
            },
            'coverage_amount': {
                'label': 'Coverage Amount',
                'values': [],
                'best_index': None,
                'unit': '$'
            },
            'suitability_score': {
                'label': 'Suitability Score',
                'values': [],
                'best_index': None,
                'unit': '/100'
            },
            'cost_score': {
                'label': 'Cost Score',
                'values': [],
                'best_index': None,
                'unit': '/100'
            },
            'coverage_score': {
                'label': 'Coverage Score',
                'values': [],
                'best_index': None,
                'unit': '/100'
            },
            'overall_score': {
                'label': 'Overall Score',
                'values': [],
                'best_index': None,
                'unit': '/100'
            }
        },
        'coverage_comparison': [],
        'exclusion_comparison': []
    }
    
    # Helper to ensure numeric value
    def to_float(v):
        if v is None:
            return 0.0
        if isinstance(v, (int, float)):
            return float(v)
        try:
            return float(v)
        except (ValueError, TypeError):
            return 0.0
    
    # Extract data for comparison
    for quote in quotes:
        comparison['products'].append({
            'name': quote.product.name,
            'provider': quote.product.provider,
            'plan_type': quote.product.plan_type,
            'product_id': getattr(quote.product, 'product_id', '')
        })
        
        comparison['metrics']['monthly_premium']['values'].append(to_float(quote.product.monthly_premium))
        comparison['metrics']['annual_deductible']['values'].append(to_float(quote.product.annual_deductible))
        comparison['metrics']['max_out_of_pocket']['values'].append(to_float(quote.product.max_out_of_pocket))
        comparison['metrics']['coverage_amount']['values'].append(to_float(quote.product.coverage_amount))
        comparison['metrics']['suitability_score']['values'].append(to_float(quote.suitability_score))
        comparison['metrics']['cost_score']['values'].append(to_float(quote.cost_score))
        comparison['metrics']['coverage_score']['values'].append(to_float(quote.coverage_score))
        comparison['metrics']['overall_score']['values'].append(to_float(quote.overall_score))
    
    # Find best values (lower is better for costs, higher for scores and coverage)
    comparison['metrics']['monthly_premium']['best_index'] = comparison['metrics']['monthly_premium']['values'].index(
        min(comparison['metrics']['monthly_premium']['values'])
    )
    comparison['metrics']['annual_deductible']['best_index'] = comparison['metrics']['annual_deductible']['values'].index(
        min(comparison['metrics']['annual_deductible']['values'])
    )
    comparison['metrics']['max_out_of_pocket']['best_index'] = comparison['metrics']['max_out_of_pocket']['values'].index(
        min(comparison['metrics']['max_out_of_pocket']['values'])
    )
    comparison['metrics']['coverage_amount']['best_index'] = comparison['metrics']['coverage_amount']['values'].index(
        max(comparison['metrics']['coverage_amount']['values'])
    )
    comparison['metrics']['suitability_score']['best_index'] = comparison['metrics']['suitability_score']['values'].index(
        max(comparison['metrics']['suitability_score']['values'])
    )
    comparison['metrics']['cost_score']['best_index'] = comparison['metrics']['cost_score']['values'].index(
        max(comparison['metrics']['cost_score']['values'])
    )
    comparison['metrics']['coverage_score']['best_index'] = comparison['metrics']['coverage_score']['values'].index(
        max(comparison['metrics']['coverage_score']['values'])
    )
    comparison['metrics']['overall_score']['best_index'] = comparison['metrics']['overall_score']['values'].index(
        max(comparison['metrics']['overall_score']['values'])
    )
    
    # Compare coverage details
    all_coverages = set()
    for quote in quotes:
        details = quote.product.coverage_details
        if not isinstance(details, (list, tuple, set)):
            details = list(details) if hasattr(details, '__iter__') else []
        all_coverages.update(details)
    
    for coverage in sorted(all_coverages):
        coverage_row = {'name': coverage, 'covered_by': []}
        for quote in quotes:
            details = quote.product.coverage_details
            if not isinstance(details, (list, tuple, set)):
                details = list(details) if hasattr(details, '__iter__') else []
            coverage_row['covered_by'].append(coverage in details)
        comparison['coverage_comparison'].append(coverage_row)
    
    # Compare exclusions
    all_exclusions = set()
    for quote in quotes:
        exclusions = quote.product.exclusions
        if not isinstance(exclusions, (list, tuple, set)):
            exclusions = list(exclusions) if hasattr(exclusions, '__iter__') else []
        all_exclusions.update(exclusions)
    
    for exclusion in sorted(all_exclusions):
        exclusion_row = {'name': exclusion, 'excluded_by': []}
        for quote in quotes:
            exclusions = quote.product.exclusions
            if not isinstance(exclusions, (list, tuple, set)):
                exclusions = list(exclusions) if hasattr(exclusions, '__iter__') else []
            exclusion_row['excluded_by'].append(exclusion in exclusions)
        comparison['exclusion_comparison'].append(exclusion_row)
    
    return comparison


def generate_pdf_summary(quote_request, quotes: List[InsuranceQuote]) -> str:
    """
    Generate HTML content for PDF export
    (In production, use a library like WeasyPrint or ReportLab)
    
    Returns:
        HTML string ready for PDF conversion
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Insurance Quote Summary - {quote_request.request_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            h1 {{ color: #007bff; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
            h2 {{ color: #0056b3; margin-top: 30px; }}
            .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
            .quote-card {{ border: 2px solid #dee2e6; padding: 20px; margin: 20px 0; border-radius: 8px; page-break-inside: avoid; }}
            .score {{ display: inline-block; padding: 5px 10px; background: #28a745; color: white; border-radius: 4px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ border: 1px solid #dee2e6; padding: 10px; text-align: left; }}
            th {{ background: #e9ecef; font-weight: bold; }}
            .footer {{ margin-top: 50px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 0.9em; color: #6c757d; }}
        </style>
    </head>
    <body>
        <h1>Insurance Quote Summary</h1>
        
        <div class="header">
            <p><strong>Request ID:</strong> {quote_request.request_id}</p>
            <p><strong>Generated:</strong> {quote_request.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Status:</strong> {quote_request.status.replace('_', ' ').title()}</p>
            <p><strong>Number of Quotes:</strong> {len(quotes)}</p>
        </div>
        
        <h2>Your Profile Summary</h2>
        <table>
            <tr>
                <th>Health Conditions</th>
                <td>{', '.join(quote_request.health_data.conditions) if quote_request.health_data.conditions else 'None reported'}</td>
            </tr>
            <tr>
                <th>Current Medications</th>
                <td>{', '.join(quote_request.health_data.medications) if quote_request.health_data.medications else 'None reported'}</td>
            </tr>
            <tr>
                <th>Annual Income</th>
                <td>${quote_request.income_details.annual_income:,}</td>
            </tr>
            <tr>
                <th>Employment Status</th>
                <td>{quote_request.income_details.employment_status.replace('_', ' ').title()}</td>
            </tr>
        </table>
    """
    
    for idx, quote in enumerate(quotes, 1):
        html += f"""
        <div class="quote-card">
            <h2>Quote #{idx}: {quote.product.name}</h2>
            <p><strong>Provider:</strong> {quote.product.provider} | <strong>Plan Type:</strong> {quote.product.plan_type}</p>
            <p><span class="score">Overall Score: {quote.overall_score}/100</span></p>
            
            <h3>Pricing</h3>
            <table>
                <tr>
                    <th>Monthly Premium</th>
                    <td>${quote.product.monthly_premium}</td>
                </tr>
                <tr>
                    <th>Annual Deductible</th>
                    <td>${quote.product.annual_deductible:,}</td>
                </tr>
                <tr>
                    <th>Copay</th>
                    <td>${quote.product.copay}</td>
                </tr>
                <tr>
                    <th>Max Out-of-Pocket</th>
                    <td>${quote.product.max_out_of_pocket:,}</td>
                </tr>
                <tr>
                    <th>Coverage Amount</th>
                    <td>${quote.product.coverage_amount:,}</td>
                </tr>
            </table>
            
            <h3>Score Breakdown</h3>
            <table>
                <tr>
                    <th>Suitability</th>
                    <td>{quote.suitability_score}/100</td>
                </tr>
                <tr>
                    <th>Cost</th>
                    <td>{quote.cost_score}/100</td>
                </tr>
                <tr>
                    <th>Coverage</th>
                    <td>{quote.coverage_score}/100</td>
                </tr>
            </table>
            
            <h3>Why This Plan?</h3>
            <p>{quote.rationale}</p>
            
            <h3>Coverage Includes</h3>
            <ul>
                {''.join(f'<li>{detail}</li>' for detail in quote.product.coverage_details)}
            </ul>
            
            <h3>Exclusions</h3>
            <ul>
                {''.join(f'<li>{exclusion}</li>' for exclusion in quote.product.exclusions)}
            </ul>
        </div>
        """
    
    html += """
        <div class="footer">
            <p>This quote summary was generated by the Healthcare AI System.</p>
            <p>Please consult with a licensed insurance advisor before making final decisions.</p>
            <p>Quotes are subject to change and final approval by insurance providers.</p>
        </div>
    </body>
    </html>
    """
    
    return html

