"""
User Models for Clinical AI System
Using in-memory storage for now (will migrate to database later)
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin):
    """User model with role-based access"""
    
    def __init__(self, id, username, email, password_hash, role, first_name, last_name, 
                 specialty=None, license_number=None, date_of_birth=None, medical_record_number=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role  # 'doctor', 'patient', 'admin'
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = datetime.now()
        self.last_login = None
        
        # Doctor-specific fields
        self.specialty = specialty
        self.license_number = license_number
        
        # Patient-specific fields
        self.date_of_birth = date_of_birth
        self.medical_record_number = medical_record_number
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_display_name(self):
        """Return formatted display name"""
        if self.role == 'doctor':
            return f"Dr. {self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def get_role_display(self):
        """Return formatted role name"""
        return self.role.capitalize()
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# ================================
# Example Users (In-Memory Storage)
# ================================

def create_example_users():
    """Create example users for testing"""
    users = {}
    
    # Common password for all example users (in production, use strong passwords)
    password = 'password123'
    password_hash = generate_password_hash(password)
    
    # 1. Example Doctors
    users['dr.smith'] = User(
        id='doc_001',
        username='dr.smith',
        email='sarah.smith@hospital.com',
        password_hash=password_hash,
        role='doctor',
        first_name='Sarah',
        last_name='Smith',
        specialty='Cardiology',
        license_number='MD-12345'
    )
    
    users['dr.jones'] = User(
        id='doc_002',
        username='dr.jones',
        email='michael.jones@hospital.com',
        password_hash=password_hash,
        role='doctor',
        first_name='Michael',
        last_name='Jones',
        specialty='Neurology',
        license_number='MD-67890'
    )
    
    users['dr.chen'] = User(
        id='doc_003',
        username='dr.chen',
        email='lisa.chen@hospital.com',
        password_hash=password_hash,
        role='doctor',
        first_name='Lisa',
        last_name='Chen',
        specialty='General Medicine',
        license_number='MD-11223'
    )
    
    # 2. Example Patients
    users['patient1'] = User(
        id='pat_001',
        username='patient1',
        email='john.doe@email.com',
        password_hash=password_hash,
        role='patient',
        first_name='John',
        last_name='Doe',
        date_of_birth='1975-05-15',
        medical_record_number='MRN-001234'
    )
    
    users['patient2'] = User(
        id='pat_002',
        username='patient2',
        email='jane.wilson@email.com',
        password_hash=password_hash,
        role='patient',
        first_name='Jane',
        last_name='Wilson',
        date_of_birth='1988-09-22',
        medical_record_number='MRN-005678'
    )
    
    users['patient3'] = User(
        id='pat_003',
        username='patient3',
        email='robert.taylor@email.com',
        password_hash=password_hash,
        role='patient',
        first_name='Robert',
        last_name='Taylor',
        date_of_birth='1962-12-03',
        medical_record_number='MRN-009876'
    )
    
    # 3. Example System Administrators
    users['admin'] = User(
        id='adm_001',
        username='admin',
        email='admin@hospital.com',
        password_hash=password_hash,
        role='admin',
        first_name='System',
        last_name='Administrator'
    )
    
    users['it.admin'] = User(
        id='adm_002',
        username='it.admin',
        email='it.admin@hospital.com',
        password_hash=password_hash,
        role='admin',
        first_name='IT',
        last_name='Administrator'
    )
    
    return users


# Initialize example users
example_users = create_example_users()


# ================================
# Helper Functions
# ================================

def get_user_by_username(username):
    """Retrieve user by username"""
    return example_users.get(username)


def get_user_by_id(user_id):
    """Retrieve user by ID"""
    for user in example_users.values():
        if user.id == user_id:
            return user
    return None


def get_users_by_role(role):
    """Get all users with specific role"""
    return [user for user in example_users.values() if user.role == role]


def add_user(user):
    """Add new user to storage"""
    if user.username in example_users:
        return False
    example_users[user.username] = user
    return True


def update_user(user):
    """Update existing user"""
    if user.username in example_users:
        example_users[user.username] = user
        return True
    return False


def delete_user(username):
    """Delete user from storage"""
    if username in example_users:
        del example_users[username]
        return True
    return False

