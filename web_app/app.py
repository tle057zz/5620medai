"""
Flask Web Application for Clinical AI Assistance System
Main application file with authentication and role-based access
"""

from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

# Import our models and forms
from models import User, get_user_by_username, example_users
from forms import LoginForm, InsuranceQuoteForm
from insurance_models import (
    QuoteRequest, HealthData, MedicalHistory, IncomeDetails,
    save_quote_request, get_quote_request, get_user_quote_requests
)
from insurance_engine import process_insurance_quote_request
from insurance_utils import (
    generate_cost_breakdown, simulate_cost_scenarios,
    compare_quotes, generate_pdf_summary
)
from medical_document_processor import (
    process_uploaded_document, assess_medical_safety, AI_MEDICAL_AVAILABLE
)
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    for user in example_users.values():
        if user.id == user_id:
            return user
    return None


# ================================
# Role-Based Access Decorators
# ================================

def role_required(*roles):
    """Decorator to require specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ================================
# Authentication Routes
# ================================

@app.route('/')
def index():
    """Home page - redirect to login or dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_username(form.username.data)
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            
            # Log successful login
            print(f"✓ User logged in: {user.username} ({user.role})")
            
            flash(f'Welcome back, {user.get_display_name()}!', 'success')
            
            # Redirect to requested page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    username = current_user.username
    logout_user()
    flash(f'You have been logged out successfully.', 'info')
    print(f"✓ User logged out: {username}")
    return redirect(url_for('login'))


