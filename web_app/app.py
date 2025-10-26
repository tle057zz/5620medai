"""
Flask Web Application for Clinical AI Assistance System
Main application file with authentication and role-based access
"""

from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Import our models and forms
from models import User, get_user_by_username, example_users
from forms import LoginForm

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['TEMPLATES_AUTO_RELOAD'] = True

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

