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
from db_auth import (
    fetch_user as db_fetch_user,
    fetch_user_by_id as db_fetch_user_by_id,
    verify_password as db_verify_password,
    split_name_for_display as db_split_name,
)
from forms import LoginForm, InsuranceQuoteForm, ClinicalRecordAnalysisForm
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
from clinical_analysis_processor import (
    process_clinical_document, save_analysis_result, get_analysis_result,
    get_user_analysis_history, PIPELINE_AVAILABLE
)
from patient_history_analyzer import PatientHistoryAnalyzer, assess_data_quality
from approval_models import (
    create_review_package, save_approval_decision, get_approval_decision,
    get_pending_reviews, validate_approval, generate_digital_signature,
    escalate_for_review, ApprovalDecision, ApprovalStatus, SafetyLevel
)
from financial_assistance import (
    FinancialProfile, create_assistance_recommendation, get_assistance_recommendation
)
from werkzeug.utils import secure_filename
from rds_repository import (
    get_patient_dashboard,
    get_doctor_dashboard,
    get_admin_overview,
    list_users_admin,
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
from database_config import init_database
db = init_database(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Info: DB-backed login toggle
if os.environ.get('USE_RDS_LOGIN', 'true').lower() in {'1','true','yes'}:
    print("✓ RDS login enabled (demo password accepted unless hashes stored)")
else:
    print("✓ RDS login disabled; using demo users only")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    for user in example_users.values():
        if user.id == user_id:
            return user
    # Try database-backed user
    try:
        row = db_fetch_user_by_id(user_id)
        if row:
            first_name, last_name = db_split_name(row.get('display_name'), row['username'])
            return User(
                id=row['id'],
                username=row['username'],
                email=row.get('email') or f"{row['username']}@example.com",
                password_hash=generate_password_hash('placeholder'),
                role=row.get('role') or 'patient',
                first_name=first_name,
                last_name=last_name,
            )
    except Exception as e:
        print(f"[USER_LOADER] db fetch error: {e}")
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
        username = form.username.data
        password = form.password.data

        # If demo admin user, prioritize local demo auth
        demo_candidate = get_user_by_username(username)
        if demo_candidate and demo_candidate.role == 'admin':
            if demo_candidate.check_password(password) or password == 'password123':
                login_user(demo_candidate, remember=form.remember_me.data)
                print(f"✓ Demo admin logged in: {demo_candidate.username}")
                flash(f'Welcome back, {demo_candidate.get_display_name()}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid admin credentials.', 'danger')
                return render_template('login.html', form=form)

        # Non-admins: try RDS first, then demo fallback
        use_db_login = os.environ.get('USE_RDS_LOGIN', 'true').lower() in {'1','true','yes'}
        if use_db_login:
            try:
                row = db_fetch_user(username)
                if row and db_verify_password(row.get('password_hash') or '', password):
                    first_name, last_name = db_split_name(row.get('display_name'), row['username'])
                    mapped = User(
                        id=row['id'],
                        username=row['username'],
                        email=row.get('email') or f"{row['username']}@example.com",
                        password_hash=generate_password_hash(password),
                        role=row.get('role') or 'patient',
                        first_name=first_name,
                        last_name=last_name,
                    )
                    login_user(mapped, remember=form.remember_me.data)
                    print(f"✓ DB user logged in: {mapped.username} ({mapped.role})")
                    flash(f'Welcome back, {mapped.get_display_name()}!', 'success')
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('dashboard'))
            except Exception as e:
                print(f"[DB-LOGIN] error: {e}")

        # Fallback to demo accounts for non-admins
        if demo_candidate and demo_candidate.check_password(password):
            login_user(demo_candidate, remember=form.remember_me.data)
            print(f"✓ Demo user logged in: {demo_candidate.username} ({demo_candidate.role})")
            flash(f'Welcome back, {demo_candidate.get_display_name()}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))

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
    ctx = {}
    try:
        if os.environ.get('USE_RDS_LOGIN', 'true').lower() in {'1','true','yes'} and current_user and current_user.id:
            ctx = get_doctor_dashboard(int(str(current_user.id)))
    except Exception as e:
        print(f"[RDS doctor dashboard] {e}")
    return render_template('dashboard_doctor.html', user=current_user, rds=ctx)


@app.route('/dashboard/patient')
@login_required
@role_required('patient')
def patient_dashboard():
    """Patient dashboard - view medical records and AI analysis"""
    ctx = {}
    try:
        if os.environ.get('USE_RDS_LOGIN', 'true').lower() in {'1','true','yes'} and current_user and current_user.id:
            ctx = get_patient_dashboard(int(str(current_user.id)))
    except Exception as e:
        print(f"[RDS patient dashboard] {e}")
    return render_template('dashboard_patient.html', user=current_user, rds=ctx)


@app.route('/dashboard/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    """Admin dashboard - system management"""
    overview = {}
    adapted_users = []
    try:
        if os.environ.get('USE_RDS_LOGIN', 'true').lower() in {'1','true','yes'}:
            overview = get_admin_overview()
            rds_users = list_users_admin()
            for r in rds_users:
                # Map to User object for template compatibility
                first_name, last_name = db_split_name(r.get('name'), r.get('username'))
                role_lower = (r.get('role') or 'user').lower()
                adapted_users.append(
                    User(
                        id=str(r.get('id')),  # type: ignore[arg-type]
                        username=r.get('username'),
                        email=r.get('email'),
                        password_hash=generate_password_hash('placeholder'),
                        role=role_lower,
                        first_name=first_name,
                        last_name=last_name,
                    )
                )
    except Exception as e:
        print(f"[RDS admin overview/users] {e}")

    # Fallback to demo users if RDS not available
    if not adapted_users:
        adapted_users = list(example_users.values())

    return render_template('dashboard_admin.html', user=current_user, all_users=adapted_users, overview=overview)


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
    # Prefer RDS users if available, fallback to demo
    rds_users = []
    try:
        if os.environ.get('USE_RDS_LOGIN', 'true').lower() in {'1','true','yes'}:
            rds_users = list_users_admin()
    except Exception as e:
        print(f"[RDS users_list] {e}")
    if rds_users:
        # Adapt to template expected User-like object
        adapted = []
        for r in rds_users:
            first_name, last_name = db_split_name(r.get('name'), r.get('username'))
            role_lower = (r.get('role') or 'user').lower()
            adapted.append(
                User(
                    id=str(r.get('id')),
                    username=r.get('username'),
                    email=r.get('email'),
                    password_hash=generate_password_hash('placeholder'),
                    role=role_lower,
                    first_name=first_name,
                    last_name=last_name,
                )
            )
        return render_template('users_list.html', users=adapted, rds=True)
    else:
        users = list(example_users.values())
        return render_template('users_list.html', users=users, rds=False)


# ================================
# Profile
# ================================

@app.route('/profile')
@login_required
def profile():
    ctx = {}
    try:
        role = current_user.role
        uid = int(str(current_user.id)) if current_user and current_user.id else None
        if uid is not None:
            ctx = get_doctor_dashboard(uid) if role == 'doctor' else get_patient_dashboard(uid)
    except Exception as e:
        print(f"[RDS profile] {e}")
    return render_template('profile.html', user=current_user, rds=ctx)


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
                print(f"✓ Uploaded file: {file_path}")

                print(f"✓ Processing uploaded document: {filename}")
                doc_result = process_uploaded_document(file_path)
                print(f"✓ Doc result: {doc_result}")
                if doc_result['success']:
                    # Store extracted data in session for user review
                    session['document_data'] = doc_result
                    # IMPORTANT: update local variable so merge logic in this same request sees fresh data
                    document_data = doc_result
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
            
            # Merge AI-extracted data from uploaded document into health_data
            if document_data and document_data.get('success'):
                obs = document_data.get('observations', {}) or {}
                if not health_data.blood_pressure and obs.get('blood_pressure'):
                    health_data.blood_pressure = obs['blood_pressure']
                if not health_data.bmi and obs.get('bmi'):
                    health_data.bmi = obs['bmi']
                if not health_data.glucose and obs.get('glucose'):
                    health_data.glucose = obs['glucose']
                if not health_data.cholesterol and obs.get('cholesterol'):
                    health_data.cholesterol = obs['cholesterol']
                if not health_data.conditions and document_data.get('conditions'):
                    health_data.conditions = document_data['conditions']
                if not health_data.medications and document_data.get('medications'):
                    health_data.medications = document_data['medications']
            
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
            
            # Merge AI-extracted procedures as surgeries if user left field empty
            if document_data and document_data.get('success'):
                if not medical_history.surgeries and document_data.get('procedures'):
                    medical_history.surgeries = document_data['procedures']
                # Best-effort parse of Medical History section from raw_text into past_conditions
                if not medical_history.past_conditions:
                    raw_text = document_data.get('raw_text') or ''
                    try:
                        import re
                        m = re.search(r"Medical History:\n(.*?)(?:\n[A-Z][A-Za-z ]+:|\Z)", raw_text, re.S)
                        extracted = []
                        if m:
                            block = m.group(1)
                            for line in block.splitlines():
                                s = line.replace('(cid:127)', '').strip('-• \t')
                                if not s:
                                    continue
                                if '(diagnosed' in s:
                                    s = s.split('(diagnosed')[0].strip()
                                extracted.append(s)
                        if not extracted and document_data.get('conditions'):
                            extracted = document_data['conditions']
                        if extracted:
                            medical_history.past_conditions = extracted
                    except Exception:
                        if document_data.get('conditions'):
                            medical_history.past_conditions = document_data['conditions']
            
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
# Clinical Record Analysis Feature (Saahir Khan)
# AI-Assisted Clinical Document Processing
# ================================

@app.route('/clinical-analysis', methods=['GET', 'POST'])
@login_required
@role_required('doctor', 'patient')
def clinical_analysis():
    """
    AI-Assisted Clinical Record Analysis (Saahir Khan feature)
    Upload medical documents for complete AI pipeline analysis:
    OCR → Sectionizer → NER → Entity Linking → FHIR → Explanation → Safety Check
    """
    form = ClinicalRecordAnalysisForm()
    
    if form.validate_on_submit():
        try:
            # Get uploaded file
            uploaded_file = form.medical_document.data
            if not uploaded_file or not uploaded_file.filename:
                flash('Please select a medical document to analyze.', 'danger')
                return render_template('clinical_analysis_upload.html', form=form, pipeline_available=PIPELINE_AVAILABLE)
            
            # Save uploaded file temporarily
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            
            print(f"\n✓ Processing clinical document: {filename}")
            print(f"   Type: {form.document_type.data}")
            print(f"   User: {current_user.username} ({current_user.role})")
            
            # Process document through complete AI pipeline
            result = process_clinical_document(
                file_path=file_path,
                document_type=form.document_type.data,
                patient_name=form.patient_name.data or None,
                notes=form.notes.data or None
            )
            
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except:
                pass
            
            if result.success:
                # Save result (with patient ID for database storage)
                analysis_id = save_analysis_result(result, patient_id=current_user.id)
                
                flash(f'✓ Analysis complete! Identified {len(result.conditions)} conditions, {len(result.medications)} medications.', 'success')
                
                # Show warning if red flags detected
                if result.red_flags:
                    flash(f'⚠ WARNING: {len(result.red_flags)} red flag(s) detected. Please review carefully.', 'warning')
                
                return redirect(url_for('clinical_analysis_results', analysis_id=analysis_id))
            else:
                flash(f'⚠ Analysis failed: {result.error_message}', 'danger')
                return render_template('clinical_analysis_upload.html', form=form, pipeline_available=PIPELINE_AVAILABLE)
        
        except Exception as e:
            import traceback
            print(f"✗ Error processing clinical document: {e}")
            print(traceback.format_exc())
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('clinical_analysis_upload.html', form=form, pipeline_available=PIPELINE_AVAILABLE)
    
    return render_template('clinical_analysis_upload.html', form=form, pipeline_available=PIPELINE_AVAILABLE)


@app.route('/clinical-analysis/results/<analysis_id>')
@login_required
@role_required('doctor', 'patient')
def clinical_analysis_results(analysis_id):
    """
    Display complete analysis results with all extracted data
    """
    result = get_analysis_result(analysis_id)
    
    if not result:
        flash('Analysis not found.', 'danger')
        return redirect(url_for('clinical_analysis'))
    
    # In production, verify user has permission to view this analysis
    
    return render_template('clinical_analysis_results.html', result=result)


@app.route('/clinical-analysis/history')
@login_required
@role_required('doctor', 'patient')
def clinical_analysis_history():
    """
    View history of clinical document analyses
    """
    # In production, filter by current user
    history = get_user_analysis_history(current_user.id)
    
    return render_template('clinical_analysis_history.html', analyses=history)


@app.route('/clinical-analysis/download/<analysis_id>/fhir')
@login_required
@role_required('doctor', 'patient', 'admin')
def download_fhir_bundle(analysis_id):
    """
    Download FHIR R4 bundle as JSON
    """
    result = get_analysis_result(analysis_id)
    
    if not result or not result.fhir_bundle:
        flash('FHIR bundle not found.', 'danger')
        return redirect(url_for('clinical_analysis'))
    
    # Return as JSON download
    from flask import make_response
    response = make_response(json.dumps(result.fhir_bundle, indent=2))
    response.headers['Content-Type'] = 'application/fhir+json'
    response.headers['Content-Disposition'] = f'attachment; filename=fhir_bundle_{analysis_id}.json'
    
    return response


@app.route('/clinical-analysis/download/<analysis_id>/report')
@login_required
@role_required('doctor', 'patient')
def download_clinical_report(analysis_id):
    """
    Download complete analysis report as JSON
    """
    result = get_analysis_result(analysis_id)
    
    if not result:
        flash('Analysis not found.', 'danger')
        return redirect(url_for('clinical_analysis'))
    
    # Return as JSON download
    from flask import make_response
    response = make_response(json.dumps(result.to_dict(), indent=2, default=str))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=clinical_analysis_{analysis_id}.json'
    
    return response


# ================================
# Patient History Feature (UC-07 - Sarvadnya Kamble)
# Longitudinal Patient History with Timeline & Trends
# ================================

@app.route('/patient-history/<patient_id>')
@login_required
@role_required('doctor', 'admin')
def patient_history_dashboard(patient_id):
    """
    Main patient history dashboard
    Shows comprehensive longitudinal view with timeline, trends, and data quality
    """
    try:
        # Create analyzer instance
        analyzer = PatientHistoryAnalyzer(patient_id)
        
        # Aggregate all patient data
        history_data = analyzer.aggregate_patient_data()
        
        if not history_data['success']:
            flash(history_data.get('message', 'No medical history found for this patient.'), 'warning')
            return render_template('patient_history_empty.html', patient_id=patient_id)
        
        # Assess data quality
        quality = assess_data_quality(history_data['aggregated_data'])
        
        # Get patient info from example users (in production, from database)
        patient_user = None
        for username, user in example_users.items():
            if user.id == patient_id:
                patient_user = user
                break
        
        return render_template('patient_history_dashboard.html',
                             patient_id=patient_id,
                             patient=patient_user,
                             history=history_data,
                             quality=quality)
    
    except Exception as e:
        print(f"✗ Error loading patient history: {e}")
        flash(f'Error loading patient history: {str(e)}', 'danger')
        return redirect(url_for('doctor_dashboard'))


@app.route('/patient-history/<patient_id>/timeline')
@login_required
@role_required('doctor', 'admin')
def patient_history_timeline(patient_id):
    """
    Interactive timeline view of patient medical events
    """
    try:
        analyzer = PatientHistoryAnalyzer(patient_id)
        history_data = analyzer.aggregate_patient_data()
        
        if not history_data['success']:
            flash('No medical history found.', 'warning')
            return redirect(url_for('patient_history_dashboard', patient_id=patient_id))
        
        return render_template('patient_history_timeline.html',
                             patient_id=patient_id,
                             timeline=history_data['timeline'],
                             date_range=history_data['date_range'])
    
    except Exception as e:
        print(f"✗ Error loading timeline: {e}")
        flash(f'Error loading timeline: {str(e)}', 'danger')
        return redirect(url_for('patient_history_dashboard', patient_id=patient_id))


@app.route('/patient-history/<patient_id>/export')
@login_required
@role_required('doctor', 'admin')
def export_patient_history(patient_id):
    """
    Export patient history as JSON
    """
    try:
        analyzer = PatientHistoryAnalyzer(patient_id)
        history_data = analyzer.aggregate_patient_data()
        
        if not history_data['success']:
            flash('No medical history found.', 'warning')
            return redirect(url_for('patient_history_dashboard', patient_id=patient_id))
        
        # Return as JSON download
        from flask import make_response
        response = make_response(json.dumps(history_data, indent=2, default=str))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename=patient_history_{patient_id}.json'
        
        # Log export action
        from database_config import log_action
        try:
            log_action(current_user.id, 'export_history', 'patient', patient_id)
        except:
            pass  # Logging is optional
        
        return response
    
    except Exception as e:
        print(f"✗ Error exporting history: {e}")
        flash(f'Error exporting history: {str(e)}', 'danger')
        return redirect(url_for('patient_history_dashboard', patient_id=patient_id))


# ================================
# AI Output Review & Approval (UC-05 - Thanh Le)
# Doctor approval workflow with safety validation
# ================================

@app.route('/review/pending')
@login_required
@role_required('doctor', 'admin')
def pending_ai_reviews():
    """
    Queue of AI outputs pending doctor review
    UC-05: Main entry point for review workflow
    """
    pending_ids = get_pending_reviews()
    
    # Load analysis results for pending reviews
    pending_analyses = []
    for analysis_id in pending_ids:
        result = get_analysis_result(analysis_id)
        if result:
            # Create review package
            review_package = create_review_package(result)
            pending_analyses.append(review_package)
    
    return render_template('pending_ai_reviews.html',
                         pending_analyses=pending_analyses,
                         count=len(pending_analyses))


@app.route('/review/<analysis_id>', methods=['GET', 'POST'])
@login_required
@role_required('doctor', 'admin')
def review_ai_output(analysis_id):
    """
    Doctor reviews AI-generated medical content
    UC-05: Main review interface
    """
    # Get analysis result
    result = get_analysis_result(analysis_id)
    if not result:
        flash('Analysis not found.', 'danger')
        return redirect(url_for('pending_ai_reviews'))
    
    # Create review package
    review_package = create_review_package(result)
    
    if request.method == 'POST':
        from uuid import uuid4
        
        # Create approval decision
        decision = ApprovalDecision(
            decision_id=str(uuid4()),
            analysis_id=analysis_id,
            reviewer_id=current_user.id,
            reviewer_name=current_user.get_display_name()
        )
        
        # Parse form data
        decision.status = ApprovalStatus(request.form.get('status', 'pending'))
        decision.notes = request.form.get('notes', '')
        decision.reviewed_fhir = request.form.get('reviewed_fhir') == 'on'
        decision.reviewed_summary = request.form.get('reviewed_summary') == 'on'
        decision.reviewed_safety = request.form.get('reviewed_safety') == 'on'
        
        # Handle safety overrides
        override_flags = request.form.getlist('override_flags')
        for flag_id in override_flags:
            justification = request.form.get(f'justification_{flag_id}', '')
            if justification:
                decision.safety_overrides.append(flag_id)
                # In production, save justification to SafetyFlag object
        
        # Handle modifications
        if request.form.get('has_modifications') == 'on':
            modification_text = request.form.get('modification_text', '')
            if modification_text:
                decision.modifications.append({
                    'timestamp': datetime.now().isoformat(),
                    'text': modification_text
                })
        
        # Validate approval
        is_valid, error_msg = validate_approval(review_package, decision)
        
        if not is_valid:
            flash(f'Approval validation failed: {error_msg}', 'danger')
            return render_template('review_ai_output.html',
                                 review=review_package,
                                 analysis=result)
        
        # Generate digital signature for approval/rejection
        if decision.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
            decision.digital_signature = generate_digital_signature(current_user.id, decision)
            decision.signature_timestamp = datetime.now()
        
        # Check if escalation is needed
        if review_package.overall_confidence < 0.7 and decision.status == ApprovalStatus.APPROVED:
            if not decision.specialist_reviews:
                # Auto-escalate low confidence cases
                decision.status = ApprovalStatus.ESCALATED
                decision.requires_specialist = True
                flash('Case automatically escalated for specialist review due to low AI confidence.', 'warning')
        
        # Save decision
        save_approval_decision(decision)
        
        # Flash message
        if decision.status == ApprovalStatus.APPROVED:
            flash('✓ AI output approved. Patient can now view this analysis.', 'success')
            # In production, trigger notification to patient
        elif decision.status == ApprovalStatus.REJECTED:
            flash('AI output rejected. Analysis will not be released to patient.', 'info')
        elif decision.status == ApprovalStatus.ESCALATED:
            flash('Case escalated for specialist review.', 'warning')
        else:
            flash(f'Review saved with status: {decision.status.value}', 'info')
        
        return redirect(url_for('pending_ai_reviews'))
    
    return render_template('review_ai_output.html',
                         review=review_package,
                         analysis=result)


@app.route('/review/history')
@login_required
@role_required('doctor', 'admin')
def review_history():
    """
    View history of approval decisions
    """
    from approval_models import approval_decisions_storage
    
    # Get all decisions (in production, filter by user or date range)
    decisions = list(approval_decisions_storage.values())
    decisions.sort(key=lambda d: d.timestamp, reverse=True)
    
    return render_template('review_history.html', decisions=decisions)


@app.route('/review/decision/<decision_id>')
@login_required
@role_required('doctor', 'admin')
def view_approval_decision(decision_id):
    """
    View details of a specific approval decision
    """
    decision = get_approval_decision(decision_id)
    
    if not decision:
        flash('Approval decision not found.', 'danger')
        return redirect(url_for('review_history'))
    
    # Get associated analysis
    analysis = get_analysis_result(decision.analysis_id)
    
    return render_template('approval_decision_detail.html',
                         decision=decision,
                         analysis=analysis)


@app.route('/review/escalate/<analysis_id>', methods=['POST'])
@login_required
@role_required('doctor', 'admin')
def escalate_review(analysis_id):
    """
    Escalate case for multi-physician review
    UC-05: Extension Path 3 - Multi-Physician Review
    """
    result = get_analysis_result(analysis_id)
    if not result:
        return jsonify({'success': False, 'message': 'Analysis not found'}), 404
    
    reason = request.form.get('reason', 'Complex case requiring specialist input')
    
    review_package = create_review_package(result)
    decision = escalate_for_review(review_package, current_user.id, reason)
    
    flash(f'Case escalated for specialist review. Decision ID: {decision.decision_id}', 'info')
    return redirect(url_for('pending_ai_reviews'))


# ================================
# Financial Assistance & Loan Matching (UC-04 - Venkatesh Badri Narayanan)
# Subsidy eligibility and financial assistance recommendations
# ================================

@app.route('/financial-assistance/<request_id>')
@login_required
@role_required('patient')
def financial_assistance_from_quote(request_id):
    """
    Start financial assistance flow from insurance quote
    UC-04: Entry point from quote results page
    """
    # Get the insurance quote request
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        flash('Insurance quote not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify user owns this request
    if quote_request.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    if not quote_request.quotes:
        flash('No quotes available for financial assistance calculation.', 'warning')
        return redirect(url_for('request_insurance_quote'))
    
    # Extract financial profile from quote request
    income_details = quote_request.income_details
    
    # Redirect to assistance form with pre-filled data
    return redirect(url_for('request_financial_assistance', 
                           from_quote=request_id,
                           income=income_details.annual_income,
                           dependents=income_details.dependents))


@app.route('/financial-assistance/request', methods=['GET', 'POST'])
@login_required
@role_required('patient')
def request_financial_assistance():
    """
    Financial assistance request form
    UC-04: Collects/confirms financial data and calculates subsidies
    """
    # Check if coming from insurance quote
    from_quote_id = request.args.get('from_quote')
    pre_income = request.args.get('income', type=float)
    pre_dependents = request.args.get('dependents', type=int, default=0)
    
    if request.method == 'POST':
        try:
            # Create financial profile from form
            financial_profile = FinancialProfile(
                annual_income=float(request.form.get('annual_income', 0)),
                household_size=int(request.form.get('household_size', 1)),
                state=request.form.get('state', 'NSW'),
                employment_status=request.form.get('employment_status', 'employed'),
                dependents=int(request.form.get('dependents', 0)),
                has_medicare_card=request.form.get('has_medicare_card') == 'on',
                has_health_care_card=request.form.get('has_health_care_card') == 'on',
                pensioner=request.form.get('pensioner') == 'on',
                student=request.form.get('student') == 'on',
                credit_score=int(request.form.get('credit_score', 0)) or None
            )
            
            # Get selected plan cost
            selected_plan_cost = float(request.form.get('monthly_premium', 0))
            selected_plan_id = request.form.get('plan_id', '')
            
            if selected_plan_cost <= 0:
                flash('Please provide a valid monthly premium cost.', 'danger')
                return render_template('financial_assistance_form.html',
                                     from_quote_id=from_quote_id,
                                     pre_income=pre_income,
                                     pre_dependents=pre_dependents)
            
            # Create assistance recommendation
            recommendation = create_assistance_recommendation(
                financial_profile=financial_profile,
                user_id=current_user.id,
                original_monthly_cost=selected_plan_cost,
                selected_plan_id=selected_plan_id
            )
            
            print(f"✓ Financial assistance recommendation created: {recommendation.request_id}")
            print(f"   Total subsidies: ${recommendation.total_monthly_subsidy:.2f}/month")
            print(f"   Affordability: {recommendation.affordability_score.rating}")
            
            flash(f'✓ Subsidy eligibility calculated! Found {len(recommendation.subsidies)} applicable subsidies.', 'success')
            
            return redirect(url_for('view_assistance_recommendation', 
                                   recommendation_id=recommendation.request_id,
                                   from_quote=from_quote_id))
        
        except Exception as e:
            print(f"✗ Error processing financial assistance: {e}")
            import traceback
            traceback.print_exc()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('financial_assistance_form.html',
                         from_quote_id=from_quote_id,
                         pre_income=pre_income,
                         pre_dependents=pre_dependents)


@app.route('/financial-assistance/recommendation/<recommendation_id>')
@login_required
@role_required('patient')
def view_assistance_recommendation(recommendation_id):
    """
    Display financial assistance recommendation with subsidies and options
    UC-04: Main results page showing cost breakdown and assistance options
    """
    recommendation = get_assistance_recommendation(recommendation_id)
    
    if not recommendation:
        flash('Assistance recommendation not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify user owns this recommendation
    if recommendation.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if coming from quote
    from_quote_id = request.args.get('from_quote')
    quote_request = None
    if from_quote_id:
        quote_request = get_quote_request(from_quote_id)
    
    return render_template('financial_assistance_results.html',
                         recommendation=recommendation,
                         quote_request=quote_request,
                         from_quote_id=from_quote_id)


@app.route('/financial-assistance/export/<recommendation_id>')
@login_required
@role_required('patient')
def export_assistance_recommendation(recommendation_id):
    """
    Export assistance recommendation as JSON
    UC-04: Export for records
    """
    recommendation = get_assistance_recommendation(recommendation_id)
    
    if not recommendation:
        flash('Recommendation not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Verify user owns this recommendation
    if recommendation.user_id != current_user.id:
        flash('Permission denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Return as JSON download
    from flask import make_response
    response = make_response(json.dumps(recommendation.to_dict(), indent=2, default=str))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=financial_assistance_{recommendation_id}.json'
    
    return response


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
    print("\n🌐 Server starting at: http://127.0.0.1:5000 Thanh")
    print("Press CTRL+C to stop the server\n")
    
    
    app.run(debug=True, host='0.0.0.0', port=5000)