# ================================
# Dashboard Routes (Role-Based)
# ================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - routes to role-specific dashboard"""
    if current_user.role == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    elif current_user.role == 'patient':
        return redirect(url_for('patient_dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid user role.', 'danger')
        return redirect(url_for('logout'))


@app.route('/dashboard/doctor')
@login_required
@role_required('doctor')
def doctor_dashboard():
    """Doctor dashboard - access to clinical AI tools"""
    return render_template('dashboard_doctor.html', user=current_user)


@app.route('/dashboard/patient')
@login_required
@role_required('patient')
def patient_dashboard():
    """Patient dashboard - view medical records and AI analysis"""
    return render_template('dashboard_patient.html', user=current_user)


@app.route('/dashboard/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    """Admin dashboard - system management"""
    # Get all users for display
    all_users = list(example_users.values())
    return render_template('dashboard_admin.html', user=current_user, all_users=all_users)


# ================================
# API Routes (for future integration)
# ================================

@app.route('/api/process-document', methods=['POST'])
@login_required
@role_required('doctor', 'admin')
def process_document():
    """API endpoint to process medical documents through AI pipeline"""
    # TODO: Integrate with ai_medical pipeline
    return {'status': 'success', 'message': 'Document processing not yet implemented'}


@app.route('/api/get-patient-records', methods=['GET'])
@login_required
def get_patient_records():
    """API endpoint to retrieve patient records"""
    # TODO: Implement patient record retrieval
    return {'status': 'success', 'records': []}


# ================================
# User Management (Admin Only)
# ================================

@app.route('/users')
@login_required
@role_required('admin')
def list_users():
    """List all users (admin only)"""
    users = list(example_users.values())
    return render_template('users_list.html', users=users)


# ================================
# Insurance Quote Feature (Chadwick Ng)
# ================================

@app.route('/insurance/request-quote', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def request_insurance_quote():
    """
    Request Insurance Quote - Main entry point (PATIENT ONLY)
    Collects user health data, medical history, and income details
    NOW WITH AI MEDICAL DOCUMENT PROCESSING!
    """
    form = InsuranceQuoteForm()
    
    # Store document processing results in session
    document_data = session.get('document_data', {})
    
    if form.validate_on_submit():
        try:
            # Check if user uploaded a medical document
            uploaded_file = form.medical_document.data
            if uploaded_file and uploaded_file.filename:
                # Process document through AI medical pipeline
                filename = secure_filename(uploaded_file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                uploaded_file.save(file_path)
                
                print(f"✓ Processing uploaded document: {filename}")
                doc_result = process_uploaded_document(file_path)
                
                if doc_result['success']:
                    # Store extracted data in session for user review
                    session['document_data'] = doc_result
                    flash(f"✓ Document processed! Extracted {len(doc_result['conditions'])} conditions and {len(doc_result['medications'])} medications.", 'success')
                    print(f"✓ Extracted: {doc_result['conditions']}, {doc_result['medications']}")
                else:
                    flash(f"⚠ Document processing failed: {doc_result.get('error')}", 'warning')
                
                # Clean up uploaded file
                try:
                    os.remove(file_path)
                except:
                    pass
            
            # Create a new quote request
            quote_request = QuoteRequest(user_id=current_user.id)
            
            # Populate health data
            health_data = HealthData()
            
            # Parse conditions (split by comma or newline)
            conditions_text = form.current_conditions.data or ''
            health_data.conditions = [c.strip() for c in conditions_text.replace('\n', ',').split(',') if c.strip()]
            
            # Parse medications
            medications_text = form.current_medications.data or ''
            health_data.medications = [m.strip() for m in medications_text.replace('\n', ',').split(',') if m.strip()]
            
            health_data.bmi = form.bmi.data
            health_data.blood_pressure = form.blood_pressure.data
            health_data.cholesterol = form.cholesterol.data
            health_data.glucose = form.glucose.data
            health_data.smoking_status = form.smoking_status.data
            health_data.alcohol_consumption = form.alcohol_consumption.data
            
            quote_request.health_data = health_data
            
            # Populate medical history
            medical_history = MedicalHistory()
            
            past_cond_text = form.past_conditions.data or ''
            medical_history.past_conditions = [c.strip() for c in past_cond_text.replace('\n', ',').split(',') if c.strip()]
            
            surgeries_text = form.surgeries.data or ''
            medical_history.surgeries = [s.strip() for s in surgeries_text.replace('\n', ',').split(',') if s.strip()]
            
            hosp_text = form.hospitalizations.data or ''
            medical_history.hospitalizations = [h.strip() for h in hosp_text.replace('\n', ',').split(',') if h.strip()]
            
            family_hist_text = form.family_history.data or ''
            medical_history.family_history = [f.strip() for f in family_hist_text.replace('\n', ',').split(',') if f.strip()]
            
            quote_request.medical_history = medical_history
            
            # Populate income details
            income_details = IncomeDetails(
                annual_income=form.annual_income.data,
                employment_status=form.employment_status.data,
                occupation=form.occupation.data or ''
            )
            income_details.dependents = form.dependents.data or 0
            
            quote_request.income_details = income_details
            
            # Record consent
            quote_request.consent_given = form.consent_data_use.data and form.consent_privacy.data
            
            # Validate that consent is given
            if not quote_request.consent_given:
                flash('You must provide consent to process your data.', 'danger')
                return render_template('insurance_quote_form.html', form=form)
            
            # Save the request
            quote_request.status = 'processing'
            request_id = save_quote_request(quote_request)
            
            print(f"✓ Insurance quote request created: {request_id} for user {current_user.username}")
            
            # Process the quote request through AI engine
            success, quotes, message = process_insurance_quote_request(quote_request)
            
            if success:
                flash(f'Success! {message}', 'success')
                return redirect(url_for('view_insurance_quotes', request_id=request_id))
            else:
                flash(f'Unable to generate quotes: {message}', 'warning')
                return redirect(url_for('insurance_no_results', request_id=request_id))
                
        except Exception as e:
            print(f"✗ Error processing insurance quote: {e}")
            flash(f'An error occurred while processing your request: {str(e)}', 'danger')
            return render_template('insurance_quote_form.html', form=form)
    
    return render_template('insurance_quote_form.html', form=form, ai_medical_available=AI_MEDICAL_AVAILABLE)


@app.route('/insurance/prefill-from-document')
@login_required
@role_required('patient')
def prefill_from_document():
    """
    Pre-fill form with data extracted from uploaded medical document (PATIENT ONLY)
    Uses AI Medical Pipeline: OCR → NER → Entity Linking
    """
    document_data = session.get('document_data', {})
    
    if not document_data or not document_data.get('success'):
        flash('No document data available to pre-fill.', 'warning')
        return redirect(url_for('request_insurance_quote'))
    
    # Create form instance
    form = InsuranceQuoteForm()
    
    # Pre-fill conditions
    if document_data.get('conditions'):
        form.current_conditions.data = ', '.join(document_data['conditions'])
    
    # Pre-fill medications  
    if document_data.get('medications'):
        form.current_medications.data = ', '.join(document_data['medications'])
    
    # Pre-fill observations (vitals)
    obs = document_data.get('observations', {})
    if obs.get('bmi'):
        form.bmi.data = obs['bmi']
    if obs.get('blood_pressure'):
        form.blood_pressure.data = obs['blood_pressure']
    if obs.get('glucose'):
        form.glucose.data = obs['glucose']
    if obs.get('cholesterol'):
        form.cholesterol.data = obs['cholesterol']
    
    flash('✓ Form pre-filled with data from your medical document!', 'success')
    return render_template('insurance_quote_form.html', form=form, 
                          ai_medical_available=AI_MEDICAL_AVAILABLE,
                          prefilled=True)


@app.route('/insurance/quotes/<request_id>')
@login_required
def view_insurance_quotes(request_id):
    """
    Display ranked insurance quotes for a request
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        flash('Quote request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify user owns this request
    if quote_request.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to view this request.', 'danger')
        return redirect(url_for('dashboard'))
    
    if not quote_request.quotes:
        flash('No quotes available for this request.', 'warning')
        return redirect(url_for('insurance_no_results', request_id=request_id))
    
    return render_template('insurance_quotes_display.html', 
                          quote_request=quote_request,
                          quotes=quote_request.quotes)


@app.route('/insurance/no-results/<request_id>')
@login_required
def insurance_no_results(request_id):
    """
    Display when no suitable insurance products are found
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        flash('Quote request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('insurance_no_results.html', quote_request=quote_request)


@app.route('/insurance/history')
@login_required
@role_required('patient')
def insurance_quote_history():
    """
    View user's insurance quote history (PATIENT ONLY)
    """
    user_requests = get_user_quote_requests(current_user.id)
    return render_template('insurance_history.html', requests=user_requests)


@app.route('/insurance/download/<request_id>')
@login_required
def download_insurance_quotes(request_id):
    """
    Download insurance quotes as JSON
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        flash('Quote request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify user owns this request
    if quote_request.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to download this request.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Return as JSON download
    return jsonify(quote_request.to_dict())


@app.route('/insurance/cost-breakdown/<request_id>/<product_id>')
@login_required
def insurance_cost_breakdown(request_id, product_id):
    """
    Display detailed cost breakdown for a specific insurance product
    Use Case Step: Extension Path 2 - User Requests Cost Breakdown
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        flash('Quote request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify user owns this request
    if quote_request.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to view this request.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Find the quote for this product
    target_quote = None
    for quote in quote_request.quotes:
        if quote.product.product_id == product_id:
            target_quote = quote
            break
    
    if not target_quote:
        flash('Product not found in this request.', 'danger')
        return redirect(url_for('view_insurance_quotes', request_id=request_id))
    
    # Generate cost simulations for all scenarios
    cost_scenarios = simulate_cost_scenarios(target_quote.product)
    
    return render_template('insurance_cost_breakdown.html',
                          quote_request=quote_request,
                          quote=target_quote,
                          cost_scenarios=cost_scenarios)


@app.route('/insurance/compare/<request_id>')
@login_required
def insurance_compare(request_id):
    """
    Compare multiple insurance quotes side-by-side
    Use Case Step: Nested Path 8 - Review & Save/Download (Compare)
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        flash('Quote request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify user owns this request
    if quote_request.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to view this request.', 'danger')
        return redirect(url_for('dashboard'))
    
    if not quote_request.quotes:
        flash('No quotes available to compare.', 'warning')
        return redirect(url_for('view_insurance_quotes', request_id=request_id))
    
    # Get selected quote indices from query params (default to all)
    selected_indices = request.args.get('quotes', '')
    if selected_indices:
        try:
            indices = [int(i) for i in selected_indices.split(',')]
            selected_quotes = [quote_request.quotes[i] for i in indices if i < len(quote_request.quotes)]
        except (ValueError, IndexError):
            selected_quotes = quote_request.quotes
    else:
        selected_quotes = quote_request.quotes
    
    # Generate comparison data
    comparison_data = compare_quotes(selected_quotes)
    
    return render_template('insurance_compare.html',
                          quote_request=quote_request,
                          comparison=comparison_data,
                          selected_quotes=selected_quotes)


@app.route('/insurance/favorite/<request_id>/<product_id>', methods=['POST'])
@login_required
@role_required('patient')
def toggle_favorite(request_id, product_id):
    """
    Mark/unmark a quote as favorite (PATIENT ONLY)
    Use Case Step: Nested Path 8 - User saves favorites to profile
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        return jsonify({'success': False, 'message': 'Quote request not found'}), 404
    
    # Verify user owns this request
    if quote_request.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    # Toggle favorite
    if product_id in quote_request.favorites:
        quote_request.favorites.remove(product_id)
        is_favorite = False
    else:
        quote_request.favorites.append(product_id)
        is_favorite = True
    
    return jsonify({
        'success': True,
        'is_favorite': is_favorite,
        'product_id': product_id
    })


@app.route('/insurance/share-with-doctor/<request_id>', methods=['POST'])
@login_required
@role_required('patient')
def share_with_doctor(request_id):
    """
    Share insurance quotes with assigned doctor for review (PATIENT ONLY)
    Use Case Step: Nested Path 8 - Share with doctor
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        flash('Quote request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify user owns this request
    if quote_request.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    # In production, get actual assigned doctor
    # For now, just mark as shared
    quote_request.shared_with_doctor = True
    quote_request.doctor_review_requested = True
    quote_request.status = 'pending_doctor_review'
    
    flash('Your insurance quotes have been shared with your doctor for review.', 'success')
    return redirect(url_for('view_insurance_quotes', request_id=request_id))


@app.route('/insurance/doctor-review/<request_id>', methods=['GET', 'POST'])
@login_required
@role_required('doctor', 'admin')
def doctor_review_quotes(request_id):
    """
    Doctor reviews and validates insurance quotes
    Use Case: Extension Path 1 - Doctor Involvement for Validation
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        flash('Quote request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Doctor adds review notes and approves
        doctor_notes = request.form.get('doctor_notes', '')
        override_ranking = request.form.get('override_ranking') == 'true'
        
        quote_request.doctor_notes = doctor_notes
        quote_request.doctor_id = current_user.id
        quote_request.reviewed_at = datetime.now()
        quote_request.status = 'completed'
        
        if override_ranking:
            # In a real system, doctor could reorder quotes
            # For now, just mark that override was requested
            quote_request.doctor_notes += "\n[Doctor override requested]"
        
        flash('Review completed successfully.', 'success')
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('insurance_doctor_review.html',
                          quote_request=quote_request)


@app.route('/insurance/export-pdf/<request_id>')
@login_required
def export_insurance_pdf(request_id):
    """
    Export insurance quotes as PDF
    Use Case Step: Nested Path 7 & 8 - Download PDF
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        flash('Quote request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify user owns this request
    if quote_request.user_id != current_user.id and current_user.role != 'admin':
        flash('You do not have permission to download this request.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Generate HTML for PDF (in production, convert to actual PDF)
    pdf_html = generate_pdf_summary(quote_request, quote_request.quotes)
    
    # Return HTML (in production, use library like WeasyPrint to convert to PDF)
    from flask import make_response
    response = make_response(pdf_html)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = f'attachment; filename=insurance_quotes_{request_id}.html'
    
    return response


@app.route('/insurance/pending-reviews')
@login_required
@role_required('doctor', 'admin')
def pending_doctor_reviews():
    """
    List all insurance quote requests pending doctor review
    Use Case: Extension Path 1 - Doctor Review Queue
    """
    from insurance_models import quote_requests_storage
    
    # Get all requests pending review
    pending_requests = [
        req for req in quote_requests_storage.values()
        if req.status == 'pending_doctor_review' and req.doctor_review_requested
    ]
    
    return render_template('insurance_pending_reviews.html',
                          pending_requests=pending_requests)


# ================================
# Error Handlers
# ================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


# ================================
# Context Processors
# ================================

@app.context_processor
def inject_user():
    """Make current_user available in all templates"""
    return {'current_user': current_user}


# ================================
# Run Application
# ================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏥 Clinical AI Assistance System - Web Application")
    print("="*60)
    print("\n📋 Example Users:")
    print("-" * 60)
    for username, user in example_users.items():
        print(f"  Role: {user.role.upper():10} | Username: {username:15} | Password: password123")
    print("-" * 60)
    print("\n🌐 Server starting at: http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

