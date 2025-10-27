"""
Flask-WTF Forms for Clinical AI System
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, IntegerField, FloatField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional, NumberRange


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=50)],
                          render_kw={'placeholder': 'Enter your username', 'autofocus': True})
    
    password = PasswordField('Password', 
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Enter your password'})
    
    remember_me = BooleanField('Remember Me')
    
    submit = SubmitField('Sign In')


class UploadDocumentForm(FlaskForm):
    """Form for uploading medical documents"""
    document_type = SelectField('Document Type',
                               choices=[
                                   ('medical_report', 'Medical Report'),
                                   ('lab_results', 'Lab Results'),
                                   ('prescription', 'Prescription'),
                                   ('imaging', 'Imaging Report'),
                                   ('other', 'Other')
                               ],
                               validators=[DataRequired()])
    
    patient_id = StringField('Patient ID/MRN',
                            validators=[DataRequired()],
                            render_kw={'placeholder': 'Enter patient medical record number'})
    
    notes = TextAreaField('Additional Notes',
                         render_kw={'placeholder': 'Optional notes about this document', 'rows': 3})
    
    submit = SubmitField('Upload & Process')


class SearchPatientForm(FlaskForm):
    """Form for searching patients"""
    search_query = StringField('Search',
                               validators=[DataRequired()],
                               render_kw={'placeholder': 'Search by name, MRN, or email'})
    
    submit = SubmitField('Search')


class InsuranceQuoteForm(FlaskForm):
    """Comprehensive form for insurance quote request (Chadwick Ng feature)"""
    
    # ===== Document Upload (NEW - AI Medical Integration) =====
    medical_document = FileField('Upload Medical Document (Optional)',
                                validators=[FileAllowed(['pdf', 'txt'], 'PDF or TXT files only')],
                                render_kw={'accept': '.pdf,.txt'})
    
    # ===== Health Data Section =====
    current_conditions = TextAreaField('Current Health Conditions',
                                      render_kw={'placeholder': 'List any current medical conditions (e.g., diabetes, hypertension)', 'rows': 3})
    
    current_medications = TextAreaField('Current Medications',
                                       render_kw={'placeholder': 'List medications you are currently taking', 'rows': 3})
    
    bmi = FloatField('BMI (Body Mass Index)',
                    validators=[Optional(), NumberRange(min=10, max=60)],
                    render_kw={'placeholder': 'e.g., 24.5'})
    
    blood_pressure = StringField('Blood Pressure',
                                render_kw={'placeholder': 'e.g., 120/80'})
    
    cholesterol = StringField('Cholesterol Level',
                             render_kw={'placeholder': 'e.g., 180 mg/dL'})
    
    glucose = StringField('Blood Glucose',
                         render_kw={'placeholder': 'e.g., 95 mg/dL'})
    
    smoking_status = SelectField('Smoking Status',
                                choices=[
                                    ('never', 'Never Smoked'),
                                    ('former', 'Former Smoker'),
                                    ('smoker', 'Current Smoker')
                                ],
                                validators=[DataRequired()])
    
    alcohol_consumption = SelectField('Alcohol Consumption',
                                     choices=[
                                         ('none', 'None'),
                                         ('occasional', 'Occasional (1-2 drinks/week)'),
                                         ('moderate', 'Moderate (3-7 drinks/week)'),
                                         ('heavy', 'Heavy (8+ drinks/week)')
                                     ],
                                     validators=[DataRequired()])
    
    # ===== Medical History Section =====
    past_conditions = TextAreaField('Past Medical Conditions',
                                   render_kw={'placeholder': 'List any previous medical conditions', 'rows': 2})
    
    surgeries = TextAreaField('Past Surgeries',
                             render_kw={'placeholder': 'List any surgeries you have had', 'rows': 2})
    
    hospitalizations = TextAreaField('Past Hospitalizations',
                                    render_kw={'placeholder': 'List any hospital stays', 'rows': 2})
    
    family_history = TextAreaField('Family Medical History',
                                  render_kw={'placeholder': 'Significant family medical conditions (e.g., heart disease, cancer)', 'rows': 2})
    
    # ===== Income & Employment Section =====
    annual_income = IntegerField('Annual Income ($)',
                                validators=[DataRequired(), NumberRange(min=0)],
                                render_kw={'placeholder': 'e.g., 50000'})
    
    employment_status = SelectField('Employment Status',
                                   choices=[
                                       ('full-time', 'Full-Time Employment'),
                                       ('part-time', 'Part-Time Employment'),
                                       ('self-employed', 'Self-Employed'),
                                       ('unemployed', 'Unemployed'),
                                       ('retired', 'Retired'),
                                       ('student', 'Student')
                                   ],
                                   validators=[DataRequired()])
    
    occupation = StringField('Occupation',
                            render_kw={'placeholder': 'e.g., Software Engineer, Teacher'})
    
    dependents = IntegerField('Number of Dependents',
                             validators=[Optional(), NumberRange(min=0, max=20)],
                             default=0,
                             render_kw={'placeholder': '0'})
    
    # ===== Consent Section =====
    consent_data_use = BooleanField('I consent to the use of my health data for insurance quote generation',
                                   validators=[DataRequired()])
    
    consent_privacy = BooleanField('I have read and agree to the Privacy Policy',
                                  validators=[DataRequired()])
    
    submit = SubmitField('Generate Insurance Quotes')

