"""
Flask Web Application for Clinical AI Assistance System
Main application file with authentication and role-based access
"""

from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
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
from forms import LoginForm, InsuranceQuoteForm, ClinicalRecordAnalysisForm, SignupForm, ChangePasswordForm
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
    get_quote_history_for_patient,
    get_patient_action_history,
    get_quote_request_full_for_token,
    create_user,
    get_pending_doctors,
    get_admin_dashboard_stats,
    update_doctor_approval,
    get_doctor_approval_status,
    get_patient_recent_medical_records,
    save_medical_record_to_rds,
    get_all_approved_doctors,
    get_doctor_complete_profile,
    save_review_request,
    get_pending_reviews_for_doctor,
    get_review_status_for_analysis,
    update_approval_decision_in_rds,
    update_user_password,
)
from doctor_recommender import recommend_doctors
try:
    from aws_persistence import save_quotes_to_rds
except Exception:
    save_quotes_to_rds = None

# In-memory progress tracker for simple background processing
PROGRESS: dict = {}

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
# Session & remember-me configuration (persist login across restarts like real sites)
app.config['SESSION_COOKIE_NAME'] = os.environ.get('SESSION_COOKIE_NAME', 'clinical_ai_session')
app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
app.config['REMEMBER_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'
app.config['REMEMBER_COOKIE_REFRESH_EACH_REQUEST'] = True

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
from database_config import init_database
db = init_database(app)


# Helper: adapt an RDS package (from get_quote_request_full_for_token) to in-memory-like objects
def _adapt_pkg_to_objects(pkg, user_id, request_id):
    from types import SimpleNamespace as _NS
    req_obj = _NS(
        request_id=request_id,
        user_id=user_id,
        created_at=pkg['request']['request_time'],
        status=str(pkg['request']['status']).lower(),
        use_ai_explainer=True,
        health_data=_NS(conditions=pkg['request'].get('conditions') or [], medications=[]),
        medical_history=_NS(past_conditions=pkg['request'].get('conditions') or [], surgeries=[], hospitalizations=[], family_history=[]),
        income_details=_NS(annual_income=pkg['request'].get('income') or 0, employment_status='Employed', occupation=''),
        quotes=[],
    )
    quotes = []
    for q in pkg['quotes']:
        prod = q['product']
        # Use quote_id as product_id for RDS quotes so we can match them uniquely
        quote_id = q.get('quote_id') or prod.get('quote_id')
        product_id_str = f"RDS-{quote_id}" if quote_id else 'RDS'
        product_obj = _NS(
            product_id=product_id_str,
            name=prod.get('name'),
            provider=prod.get('provider'),
            plan_type=prod.get('plan_type'),
            coverage_amount=prod.get('coverage_amount') or 0,
            monthly_premium=prod.get('monthly_premium') or 0,
            annual_deductible=prod.get('annual_deductible') or 0,
            copay=0,
            coinsurance=0,
            max_out_of_pocket=prod.get('max_out_of_pocket') or 0,
            coverage_details=list(prod.get('coverage_details') or []),
            exclusions=list(prod.get('exclusions') or []),
            product_link=prod.get('product_link') or None,
        )
        overall = q.get('overall_score')
        if overall is None:
            parts = [p for p in [q.get('suitability_score'), q.get('cost_score'), q.get('coverage_score')] if p is not None]
            overall = int(sum(parts) / len(parts)) if parts else 0
        quote_obj = _NS(
            product=product_obj,
            suitability_score=q.get('suitability_score') or 0,
            cost_score=q.get('cost_score') or 0,
            coverage_score=q.get('coverage_score') or 0,
            overall_score=overall,
            rationale=q.get('rationale') or '',
        )
        quotes.append(quote_obj)
    return req_obj, quotes

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.remember_cookie_duration = timedelta(days=30)

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
                session.permanent = True
                remember_flag = getattr(form, 'remember_me', None)
                remember_val = bool(remember_flag.data) if remember_flag is not None else True
                login_user(demo_candidate, remember=remember_val)
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
                if row:
                    stored_hash = row.get('password_hash') or ''
                    print(f"[DB-LOGIN] User found: {username}, hash exists: {bool(stored_hash)}, hash prefix: {stored_hash[:20] if stored_hash else 'N/A'}")
                    if db_verify_password(stored_hash, password):
                        # Check doctor approval status
                        role = row.get('role') or 'patient'
                        if role == 'doctor':
                            approval_status = get_doctor_approval_status(int(row['id']))
                            print(f"[DB-LOGIN] Doctor approval status: {approval_status}")
                            if approval_status == 'Pending':
                                flash('Your doctor account is pending admin approval. You will be able to log in once an administrator approves your account.', 'warning')
                                return render_template('login.html', form=form)
                            elif approval_status == 'Rejected':
                                flash('Your doctor account has been rejected. Please contact support for more information.', 'danger')
                                return render_template('login.html', form=form)
                            elif approval_status != 'Approved':
                                flash('Your doctor account is pending approval. Please wait for admin approval.', 'warning')
                                return render_template('login.html', form=form)
                        
                        first_name, last_name = db_split_name(row.get('display_name'), row['username'])
                        mapped = User(
                            id=row['id'],
                            username=row['username'],
                            email=row.get('email') or f"{row['username']}@example.com",
                            password_hash=stored_hash,  # Use stored hash, don't regenerate
                            role=role,
                            first_name=first_name,
                            last_name=last_name,
                        )
                        session.permanent = True
                        remember_flag = getattr(form, 'remember_me', None)
                        remember_val = bool(remember_flag.data) if remember_flag is not None else True
                        login_user(mapped, remember=remember_val)
                        print(f"✓ DB user logged in: {mapped.username} ({mapped.role})")
                        flash(f'Welcome back, {mapped.get_display_name()}!', 'success')
                        next_page = request.args.get('next')
                        return redirect(next_page or url_for('dashboard'))
                    else:
                        print(f"[DB-LOGIN] Password verification failed for {username}")
                else:
                    print(f"[DB-LOGIN] User not found: {username}")
            except Exception as e:
                import traceback
                print(f"[DB-LOGIN] error: {e}")
                print(traceback.format_exc())

        # Fallback to demo accounts for non-admins
        if demo_candidate and demo_candidate.check_password(password):
            session.permanent = True
            remember_flag = getattr(form, 'remember_me', None)
            remember_val = bool(remember_flag.data) if remember_flag is not None else True
            login_user(demo_candidate, remember=remember_val)
            print(f"✓ Demo user logged in: {demo_candidate.username} ({demo_candidate.role})")
            flash(f'Welcome back, {demo_candidate.get_display_name()}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))

        flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Allow users to change their password"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Get current password
        current_password = form.current_password.data
        new_password = form.new_password.data
        
        # Verify current password
        user_id = current_user.id
        user_found = False
        password_correct = False
        
        # Try to verify password from database first
        try:
            db_user = db_fetch_user_by_id(str(user_id))
            if db_user:
                user_found = True
                # Verify current password
                password_correct = db_verify_password(db_user['password_hash'], current_password)
                print(f"[CHANGE-PASSWORD] User found in DB: {db_user['username']}, password_correct: {password_correct}")
        except Exception as e:
            print(f"[CHANGE-PASSWORD] Error fetching user from DB: {e}")
        
        # If not in DB, try in-memory storage
        if not user_found:
            try:
                from models import get_user_by_username
                in_mem_user = get_user_by_username(current_user.username)
                if in_mem_user:
                    user_found = True
                    password_correct = in_mem_user.check_password(current_password)
                    print(f"[CHANGE-PASSWORD] User found in-memory: {in_mem_user.username}, password_correct: {password_correct}")
            except Exception as e:
                print(f"[CHANGE-PASSWORD] Error fetching user from in-memory: {e}")
        
        if not password_correct:
            flash('Current password is incorrect. Please try again.', 'danger')
            return render_template('change_password.html', form=form)
        
        # Current password is correct, proceed with password change
        new_password_hash = generate_password_hash(new_password)
        
        # Update password in database
        db_updated = False
        try:
            # Convert user_id to int for database operation
            user_id_int = int(user_id) if isinstance(user_id, (int, str)) and str(user_id).isdigit() else None
            
            if user_id_int:
                db_updated = update_user_password(user_id_int, new_password_hash)
                if db_updated:
                    print(f"[CHANGE-PASSWORD] Password updated in database for user {user_id_int}")
        except Exception as e:
            print(f"[CHANGE-PASSWORD] Error updating password in DB: {e}")
        
        # Update password in in-memory storage
        in_mem_updated = False
        try:
            from models import get_user_by_username, example_users
            in_mem_user = get_user_by_username(current_user.username)
            if in_mem_user:
                in_mem_user.password_hash = new_password_hash
                # Also update in example_users dict if it exists
                if current_user.username in example_users:
                    example_users[current_user.username].password_hash = new_password_hash
                in_mem_updated = True
                print(f"[CHANGE-PASSWORD] Password updated in-memory for user {current_user.username}")
        except Exception as e:
            print(f"[CHANGE-PASSWORD] Error updating password in-memory: {e}")
        
        if db_updated or in_mem_updated:
            flash('Password changed successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Error updating password. Please try again or contact support.', 'danger')
            return render_template('change_password.html', form=form)
    
    return render_template('change_password.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    username = current_user.username
    logout_user()
    try:
        # Clear any transient state
        session.pop('document_data', None)
    except Exception:
        pass
    flash(f'You have been logged out successfully.', 'info')
    print(f"✓ User logged out: {username}")
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration/signup page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data
        name = form.name.data.strip()
        role = form.role.data
        
        # Validate doctor-specific fields
        if role == 'doctor':
            if not form.ahpra_number.data or not form.ahpra_number.data.strip():
                flash('AHPRA Provider/Registration Number is required for doctor accounts.', 'danger')
                return render_template('signup.html', form=form)
            if not form.specialization.data or not form.specialization.data.strip():
                flash('Specialization is required for doctor accounts.', 'danger')
                return render_template('signup.html', form=form)
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Create user in database
        try:
            result = create_user(
                username=username,
                email=email,
                password_hash=password_hash,
                name=name,
                role=role,
                specialization=form.specialization.data.strip() if role == 'doctor' and form.specialization.data else None,
                ahpra_number=form.ahpra_number.data.strip() if role == 'doctor' and form.ahpra_number.data else None,
                qualification=form.qualification.data.strip() if role == 'doctor' and form.qualification.data else None,
                clinic_address=form.clinic_address.data.strip() if role == 'doctor' and form.clinic_address.data else None,
            )
            
            if result['success']:
                if role == 'doctor':
                    flash('Account created successfully! Your doctor account is pending admin approval. You will receive an email once your account is approved.', 'info')
                else:
                    flash('Account created successfully! You can now log in.', 'success')
                print(f"✓ New {role} account created: {username} (user_id: {result.get('user_id')})")
                return redirect(url_for('login'))
            else:
                flash(result.get('message', 'Error creating account. Please try again.'), 'danger')
        except Exception as e:
            print(f"[SIGNUP] Error: {e}")
            flash('An error occurred while creating your account. Please try again.', 'danger')
    
    return render_template('signup.html', form=form)


@app.route('/admin/doctor-approvals')
@login_required
@role_required('admin')
def admin_doctor_approvals():
    """Admin page to view and approve/reject pending doctor accounts"""
    try:
        pending_doctors = get_pending_doctors()
        return render_template('admin_doctor_approvals.html', pending_doctors=pending_doctors)
    except Exception as e:
        print(f"[ADMIN-APPROVALS] Error: {e}")
        flash('Error loading pending doctors. Please try again.', 'danger')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/approve-doctor/<int:doctor_user_id>', methods=['POST'])
@login_required
@role_required('admin')
def approve_doctor(doctor_user_id):
    """Approve a doctor account"""
    approval_notes = request.form.get('approval_notes', '').strip()
    approval_status = 'Approved'
    
    try:
        # Get admin's numeric user ID from database if they have one
        # If admin is using a demo account (string ID), approved_by will be NULL
        admin_user_id = None
        if current_user.id:
            try:
                # Try to convert to int if it's already numeric
                admin_user_id = int(current_user.id)
            except (ValueError, TypeError):
                # If it's a string ID (like 'adm_001'), try to find the user in DB
                try:
                    from db_auth import fetch_user as db_fetch_user
                    admin_db_user = db_fetch_user(current_user.username)
                    if admin_db_user and admin_db_user.get('id'):
                        admin_user_id = int(admin_db_user['id'])
                        print(f"[APPROVE-DOCTOR] Found admin in DB: username={current_user.username}, id={admin_user_id}")
                except Exception as e:
                    print(f"[APPROVE-DOCTOR] Could not find admin in DB: {e}")
                    # approved_by will be NULL, which is acceptable
        
        print(f"[APPROVE-DOCTOR] Attempting to approve doctor_user_id={doctor_user_id}, admin_id={admin_user_id}")
        success = update_doctor_approval(
            doctor_user_id=doctor_user_id,
            admin_user_id=admin_user_id,  # Can be None for demo admins
            approval_status=approval_status,
            approval_notes=approval_notes or 'Approved by administrator'
        )
        if success:
            print(f"[APPROVE-DOCTOR] Successfully approved doctor_user_id={doctor_user_id}")
            flash('Doctor account approved successfully.', 'success')
        else:
            print(f"[APPROVE-DOCTOR] Failed to approve doctor_user_id={doctor_user_id}")
            flash('Failed to approve doctor account. Please check server logs.', 'danger')
    except Exception as e:
        import traceback
        print(f"[APPROVE-DOCTOR] Exception: {e}")
        print(traceback.format_exc())
        flash(f'Error approving doctor account: {str(e)}', 'danger')
    
    return redirect(url_for('admin_doctor_approvals'))


@app.route('/admin/reject-doctor/<int:doctor_user_id>', methods=['POST'])
@login_required
@role_required('admin')
def reject_doctor(doctor_user_id):
    """Reject a doctor account"""
    approval_notes = request.form.get('rejection_notes', '').strip()
    if not approval_notes:
        flash('Please provide a reason for rejection.', 'warning')
        return redirect(url_for('admin_doctor_approvals'))
    
    approval_status = 'Rejected'
    
    try:
        # Get admin's numeric user ID from database if they have one
        # If admin is using a demo account (string ID), approved_by will be NULL
        admin_user_id = None
        if current_user.id:
            try:
                # Try to convert to int if it's already numeric
                admin_user_id = int(current_user.id)
            except (ValueError, TypeError):
                # If it's a string ID (like 'adm_001'), try to find the user in DB
                try:
                    from db_auth import fetch_user as db_fetch_user
                    admin_db_user = db_fetch_user(current_user.username)
                    if admin_db_user and admin_db_user.get('id'):
                        admin_user_id = int(admin_db_user['id'])
                        print(f"[REJECT-DOCTOR] Found admin in DB: username={current_user.username}, id={admin_user_id}")
                except Exception as e:
                    print(f"[REJECT-DOCTOR] Could not find admin in DB: {e}")
                    # approved_by will be NULL, which is acceptable
        
        success = update_doctor_approval(
            doctor_user_id=doctor_user_id,
            admin_user_id=admin_user_id,  # Can be None for demo admins
            approval_status=approval_status,
            approval_notes=approval_notes
        )
        if success:
            flash('Doctor account rejected.', 'info')
        else:
            flash('Failed to reject doctor account.', 'danger')
    except Exception as e:
        print(f"[REJECT-DOCTOR] Error: {e}")
        flash('Error rejecting doctor account.', 'danger')
    
    return redirect(url_for('admin_doctor_approvals'))


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
    action_history = []
    try:
        if os.environ.get('USE_RDS_LOGIN', 'true').lower() in {'1','true','yes'} and current_user and current_user.id:
            ctx = get_patient_dashboard(int(str(current_user.id)))
            # Get action history (insurance quotes + medical analyses)
            try:
                action_history = get_patient_action_history(int(str(current_user.id)), limit=20)
            except Exception as e:
                print(f"[RDS action history] {e}")
    except Exception as e:
        print(f"[RDS patient dashboard] {e}")
    return render_template('dashboard_patient.html', user=current_user, rds=ctx, action_history=action_history)


@app.route('/dashboard/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    """Admin dashboard - system management"""
    overview = {}
    adapted_users = []
    pending_doctors_count = 0
    dashboard_stats = {
        'total_users': len(example_users),
        'documents_processed': 0,
        'ai_pipeline_uptime': '100%',
        'storage_used': 'N/A'
    }
    
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
            # Get pending doctors count
            try:
                pending_doctors = get_pending_doctors()
                pending_doctors_count = len(pending_doctors)
            except Exception as e:
                print(f"[RDS pending doctors count] {e}")
                pending_doctors_count = 0
            
            # Get real dashboard stats
            try:
                dashboard_stats = get_admin_dashboard_stats()
            except Exception as e:
                print(f"[RDS admin dashboard stats] {e}")
    except Exception as e:
        print(f"[RDS admin overview/users] {e}")

    # Fallback to demo users if RDS not available
    if not adapted_users:
        adapted_users = list(example_users.values())
        dashboard_stats['total_users'] = len(adapted_users)

    return render_template('dashboard_admin.html', 
                          user=current_user, 
                          all_users=adapted_users, 
                          overview=overview,
                          pending_doctors_count=pending_doctors_count,
                          stats=dashboard_stats)


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
                
                # Get file info for saving to RDS
                import os as os_module
                from hashlib import sha256
                file_size = os_module.path.getsize(file_path)
                file_size_mb = round(file_size / (1024 * 1024), 3)
                # Estimate pages (rough: 1 page ≈ 50KB for text, but varies)
                # For now, we'll leave pages as None and let it be inferred
                file_hash = sha256(filename.encode() + str(current_user.id).encode() + str(datetime.now()).encode()).hexdigest()[:32]

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
                    
                    # Try to infer document type from filename or content
                    inferred_doc_type = 'other'  # Default
                    filename_lower = filename.lower()
                    if 'lab' in filename_lower or 'laboratory' in filename_lower:
                        inferred_doc_type = 'lab_results'
                    elif 'imaging' in filename_lower or 'radiology' in filename_lower or 'xray' in filename_lower or 'ct' in filename_lower or 'mri' in filename_lower:
                        inferred_doc_type = 'imaging_report'
                    elif 'pathology' in filename_lower:
                        inferred_doc_type = 'pathology'
                    elif 'prescription' in filename_lower or 'rx' in filename_lower:
                        inferred_doc_type = 'prescription'
                    elif 'discharge' in filename_lower:
                        inferred_doc_type = 'discharge_summary'
                    elif 'consultation' in filename_lower or 'consult' in filename_lower:
                        inferred_doc_type = 'consultation'
                    else:
                        # Default to medical_report for insurance quote documents
                        inferred_doc_type = 'medical_report'
                    
                    # Save medical record to RDS
                    try:
                        if os.environ.get('USE_RDS_LOGIN', 'true').lower() in {'1','true','yes'}:
                            patient_user_id = int(str(current_user.id))
                            record_id = save_medical_record_to_rds(
                                patient_user_id=patient_user_id,
                                file_hash=file_hash,
                                document_type=inferred_doc_type,
                                size_mb=file_size_mb,
                                status='Processed',
                                uploaded_at=datetime.now()
                            )
                            if record_id:
                                print(f"[RDS] Saved medical record from insurance quote: record_id={record_id}")
                    except Exception as e:
                        print(f"[RDS] Failed to save medical record from insurance quote: {e}")
                else:
                    flash(f"⚠ Document processing failed: {doc_result.get('error')}", 'warning')
                
                # Clean up uploaded file
                try:
                    os.remove(file_path)
                except:
                    pass
            
            # Create a new quote request
            quote_request = QuoteRequest(user_id=current_user.id)
            # Optional: user-selected AI analyzer for rationale
            try:
                use_ai = request.form.get('use_ai_analyzer') in {'on','true','1'}
                setattr(quote_request, 'use_ai_explainer', use_ai)
            except Exception:
                pass
            
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
            
            # If AI analyzer selected, show progress page and process asynchronously via fetch
            if getattr(quote_request, 'use_ai_explainer', False):
                return redirect(url_for('processing_quotes', request_id=request_id))
            else:
                # Process synchronously (legacy path)
                success, quotes, message = process_insurance_quote_request(quote_request)
                if success:
                    # Persist to AWS (best-effort)
                    try:
                        if save_quotes_to_rds:
                            save_quotes_to_rds(quote_request, quotes, {
                                'username': getattr(current_user, 'username', str(current_user.id)),
                                'name': getattr(current_user, 'first_name', '') or getattr(current_user, 'username', 'patient'),
                                'email': getattr(current_user, 'email', f"{getattr(current_user, 'username', 'patient')}@example.com"),
                            })
                    except Exception as e:
                        print(f"[RDS persist] sync save failed: {e}")
                    flash(f'Success! {message}', 'success')
                    try:
                        session.pop('document_data', None)
                    except Exception:
                        pass
                    return redirect(url_for('view_insurance_quotes', request_id=request_id))
                else:
                    flash(f'Unable to generate quotes: {message}', 'warning')
                    try:
                        session.pop('document_data', None)
                    except Exception:
                        pass
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
    
    # Clear the session banner so it doesn't persist across tabs/pages
    try:
        session.pop('document_data', None)
    except Exception:
        pass
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
        # Fallback: load from RDS by REQ token inside quote_requests.user_input
        try:
            pkg = get_quote_request_full_for_token(int(str(current_user.id)), request_id)
        except Exception as e:
            pkg = None
            print(f"[RDS view] failed: {e}")
        if not pkg:
            flash('Quote request not found.', 'danger')
            return redirect(url_for('dashboard'))
        req_obj, quotes = _adapt_pkg_to_objects(pkg, current_user.id, request_id)
        return render_template('insurance_quotes_display.html', quote_request=req_obj, quotes=quotes)
    
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


@app.route('/insurance/processing/<request_id>')
@login_required
def processing_quotes(request_id):
    """Show progress bar while AI analyzer generates quotes."""
    quote_request = get_quote_request(request_id)
    if not quote_request:
        flash('Quote request not found.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('processing_quotes.html', request_id=request_id)


@app.route('/insurance/process-now/<request_id>', methods=['POST'])
@login_required
def process_quotes_now(request_id):
    """Start background processing and return immediately."""
    import threading
    qr = get_quote_request(request_id)
    if not qr:
        return jsonify({'success': False, 'message': 'Request not found'}), 404
    # Initialize progress
    PROGRESS[request_id] = {'pct': 5, 'status': 'Starting', 'done': False, 'success': None, 'results_url': None}
    
    def cb(pct: int, msg: str):
        PROGRESS[request_id] = {**PROGRESS.get(request_id, {}), 'pct': int(pct), 'status': msg}
    
    # Capture lightweight user context for persistence in the worker thread
    user_ctx = {
        'username': getattr(current_user, 'username', str(current_user.id)),
        'name': getattr(current_user, 'first_name', '') or getattr(current_user, 'username', 'patient'),
        'email': getattr(current_user, 'email', f"{getattr(current_user, 'username', 'patient')}@example.com"),
    }

    def worker():
        success, quotes, message = process_insurance_quote_request(qr, progress_cb=cb)
        # Persist to AWS
        try:
            if success and save_quotes_to_rds:
                save_quotes_to_rds(qr, quotes, user_ctx)
        except Exception as e:
            print(f"[RDS persist] async save failed: {e}")
        # url_for requires an app context when used in a background thread
        try:
            with app.app_context():
                url = url_for('view_insurance_quotes', request_id=request_id) if success else url_for('insurance_no_results', request_id=request_id)
        except Exception:
            # Fallback to simple path if context fails
            url = f"/insurance/quotes/{request_id}" if success else f"/insurance/no-results/{request_id}"
        PROGRESS[request_id] = {'pct': 100 if success else PROGRESS.get(request_id, {}).get('pct', 95),
                                'status': 'Completed' if success else message,
                                'done': True, 'success': success, 'results_url': url}
        try:
            session.pop('document_data', None)
        except Exception:
            pass
    
    threading.Thread(target=worker, daemon=True).start()
    return jsonify({'success': True})


@app.route('/insurance/progress/<request_id>')
@login_required
def insurance_progress(request_id):
    data = PROGRESS.get(request_id) or {'pct': 0, 'status': 'Pending', 'done': False}
    return jsonify(data)


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


@app.route('/insurance/clear-doc-data')
@login_required
def clear_extracted_document_data():
    """Clear AI-extracted document data from session to stop persistent banner."""
    try:
        session.pop('document_data', None)
        flash('Cleared extracted document data.', 'info')
    except Exception:
        pass
    # Redirect back to where user came from, fallback to request-quote
    return redirect(request.referrer or url_for('request_insurance_quote'))


@app.route('/insurance/history')
@login_required
@role_required('patient')
def insurance_quote_history():
    """
    View user's insurance quote history (PATIENT ONLY)
    """
    # Prefer RDS-backed history if available
    rds_history = []
    try:
        rds_history = get_quote_history_for_patient(int(str(current_user.id)))
    except Exception as e:
        print(f"[RDS history] fallback to in-memory: {e}")
    if rds_history:
        return render_template('insurance_history.html', rds_history=rds_history, requests=None)
    # Fallback to in-memory requests
    user_requests = get_user_quote_requests(current_user.id)
    return render_template('insurance_history.html', requests=user_requests)


@app.route('/insurance/history/delete-rds/<int:rds_request_id>', methods=['POST'])
@login_required
@role_required('patient')
def delete_rds_quote_request(rds_request_id: int):
    """Delete a DB-backed quote request (and its recs/quotes) for current user."""
    try:
        from rds_repository import _conn
        with _conn() as conn:
            conn.autocommit = False
            cur = conn.cursor()
            # Ownership check
            cur.execute("SELECT patient_id FROM quote_requests WHERE id=%s", (rds_request_id,))
            row = cur.fetchone()
            if not row or int(row[0]) != int(str(current_user.id)):
                conn.rollback()
                flash('Permission denied for this request.', 'danger')
                return redirect(url_for('insurance_quote_history'))
            # Delete quotes tied to recommendations of this request (optional cleanup)
            cur.execute(
                "DELETE FROM quotes WHERE id IN (SELECT quote_id FROM quote_recommendations WHERE quote_request_id=%s)",
                (rds_request_id,),
            )
            # Delete the quote_request (cascades to recommendations)
            cur.execute("DELETE FROM quote_requests WHERE id=%s", (rds_request_id,))
            conn.commit()
        flash('Quote request deleted.', 'info')
    except Exception as e:
        print(f"[RDS delete] failed: {e}")
        flash('Unable to delete request.', 'warning')
    return redirect(url_for('insurance_quote_history'))


@app.route('/insurance/history/delete/<request_id>', methods=['POST'])
@login_required
@role_required('patient')
def delete_local_quote_request(request_id: str):
    """Delete an in-memory quote request by request_id."""
    try:
        from insurance_models import quote_requests_storage
        req = quote_requests_storage.get(request_id)
        if not req or getattr(req, 'user_id', None) != current_user.id:
            flash('Request not found or permission denied.', 'warning')
            return redirect(url_for('insurance_quote_history'))
        del quote_requests_storage[request_id]
        flash('Quote request deleted.', 'info')
    except Exception as e:
        print(f"[LOCAL delete] failed: {e}")
        flash('Unable to delete request.', 'warning')
    return redirect(url_for('insurance_quote_history'))


@app.route('/insurance/download/<request_id>')
@login_required
def download_insurance_quotes(request_id):
    """
    Download insurance quotes as JSON
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        # Fallback to RDS
        try:
            pkg = get_quote_request_full_for_token(int(str(current_user.id)), request_id)
        except Exception as e:
            pkg = None
            print(f"[RDS download] failed: {e}")
        if not pkg:
            flash('Quote request not found.', 'danger')
            return redirect(url_for('dashboard'))
        # Build JSON directly from pkg
        return jsonify(pkg)
    
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
        # Fallback: load from RDS by REQ token inside quote_requests.user_input
        try:
            pkg = get_quote_request_full_for_token(int(str(current_user.id)), request_id)
        except Exception as e:
            pkg = None
            print(f"[RDS cost-breakdown] failed: {e}")
        if not pkg:
            flash('Quote request not found.', 'danger')
            return redirect(url_for('dashboard'))
        req_obj, quotes = _adapt_pkg_to_objects(pkg, current_user.id, request_id)
        quote_request = req_obj
        quote_request.quotes = quotes
    
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
    
    # If still not found (e.g., old format or missing quote_id), try to match by first quote
    # This is a fallback for edge cases
    if not target_quote and quote_request.quotes:
        # Try matching RDS quotes that might not have quote_id in product_id
        if product_id.startswith('RDS'):
            # Extract quote_id if in format "RDS-{id}"
            if '-' in product_id:
                try:
                    quote_id_part = int(product_id.split('-')[1])
                    # Try to match by checking if any quote has this quote_id embedded
                    # Since we don't store quote_id directly on the quote object, use first as fallback
                    target_quote = quote_request.quotes[0]
                except (ValueError, IndexError):
                    target_quote = quote_request.quotes[0]
            else:
                target_quote = quote_request.quotes[0]
        else:
            target_quote = quote_request.quotes[0]
    
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
    FEATURE COMING SOON - Currently disabled
    """
    flash('Compare Quotes feature is coming soon! This feature will allow you to compare multiple insurance quotes side-by-side.', 'info')
    return redirect(url_for('view_insurance_quotes', request_id=request_id))


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
    Export insurance quotes as HTML
    Use Case Step: Nested Path 7 & 8 - Download HTML
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        # RDS fallback
        try:
            pkg = get_quote_request_full_for_token(int(str(current_user.id)), request_id)
        except Exception as e:
            pkg = None
            print(f"[RDS pdf] failed: {e}")
        if not pkg:
            flash('Quote request not found.', 'danger')
            return redirect(url_for('dashboard'))
        req_obj, quotes = _adapt_pkg_to_objects(pkg, current_user.id, request_id)
        from flask import make_response
        pdf_html = generate_pdf_summary(req_obj, quotes)
        response = make_response(pdf_html)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'attachment; filename=insurance_quotes_{request_id}.html'
        return response
    
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


@app.route('/insurance/export-real-pdf/<request_id>')
@login_required
def export_insurance_real_pdf(request_id):
    """
    Export insurance quotes as actual PDF file
    Uses WeasyPrint if available, otherwise falls back to HTML
    """
    quote_request = get_quote_request(request_id)
    
    if not quote_request:
        # RDS fallback
        try:
            pkg = get_quote_request_full_for_token(int(str(current_user.id)), request_id)
        except Exception as e:
            pkg = None
            print(f"[RDS real-pdf] failed: {e}")
        if not pkg:
            flash('Quote request not found.', 'danger')
            return redirect(url_for('dashboard'))
        req_obj, quotes = _adapt_pkg_to_objects(pkg, current_user.id, request_id)
        html_content = generate_pdf_summary(req_obj, quotes)
    else:
        # Verify user owns this request
        if quote_request.user_id != current_user.id and current_user.role != 'admin':
            flash('You do not have permission to download this request.', 'danger')
            return redirect(url_for('dashboard'))
        html_content = generate_pdf_summary(quote_request, quote_request.quotes)
    
    # Try to convert HTML to PDF using WeasyPrint
    from flask import make_response
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        font_config = FontConfiguration()
        pdf_bytes = HTML(string=html_content).write_pdf(
            stylesheets=[CSS(string='@page { size: A4; margin: 2cm; }')],
            font_config=font_config
        )
        
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=insurance_quotes_{request_id}.pdf'
        return response
    except ImportError:
        # WeasyPrint not installed - fallback to HTML
        flash('PDF export requires WeasyPrint library. Exporting as HTML instead.', 'info')
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'attachment; filename=insurance_quotes_{request_id}.html'
        return response
    except Exception as e:
        print(f"[PDF export] error: {e}")
        flash(f'PDF generation failed: {str(e)}. Exporting as HTML instead.', 'warning')
        response = make_response(html_content)
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
    AI-Assisted Clinical Record Analysis (Saahir Khan - Use Case 2)
    
    Upload medical documents for complete AI pipeline analysis using UC2_models pipeline:
    1. OCR - Extract text from PDFs/images
    2. Sectionizer - Split into medical categories
    3. NER - Identify entities (problems, medications, allergies, lab tests)
    4. Entity Linking - Map to ICD-10-AM, SNOMED, RxNorm
    5. FHIR Mapping - Generate FHIR R4 bundle
    6. Explanation - Generate patient-friendly summary with glossary and risks
    7. Safety Check - Detect red flags and contraindications
    
    Outputs: summary_md, risks_md, safety_flags_json, fhir_data
    """
    form = ClinicalRecordAnalysisForm()
    
    if form.validate_on_submit():
        try:
            # Get uploaded file
            uploaded_file = form.medical_document.data
            if not uploaded_file or not uploaded_file.filename:
                flash('Please select a medical document to analyze.', 'danger')
                return render_template('clinical_analysis_upload.html', form=form, pipeline_available=PIPELINE_AVAILABLE)
            
            # Get user ID for folder structure
            try:
                user_id = int(current_user.id) if isinstance(current_user.id, (int, str)) else current_user.id
            except (ValueError, TypeError):
                try:
                    from db_auth import fetch_user as db_fetch_user
                    db_user = db_fetch_user(current_user.username)
                    if db_user and db_user.get('id'):
                        user_id = int(db_user['id'])
                    else:
                        user_id = current_user.id
                except Exception:
                    user_id = current_user.id
            
            # Generate analysis_id before saving file (to use in folder name)
            from datetime import datetime
            analysis_id_temp = f"CA-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # Create folder structure: uploads/user_id_analysis_id/
            folder_name = f"{user_id}_{analysis_id_temp}"
            user_analysis_folder = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
            os.makedirs(user_analysis_folder, exist_ok=True)
            
            # Save uploaded file in user_id_analysis_id folder
            original_filename = uploaded_file.filename
            filename = secure_filename(original_filename)
            file_path = os.path.join(user_analysis_folder, filename)
            uploaded_file.save(file_path)
            
            # Store relative path (user_id_analysis_id/filename) for database
            relative_file_path = os.path.join(folder_name, filename)
            
            # Get file info before processing (for saving to RDS)
            from hashlib import sha256
            file_size = os.path.getsize(file_path)
            file_size_mb = round(file_size / (1024 * 1024), 3)
            
            print(f"\n{'='*70}")
            print(f"📄 CLINICAL DOCUMENT UPLOAD")
            print(f"{'='*70}")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Filename: {filename}")
            print(f"Original Filename: {original_filename}")
            print(f"File Size: {file_size_mb} MB ({file_size:,} bytes)")
            print(f"Document Type: {form.document_type.data}")
            print(f"User: {current_user.username} ({current_user.role})")
            print(f"User ID: {user_id}")
            print(f"Analysis ID: {analysis_id_temp}")
            print(f"Folder: {folder_name}")
            print(f"File Path: {relative_file_path}")
            if form.patient_name.data:
                print(f"Patient Name: {form.patient_name.data}")
            if form.notes.data:
                print(f"Notes: {form.notes.data[:100]}..." if len(form.notes.data) > 100 else f"Notes: {form.notes.data}")
            print(f"{'='*70}\n")
            
            # Save file info to session for processing page
            session['clinical_analysis_file'] = {
                'file_path': file_path,
                'relative_path': relative_file_path,
                'filename': filename,
                'original_filename': original_filename,
                'file_size_mb': file_size_mb,
                'document_type': form.document_type.data,
                'patient_name': form.patient_name.data or None,
                'notes': form.notes.data or None,
                'user_id': user_id,
                'analysis_id': analysis_id_temp  # Store the analysis_id for later use
            }
            
            # Redirect to processing page instead of processing directly
            return redirect(url_for('processing_clinical_analysis', analysis_id=analysis_id_temp))
                
        except Exception as e:
            import traceback
            print(f"✗ Error processing clinical document: {e}")
            print(traceback.print_exc())
            flash(f'An error occurred: {str(e)}', 'danger')
            return render_template('clinical_analysis_upload.html', form=form, pipeline_available=PIPELINE_AVAILABLE)
    
    return render_template('clinical_analysis_upload.html', form=form, pipeline_available=PIPELINE_AVAILABLE)


@app.route('/clinical-analysis/processing/<analysis_id>')
@login_required
@role_required('doctor', 'patient')
def processing_clinical_analysis(analysis_id):
    """Display processing page with progress bar"""
    return render_template('processing_clinical_analysis.html', analysis_id=analysis_id)


@app.route('/clinical-analysis/process-now/<analysis_id>', methods=['POST'])
@login_required
def process_clinical_analysis_now(analysis_id):
    """Start background processing and return immediately."""
    import threading
    
    # Get file info from session
    file_info = session.get('clinical_analysis_file')
    if not file_info:
        return jsonify({'success': False, 'message': 'File information not found'}), 404
    
    file_path = file_info['file_path']
    document_type = file_info['document_type']
    patient_name = file_info.get('patient_name')
    notes = file_info.get('notes')
    
    # Capture user_id before starting thread (current_user not available in threads)
    # Convert to int for database operations, but keep as string for compatibility
    try:
        user_id_int = int(current_user.id) if current_user.is_authenticated else None
        user_id_str = str(current_user.id) if current_user.is_authenticated else None
    except (ValueError, TypeError):
        user_id_int = None
        user_id_str = None
    user_id = user_id_int  # Use int version for database
    username = getattr(current_user, 'username', 'unknown')
    
    # Initialize progress
    PROGRESS[analysis_id] = {'pct': 2, 'status': 'Initializing...', 'done': False, 'success': None, 'results_url': None}
    
    def cb(pct: int, msg: str):
        PROGRESS[analysis_id] = {**PROGRESS.get(analysis_id, {}), 'pct': int(pct), 'status': msg}
    
    def worker():
        try:
            from datetime import datetime
            from hashlib import sha256
            from rds_repository import save_medical_record_to_rds
            
            # Process document through complete AI pipeline
            print(f"🚀 Starting UC2 AI Medical Pipeline Processing...\n")
            pipeline_start_time = datetime.now()
            
            result = process_clinical_document(
                file_path=file_path,
                document_type=document_type,
                patient_name=patient_name,
                notes=notes,
                progress_cb=cb
            )
            
            pipeline_end_time = datetime.now()
            pipeline_duration = (pipeline_end_time - pipeline_start_time).total_seconds()
            
            # Keep the uploaded file for future access (don't delete)
            # File is saved in user_id_analysis_id folder and path stored in database
            relative_file_path = file_info.get('relative_path')
            original_filename = file_info.get('original_filename') or file_info.get('filename')
            print(f"\n💾 File saved for future access: {relative_file_path or file_info.get('filename')}")
            
            print(f"[Worker Debug] Pipeline completed. result.success={result.success}, result.analysis_id={result.analysis_id}")
            print(f"[Worker Debug] user_id={user_id}, relative_file_path={relative_file_path}, original_filename={original_filename}")
            
            if result.success:
                # Save result (with patient ID, notes, and file path for database storage)
                # This function handles ALL RDS saving (medical_record, FHIR, explanation, safety flags, processing jobs, complete analysis data)
                try:
                    # Ensure patient_id is passed (as int or string, save_analysis_result will convert)
                    actual_analysis_id = save_analysis_result(
                        result, 
                        patient_id=str(user_id) if user_id else None,  # Pass as string, will be converted to int inside
                        notes=notes,
                        file_path=relative_file_path,
                        original_filename=original_filename
                    )
                    print(f"[Worker Debug] save_analysis_result returned: {actual_analysis_id}")
                except Exception as save_error:
                    # Even if saving to RDS fails, we still want to show the results
                    print(f"⚠️ Warning: Failed to save to RDS, but analysis was successful: {save_error}")
                    import traceback
                    traceback.print_exc()
                    actual_analysis_id = result.analysis_id
                
                # The duplicate save_medical_record_to_rds call below is redundant since save_analysis_result already handles it
                # But keeping it for backward compatibility if needed
                
                print(f"\n{'='*70}")
                print(f"📊 ANALYSIS RESULTS SUMMARY")
                print(f"{'='*70}")
                print(f"Analysis ID: {result.analysis_id}")
                print(f"Patient: {result.patient_name or 'Unknown'}")
                print(f"Conditions Found: {len(result.conditions)}")
                print(f"Medications Found: {len(result.medications)}")
                print(f"Risk Level: {result.risk_level.upper()}")
                print(f"Red Flags: {len(result.red_flags)}")
                print(f"Mistral LLM Analysis: {'✓ Available' if result.mistral_analysis else '✗ Not available'}")
                print(f"{'='*70}\n")
                
                # CRITICAL: Verify the analysis was saved to RDS
                # If not, try to save it again (retry mechanism)
                try:
                    from rds_repository import get_clinical_analysis_result_from_rds
                    verify_result = get_clinical_analysis_result_from_rds(
                        analysis_id=actual_analysis_id, 
                        patient_user_id=user_id
                    )
                    if not verify_result:
                        print(f"⚠️ WARNING: Analysis {actual_analysis_id} was NOT saved to RDS! Attempting to save now...")
                        # Retry save one more time
                        try:
                            retry_analysis_id = save_analysis_result(
                                result,
                                patient_id=str(user_id) if user_id else None,
                                notes=notes,
                                file_path=relative_file_path,
                                original_filename=original_filename
                            )
                            print(f"✓ Retry save completed: {retry_analysis_id}")
                        except Exception as retry_error:
                            print(f"✗ Retry save also failed: {retry_error}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"✓ Verified: Analysis {actual_analysis_id} is saved in RDS")
                except Exception as verify_error:
                    print(f"⚠️ Could not verify RDS save status: {verify_error}")
                
                # Build results URL manually (url_for doesn't work in threads without request context)
                url = f'/clinical-analysis/results/{actual_analysis_id}'
                print(f"✅ [PROGRESS 100%] Analysis complete! Results URL: {url}")
                
                PROGRESS[analysis_id] = {
                    'pct': 100,
                    'status': 'Analysis complete!',
                    'done': True,
                    'success': True,
                    'results_url': url
                }
            else:
                url = '/clinical-analysis'
                print(f"❌ [PROGRESS 100%] Analysis failed! Redirecting to upload page.")
                
                PROGRESS[analysis_id] = {
                    'pct': 100,
                    'status': f'Analysis failed: {result.error_message}',
                    'done': True,
                    'success': False,
                    'results_url': url
                }
            
            print(f"🎯 [PROGRESS UPDATE] Progress bar reached 100% - Status: {PROGRESS[analysis_id]['status']}")
            
            # Clear session data
            try:
                session.pop('clinical_analysis_file', None)
            except Exception:
                pass
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            # If the analysis result exists, try to show it even if saving failed
            error_url = '/clinical-analysis'
            error_message = str(e)
            print(f"💥 [PROGRESS 100%] Error occurred during processing: {error_message}")
            print(f"[Worker Debug] Exception in worker thread: {type(e).__name__}: {e}")
            traceback.print_exc()
            
            # Check if we have a result object (even if saving failed)
            if 'result' in locals() and result and result.success:
                # Analysis succeeded but saving failed - still show results
                try:
                    actual_analysis_id = result.analysis_id
                    url = f'/clinical-analysis/results/{actual_analysis_id}'
                    print(f"⚠️  Showing results despite save error: {url}")
                    PROGRESS[analysis_id] = {
                        'pct': 100,
                        'status': f'Analysis complete (save warning: {error_message[:50]}...)',
                        'done': True,
                        'success': True,
                        'results_url': url
                    }
                except:
                    # Fallback to error page
                    PROGRESS[analysis_id] = {
                        'pct': 100,
                        'status': f'Error: {error_message}',
                        'done': True,
                        'success': False,
                        'results_url': error_url
                    }
            else:
                # Analysis failed or no result - show error page
                PROGRESS[analysis_id] = {
                    'pct': 100,
                    'status': f'Error: {error_message}',
                    'done': True,
                    'success': False,
                    'results_url': error_url
                }
            print(f"🎯 [PROGRESS UPDATE] Progress bar reached 100% (with error) - Status: {PROGRESS[analysis_id]['status']}")
    
    threading.Thread(target=worker, daemon=True).start()
    return jsonify({'success': True})


@app.route('/clinical-analysis/progress/<analysis_id>')
@login_required
def clinical_analysis_progress(analysis_id):
    """Return current progress status"""
    data = PROGRESS.get(analysis_id) or {'pct': 0, 'status': 'Pending', 'done': False}
    return jsonify(data)


@app.route('/clinical-analysis/results/<analysis_id>')
@login_required
@role_required('doctor', 'patient')
def clinical_analysis_results(analysis_id):
    """
    Display complete analysis results with all extracted data
    """
    # Get current user ID and filter by user to ensure they can only see their own analyses
    try:
        patient_user_id = int(str(current_user.id)) if current_user.is_authenticated else None
    except (ValueError, TypeError):
        patient_user_id = None
    
    result = get_analysis_result(analysis_id, patient_user_id=patient_user_id)
    
    if not result:
        flash('Analysis not found or you do not have permission to view this analysis.', 'danger')
        return redirect(url_for('clinical_analysis'))
    
    # If file_path is missing but analysis exists, try to find the file in uploads folder
    if not getattr(result, 'file_path', None) and analysis_id.startswith('CA-'):
        import os
        # Files are stored in uploads/user_id_analysis_id/filename.pdf
        # First try with patient_user_id from current user
        user_id_to_try = patient_user_id
        
        # If patient_user_id is None, try to get it from result or current_user
        if not user_id_to_try:
            # Try to extract from result if available
            if hasattr(result, 'patient_id') and result.patient_id:
                try:
                    user_id_to_try = int(str(result.patient_id))
                except (ValueError, TypeError):
                    pass
            
            # If still None, try current_user
            if not user_id_to_try and current_user.is_authenticated:
                try:
                    user_id_to_try = int(str(current_user.id))
                except (ValueError, TypeError):
                    pass
        
        if user_id_to_try:
            pattern_folder = f"{user_id_to_try}_{analysis_id}"
            pattern_path = os.path.join(app.config['UPLOAD_FOLDER'], pattern_folder)
            if os.path.exists(pattern_path):
                # Find any files in that folder
                try:
                    for f in os.listdir(pattern_path):
                        if f.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.txt', '.doc', '.docx')):
                            result.file_path = os.path.join(pattern_folder, f)
                            if not getattr(result, 'original_filename', None):
                                result.original_filename = f
                            print(f"[Results Debug] Found file on disk: {result.file_path}")
                            break
                except Exception as e:
                    print(f"[Results Debug] Error scanning folder {pattern_path}: {e}")
        else:
            print(f"[Results Debug] Could not determine user_id to search for file")
    
    # Debug: Log file_path information
    print(f"[Results Debug] Analysis ID: {analysis_id}")
    print(f"[Results Debug] result.file_path: {getattr(result, 'file_path', None)}")
    print(f"[Results Debug] result.original_filename: {getattr(result, 'original_filename', None)}")
    print(f"[Results Debug] Has file: {bool(getattr(result, 'file_path', None) or getattr(result, 'original_filename', None))}")
    
    return render_template('clinical_analysis_results.html', result=result)


@app.route('/clinical-analysis/history')
@login_required
@role_required('doctor', 'patient')
def clinical_analysis_history():
    """
    View history of clinical document analyses
    """
    try:
        # Get current user ID
        try:
            patient_user_id = int(str(current_user.id)) if current_user.is_authenticated else None
        except (ValueError, TypeError):
            patient_user_id = None
        
        if not patient_user_id:
            flash('Unable to identify user.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get history from database with review status
        from rds_repository import get_clinical_analysis_history_for_user
        history = get_clinical_analysis_history_for_user(patient_user_id, limit=50)
        
        # Fallback to in-memory if no database history
        if not history:
            history = get_user_analysis_history(current_user.id)
        
        return render_template('clinical_analysis_history.html', analyses=history)
    except Exception as e:
        import traceback
        print(f"[Analysis History] Error: {e}")
        traceback.print_exc()
        flash(f'Error loading analysis history: {str(e)}', 'danger')
        # Fallback to in-memory
        history = get_user_analysis_history(current_user.id)
        return render_template('clinical_analysis_history.html', analyses=history)


@app.route('/clinical-analysis/download/<analysis_id>/fhir')
@login_required
@role_required('doctor', 'patient', 'admin')
def download_fhir_bundle(analysis_id):
    """
    Download FHIR R4 bundle as JSON
    """
    # Get current user ID and filter by user
    try:
        patient_user_id = int(str(current_user.id)) if current_user.is_authenticated else None
    except (ValueError, TypeError):
        patient_user_id = None
    
    result = get_analysis_result(analysis_id, patient_user_id=patient_user_id)
    
    if not result or not result.fhir_bundle:
        flash('FHIR bundle not found or you do not have permission to access it.', 'danger')
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
    # Get current user ID and filter by user
    try:
        patient_user_id = int(str(current_user.id)) if current_user.is_authenticated else None
    except (ValueError, TypeError):
        patient_user_id = None
    
    result = get_analysis_result(analysis_id, patient_user_id=patient_user_id)
    
    if not result:
        flash('Analysis not found or you do not have permission to access it.', 'danger')
        return redirect(url_for('clinical_analysis'))
    
    # Return as JSON download
    from flask import make_response
    response = make_response(json.dumps(result.to_dict(), indent=2, default=str))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=clinical_analysis_{analysis_id}.json'
    
    return response


@app.route('/clinical-analysis/view/<analysis_id>/file')
@login_required
@role_required('doctor', 'patient')
def view_clinical_analysis_file(analysis_id):
    """
    View the original uploaded file for a clinical analysis in the browser
    """
    try:
        # Get user ID for verification
        try:
            user_id = int(current_user.id) if isinstance(current_user.id, (int, str)) else current_user.id
        except (ValueError, TypeError):
            try:
                from db_auth import fetch_user as db_fetch_user
                db_user = db_fetch_user(current_user.username)
                if db_user and db_user.get('id'):
                    user_id = int(db_user['id'])
                else:
                    user_id = current_user.id
            except Exception:
                user_id = current_user.id
        
        # Get analysis result from RDS or in-memory storage
        result = get_analysis_result(analysis_id, patient_user_id=user_id)
        
        if not result:
            flash('Analysis not found or you do not have permission to access it.', 'danger')
            return redirect(url_for('clinical_analysis_history'))
        
        # Get file path from result
        file_path = getattr(result, 'file_path', None)
        if not file_path:
            flash('File not found for this analysis.', 'warning')
            return redirect(url_for('clinical_analysis_results', analysis_id=analysis_id))
        
        # Build full file path
        # file_path is relative (e.g., "user_id_analysis_id/filename.pdf")
        full_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
        
        # Verify file exists
        if not os.path.exists(full_file_path):
            flash('File not found on server.', 'warning')
            return redirect(url_for('clinical_analysis_results', analysis_id=analysis_id))
        
        # Get original filename for display
        original_filename = getattr(result, 'original_filename', None) or os.path.basename(file_path)
        
        # Determine MIME type based on file extension
        file_ext = os.path.splitext(original_filename)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.txt': 'text/plain'
        }
        mimetype = mime_types.get(file_ext, 'application/octet-stream')
        
        # Return file for viewing in browser (inline)
        from flask import send_file
        return send_file(
            full_file_path,
            as_attachment=False,  # Display in browser, don't download
            download_name=original_filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        import traceback
        print(f"✗ Error viewing file: {e}")
        traceback.print_exc()
        flash(f'Error viewing file: {str(e)}', 'danger')
        return redirect(url_for('clinical_analysis_history'))


@app.route('/clinical-analysis/download/<analysis_id>/file')
@login_required
@role_required('doctor', 'patient')
def download_clinical_analysis_file(analysis_id):
    """
    Download the original uploaded file for a clinical analysis
    """
    try:
        # Get user ID for verification
        try:
            user_id = int(current_user.id) if isinstance(current_user.id, (int, str)) else current_user.id
        except (ValueError, TypeError):
            try:
                from db_auth import fetch_user as db_fetch_user
                db_user = db_fetch_user(current_user.username)
                if db_user and db_user.get('id'):
                    user_id = int(db_user['id'])
                else:
                    user_id = current_user.id
            except Exception:
                user_id = current_user.id
        
        # Get analysis result from RDS or in-memory storage
        result = get_analysis_result(analysis_id, patient_user_id=user_id)
        
        if not result:
            flash('Analysis not found or you do not have permission to access it.', 'danger')
            return redirect(url_for('clinical_analysis_history'))
        
        # Get file path from result
        file_path = getattr(result, 'file_path', None)
        if not file_path:
            flash('File not found for this analysis.', 'warning')
            return redirect(url_for('clinical_analysis_results', analysis_id=analysis_id))
        
        # Build full file path
        # file_path is relative (e.g., "user_id_analysis_id/filename.pdf")
        full_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
        
        # Verify file exists
        if not os.path.exists(full_file_path):
            flash('File not found on server.', 'warning')
            return redirect(url_for('clinical_analysis_results', analysis_id=analysis_id))
        
        # Get original filename for download
        original_filename = getattr(result, 'original_filename', None) or os.path.basename(file_path)
        
        # Return file for download
        from flask import send_file
        return send_file(
            full_file_path,
            as_attachment=True,  # Download file
            download_name=original_filename
        )
        
    except Exception as e:
        import traceback
        print(f"✗ Error downloading file: {e}")
        traceback.print_exc()
        flash(f'Error downloading file: {str(e)}', 'danger')
        return redirect(url_for('clinical_analysis_history'))


@app.route('/clinical-analysis/recommend-doctors/<analysis_id>')
@login_required
@role_required('patient')
def recommend_doctors_for_analysis(analysis_id):
    """
    Find suitable doctors for a clinical analysis using AI.
    Uses Mistral:7b-instruct to analyze the results and recommend doctors.
    """
    try:
        # Get current user ID
        try:
            patient_user_id = int(str(current_user.id)) if current_user.is_authenticated else None
        except (ValueError, TypeError):
            patient_user_id = None
        
        # Get the analysis result
        result = get_analysis_result(analysis_id, patient_user_id=patient_user_id)
        
        if not result:
            flash('Analysis not found or you do not have permission to view it.', 'danger')
            return redirect(url_for('clinical_analysis'))
        
        # Get all approved doctors
        all_doctors = get_all_approved_doctors()
        
        if not all_doctors:
            flash('No approved doctors available for recommendation.', 'warning')
            return redirect(url_for('clinical_analysis_results', analysis_id=analysis_id))
        
        # Prepare clinical result data for recommendation
        clinical_data = {
            'conditions': result.conditions or [],
            'medications': result.medications or [],
            'risk_level': result.risk_level or 'UNKNOWN',
            'observations': getattr(result, 'observations', []) or [],
            'procedures': getattr(result, 'procedures', []) or [],
        }
        
        # Use AI to recommend doctors
        print(f"[Doctor Recommendation] Finding suitable doctors for analysis {analysis_id}...")
        recommended = recommend_doctors(clinical_data, all_doctors)
        
        if not recommended:
            flash('Could not generate doctor recommendations at this time. Please try again later.', 'warning')
            return redirect(url_for('clinical_analysis_results', analysis_id=analysis_id))
        
        print(f"[Doctor Recommendation] Recommended {len(recommended)} doctors")
        
        # Pass recommendations to template
        return render_template('doctor_recommendations.html', 
                             recommended_doctors=recommended,
                             analysis_id=analysis_id,
                             analysis_result=result)
        
    except Exception as e:
        import traceback
        print(f"[Doctor Recommendation] Error: {e}")
        traceback.print_exc()
        flash(f'Error finding doctor recommendations: {str(e)}', 'danger')
        return redirect(url_for('clinical_analysis_results', analysis_id=analysis_id))


@app.route('/clinical-analysis/request-review/<analysis_id>/<int:doctor_user_id>', methods=['POST'])
@login_required
@role_required('patient')
def request_doctor_review(analysis_id, doctor_user_id):
    """
    Request a doctor to review a clinical analysis.
    Creates a pending review entry in the database.
    """
    try:
        # Get current user ID
        try:
            patient_user_id = int(str(current_user.id)) if current_user.is_authenticated else None
        except (ValueError, TypeError):
            patient_user_id = None
        
        if not patient_user_id:
            flash('Unable to identify patient user.', 'danger')
            return redirect(url_for('recommend_doctors_for_analysis', analysis_id=analysis_id))
        
        # Get the analysis result to find medical_record_id
        result = get_analysis_result(analysis_id, patient_user_id=patient_user_id)
        if not result:
            flash('Analysis not found or you do not have permission to view it.', 'danger')
            return redirect(url_for('recommend_doctors_for_analysis', analysis_id=analysis_id))
        
        # Get medical_record_id from database using analysis_id (file_hash)
        from rds_repository import _conn
        from psycopg2.extras import RealDictCursor
        import os
        
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id FROM medical_records 
                WHERE file_hash = %s AND patient_id = %s
                LIMIT 1
            """, (analysis_id, patient_user_id))
            mr_row = cur.fetchone()
            
            if not mr_row:
                flash('Medical record not found in database.', 'danger')
                return redirect(url_for('recommend_doctors_for_analysis', analysis_id=analysis_id))
            
            medical_record_id = mr_row['id']
        
        # Get optional notes from form
        notes = request.form.get('notes', '').strip() or None
        
        # Save review request to database
        approval_id = save_review_request(
            patient_user_id=patient_user_id,
            doctor_user_id=doctor_user_id,
            medical_record_id=medical_record_id,
            analysis_id=analysis_id,
            notes=notes
        )
        
        if approval_id:
            flash(f'Review request sent successfully to the doctor. You will be notified when the review is completed.', 'success')
        else:
            flash('Review request may have already been sent. Please check your analysis history.', 'info')
        
        return redirect(url_for('recommend_doctors_for_analysis', analysis_id=analysis_id))
        
    except Exception as e:
        import traceback
        print(f"[Request Review] Error: {e}")
        traceback.print_exc()
        flash(f'Error sending review request: {str(e)}', 'danger')
        return redirect(url_for('recommend_doctors_for_analysis', analysis_id=analysis_id))


@app.route('/doctor/profile/<int:doctor_user_id>')
@login_required
@role_required('patient', 'doctor', 'admin')
def view_doctor_profile(doctor_user_id):
    """
    View complete doctor profile (accessible by patients, doctors, and admins).
    """
    try:
        print(f"[View Doctor Profile] Attempting to fetch profile for doctor_user_id={doctor_user_id}")
        profile = get_doctor_complete_profile(doctor_user_id)
        
        if not profile:
            print(f"[View Doctor Profile] Profile not found for doctor_user_id={doctor_user_id}")
            flash('Doctor profile not found. The doctor may not be registered in the system.', 'danger')
            # Try to redirect back to recommendations if coming from there
            referrer = request.referrer
            if referrer and 'recommend-doctors' in referrer:
                return redirect(referrer)
            elif current_user.role == 'patient':
                return redirect(url_for('clinical_analysis_history'))
            elif current_user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('admin_dashboard'))
        
        print(f"[View Doctor Profile] Successfully loaded profile for doctor_user_id={doctor_user_id}: {profile.get('name') or profile.get('username')}")
        
        # Check if doctor is approved (patients can only view approved doctors)
        if current_user.role == 'patient' and profile.get('approval_status') != 'Approved':
            flash('This doctor profile is not available for viewing. Only approved doctors are visible to patients.', 'warning')
            return redirect(url_for('clinical_analysis_history'))
        
        return render_template('patient_doctor_profile.html', doctor=profile)
        
    except Exception as e:
        import traceback
        print(f"[View Doctor Profile] Error: {e}")
        traceback.print_exc()
        flash(f'Error loading doctor profile: {str(e)}', 'danger')
        if current_user.role == 'patient':
            return redirect(url_for('clinical_analysis_history'))
        elif current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        else:
            return redirect(url_for('admin_dashboard'))


@app.route('/clinical-analysis/delete/<analysis_id>', methods=['POST'])
@login_required
@role_required('doctor', 'patient')
def delete_clinical_analysis(analysis_id):
    """
    Delete a clinical analysis - COMING SOON
    Currently shows a "Coming Soon" message instead of deleting
    """
    flash('Delete functionality is coming soon! This feature is currently under development.', 'info')
    return redirect(url_for('clinical_analysis_history'))
    
    # TODO: Original delete functionality will be restored here in the future
    # The code below is commented out but preserved for future implementation:
    """
    try:
        # Get user ID for ownership verification
        try:
            user_id = int(current_user.id) if isinstance(current_user.id, (int, str)) else current_user.id
        except (ValueError, TypeError):
            try:
                from db_auth import fetch_user as db_fetch_user
                db_user = db_fetch_user(current_user.username)
                if db_user and db_user.get('id'):
                    user_id = int(db_user['id'])
                else:
                    user_id = current_user.id
            except Exception:
                user_id = current_user.id
        
        # Get analysis result to verify ownership
        result = get_analysis_result(analysis_id, patient_user_id=user_id)
        
        if not result:
            flash('Analysis not found or you do not have permission to delete it.', 'danger')
            return redirect(url_for('clinical_analysis_history'))
        
        deleted_from_rds = False
        deleted_from_memory = False
        
        # Delete from RDS
        try:
            if os.environ.get('USE_RDS_LOGIN', 'true').lower() in {'1','true','yes'}:
                from rds_repository import delete_clinical_analysis_from_rds
                if delete_clinical_analysis_from_rds(analysis_id=analysis_id, patient_user_id=user_id):
                    deleted_from_rds = True
                    print(f"[DELETE] Successfully deleted analysis {analysis_id} from RDS")
        except Exception as e:
            print(f"[DELETE] Error deleting from RDS: {e}")
            import traceback
            traceback.print_exc()
        
        # Delete from in-memory storage
        try:
            from clinical_analysis_processor import analysis_results_storage
            if analysis_id in analysis_results_storage:
                del analysis_results_storage[analysis_id]
                deleted_from_memory = True
                print(f"[DELETE] Successfully deleted analysis {analysis_id} from in-memory storage")
        except Exception as e:
            print(f"[DELETE] Error deleting from in-memory storage: {e}")
        
        if deleted_from_rds or deleted_from_memory:
            flash('Analysis deleted successfully.', 'success')
        else:
            flash('Analysis not found or could not be deleted.', 'warning')
        
    except Exception as e:
        import traceback
        print(f"✗ Error deleting analysis: {e}")
        traceback.print_exc()
        flash(f'Error deleting analysis: {str(e)}', 'danger')
    
    return redirect(url_for('clinical_analysis_history'))
    """


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
    Filters by logged-in doctor's ID
    """
    try:
        # Get current doctor user ID
        try:
            doctor_user_id = int(str(current_user.id)) if current_user.is_authenticated else None
        except (ValueError, TypeError):
            doctor_user_id = None
        
        if not doctor_user_id:
            flash('Unable to identify doctor user.', 'danger')
            return redirect(url_for('doctor_dashboard'))
        
        # Get pending reviews for this specific doctor from database
        pending_reviews_db = get_pending_reviews_for_doctor(doctor_user_id)
        
        # Load analysis results for pending reviews
        pending_analyses = []
        for review in pending_reviews_db:
            analysis_id = review.get('analysis_id')
            patient_user_id = review.get('patient_id')
            
            if analysis_id:
                result = get_analysis_result(analysis_id, patient_user_id=patient_user_id)
                if result:
                    # Create review package
                    review_package = create_review_package(result)
                    # Convert dataclass to dict and add database review info
                    try:
                        from dataclasses import asdict
                        review_dict = asdict(review_package)
                    except Exception:
                        # Fallback: manually convert if asdict fails
                        review_dict = {
                            'analysis_id': review_package.analysis_id,
                            'patient_id': review_package.patient_id,
                            'document_type': review_package.document_type,
                            'processed_at': review_package.processed_at,
                            'fhir_data': review_package.fhir_data,
                            'summary_md': review_package.summary_md,
                            'risks_md': review_package.risks_md,
                            'safety_flags': [{'flag_id': f.flag_id, 'severity': f.severity.value if hasattr(f.severity, 'value') else str(f.severity), 'description': f.description} for f in review_package.safety_flags] if review_package.safety_flags else [],
                            'overall_confidence': review_package.overall_confidence,
                            'low_confidence_areas': review_package.low_confidence_areas,
                            'has_critical_flags': review_package.has_critical_flags,
                            'requires_mandatory_override': review_package.requires_mandatory_override,
                        }
                    review_dict['review_info'] = review
                    pending_analyses.append(review_dict)
        
        # NO FALLBACK to in-memory reviews - we only use database now
        # This ensures reviews disappear immediately after submission
        print(f"[Pending AI Reviews] Returning {len(pending_analyses)} reviews from database")
        
        return render_template('pending_ai_reviews.html',
                             pending_analyses=pending_analyses,
                             count=len(pending_analyses))
    except Exception as e:
        import traceback
        print(f"[Pending Reviews] Error: {e}")
        traceback.print_exc()
        flash(f'Error loading pending reviews: {str(e)}', 'danger')
        return redirect(url_for('doctor_dashboard'))


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
    
    # Get approval_id from database if this is a review request
    approval_id = None
    try:
        doctor_user_id = int(str(current_user.id)) if current_user.is_authenticated else None
        if doctor_user_id:
            from rds_repository import _conn
            from psycopg2.extras import RealDictCursor
            
            with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT aa.id AS approval_id
                    FROM medical_records mr
                    JOIN ai_approvals aa ON aa.medical_record_id = mr.id 
                    WHERE mr.file_hash = %s
                    AND aa.doctor_id = %s
                    AND aa.signed_at IS NULL
                    LIMIT 1
                """, (analysis_id, doctor_user_id))
                
                approval_row = cur.fetchone()
                if approval_row:
                    approval_id = approval_row.get('approval_id')
    except Exception as e:
        print(f"[Review] Error getting approval_id: {e}")
    
    if request.method == 'POST':
        # Simple: just get the status and update database
        status_value = request.form.get('status', '').lower()
        
        # Map status to database enum values
        status_map = {
            'approved': 'Approved',
            'rejected': 'Rejected',
            'needs_revision': 'NeedsChanges',
            'escalated': 'NeedsChanges'  # Escalate also maps to NeedsChanges
        }
        
        db_decision = status_map.get(status_value, 'NeedsChanges')
        notes = request.form.get('notes', '')
        
        print(f"[Review Submit] Status: '{status_value}' -> DB decision: '{db_decision}'")
        
        # Update database
        try:
            from rds_repository import _conn, update_approval_decision_in_rds
            from psycopg2.extras import RealDictCursor
            
            with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Find the approval_id from analysis_id
                cur.execute("""
                    SELECT aa.id AS approval_id
                    FROM medical_records mr
                    JOIN ai_approvals aa ON aa.medical_record_id = mr.id 
                    WHERE mr.file_hash = %s
                    AND aa.doctor_id = %s
                    AND aa.signed_at IS NULL
                    LIMIT 1
                """, (analysis_id, int(str(current_user.id))))
                
                approval_row = cur.fetchone()
                if approval_row and approval_row.get('approval_id'):
                    approval_id = approval_row['approval_id']
                    
                    # Update the approval in database
                    success = update_approval_decision_in_rds(
                        approval_id=approval_id,
                        doctor_user_id=int(str(current_user.id)),
                        decision=db_decision,
                        notes=notes,
                        signed_at=datetime.now()
                    )
                    
                    if success:
                        print(f"[Review Submit] ✅ Successfully updated approval {approval_id} in database with status: {db_decision}")
                        
                        # Verify the update is visible by querying immediately
                        cur.execute("""
                            SELECT signed_at FROM ai_approvals 
                            WHERE id = %s AND doctor_id = %s
                        """, (approval_id, int(str(current_user.id))))
                        verify_row = cur.fetchone()
                        if verify_row:
                            # RealDictCursor returns dict-like objects, so use key access
                            signed_at_value = verify_row.get('signed_at') if isinstance(verify_row, dict) else verify_row[0]
                            print(f"[Review Submit] Verification: approval {approval_id} signed_at={signed_at_value}")
                            if signed_at_value is None:
                                print(f"[Review Submit] ⚠️ WARNING: signed_at is still NULL after update!")
                        
                        # Flash message
                        if status_value == 'approved':
                            flash('✓ Review approved. Status updated in database.', 'success')
                        elif status_value == 'rejected':
                            flash('Review rejected. Status updated in database.', 'info')
                        elif status_value == 'escalated':
                            flash('Review escalated. Status updated in database.', 'warning')
                        else:
                            flash('Review status updated in database.', 'info')
                    else:
                        print(f"[Review Submit] ⚠️ Failed to update approval in database")
                        flash('Failed to update status in database.', 'danger')
                else:
                    print(f"[Review Submit] ⚠️ No pending approval found for analysis {analysis_id}")
                    flash('No pending approval found for this analysis.', 'warning')
                    
        except Exception as e:
            import traceback
            print(f"[Review Submit] ❌ Error updating database: {e}")
            traceback.print_exc()
            flash(f'Error updating status: {str(e)}', 'danger')
        
        # Force redirect with cache-busting parameter to ensure fresh data
        from flask import redirect, url_for
        return redirect(url_for('pending_ai_reviews', _external=False) + '?t=' + str(datetime.now().timestamp()))
    
    # Convert review_package to dict for template
    try:
        from dataclasses import asdict
        review_dict = asdict(review_package)
    except Exception:
        review_dict = {
            'analysis_id': review_package.analysis_id,
            'patient_id': review_package.patient_id,
            'document_type': review_package.document_type,
            'processed_at': review_package.processed_at,
            'fhir_data': review_package.fhir_data,
            'summary_md': review_package.summary_md,
            'risks_md': review_package.risks_md,
            'safety_flags': review_package.safety_flags,
            'overall_confidence': review_package.overall_confidence,
            'low_confidence_areas': review_package.low_confidence_areas,
            'has_critical_flags': review_package.has_critical_flags,
            'requires_mandatory_override': review_package.requires_mandatory_override,
        }
    
    return render_template('review_ai_output.html',
                         review=review_dict,
                         analysis=result,
                         approval_id=approval_id)


@app.route('/review/history')
@login_required
@role_required('doctor', 'admin')
def review_history():
    """
    View history of approval decisions from AWS database
    """
    from rds_repository import get_review_history_from_rds
    
    # For doctors, only show their own reviews. For admins, show all reviews.
    doctor_user_id = None
    if current_user.role == 'doctor':
        try:
            doctor_user_id = int(str(current_user.id))
        except (ValueError, TypeError):
            # If it's a string ID, try to find in database
            try:
                from db_auth import fetch_user as db_fetch_user
                db_user = db_fetch_user(current_user.username)
                if db_user:
                    doctor_user_id = db_user['id']
            except Exception:
                pass
    
    # Fetch from AWS database
    reviews = get_review_history_from_rds(doctor_user_id=doctor_user_id)
    
    # Convert to format expected by template (similar to ApprovalDecision dataclass)
    # The template expects objects with: status.value, decision_id, analysis_id, reviewer_name, timestamp, etc.
    decisions = []
    for review in reviews:
        # Map database decision to ApprovalStatus-like structure
        decision_value = review['decision'].lower()
        if decision_value == 'approved':
            status_value = 'approved'
        elif decision_value == 'rejected':
            status_value = 'rejected'
        elif decision_value == 'needschanges':
            status_value = 'needs_revision'
        else:
            status_value = 'needs_revision'
        
        # Get timestamp - ensure it's a datetime object
        timestamp = review.get('signed_at') or review.get('created_at')
        # If timestamp is a string, parse it; otherwise use as-is (datetime from DB)
        if timestamp and isinstance(timestamp, str):
            try:
                from dateutil.parser import parse
                timestamp = parse(timestamp)
            except:
                timestamp = None
        
        # Create a simple object that mimics ApprovalDecision for the template
        decision_obj = type('Decision', (), {
            'decision_id': f"DEC-{review['approval_id']}",
            'analysis_id': review['analysis_id'],
            'reviewer_name': review['doctor_name'],
            'reviewer_id': review['doctor_id'],
            'status': type('Status', (), {'value': status_value})(),
            'timestamp': timestamp,  # Should be datetime object from DB
            'notes': review['notes'] or '',
            'safety_overrides': [],  # Not stored in DB yet
            'released_to_patient': decision_value == 'approved',
            'medical_record_id': review['medical_record_id'],
            'approval_id': review['approval_id']
        })()
        decisions.append(decision_obj)
    
    # Sort by timestamp (newest first)
    decisions.sort(key=lambda d: d.timestamp or datetime.min, reverse=True)
    
    print(f"[Review History] Displaying {len(decisions)} reviews")
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

