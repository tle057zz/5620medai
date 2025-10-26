"""
Flask-WTF Forms for Clinical AI System
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError


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

