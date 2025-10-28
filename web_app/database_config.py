"""
Database Configuration for Clinical AI System
Supports both SQLite (development) and PostgreSQL (production)
"""

import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_database(app):
    """
    Initialize database with Flask app
    Automatically detects and uses appropriate database backend
    """
    # Check if PostgreSQL DATABASE_URL is set (production)
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # PostgreSQL (production/deployment)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print("✓ Using PostgreSQL database")
    else:
        # SQLite (development)
        db_path = os.path.join(os.path.dirname(__file__), 'clinical_ai.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        print(f"✓ Using SQLite database: {db_path}")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False  # Set to True for SQL debugging
    
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created/verified")
    
    return db


# =====================
# Database Models for UC-07 (Patient History)
# =====================

class MedicalRecord(db.Model):
    """
    Stores metadata about uploaded medical documents
    """
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    file_hash = db.Column(db.String(64), unique=True)
    patient_id = db.Column(db.String(50), nullable=False, index=True)
    document_type = db.Column(db.String(50))  # medical_report, lab_results, etc.
    pages = db.Column(db.Integer)
    size_mb = db.Column(db.Float)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Uploaded')  # Uploaded, Processed, Explained
    
    # Relationships
    fhir_bundle = db.relationship('FHIRBundle', back_populates='medical_record', uselist=False, cascade='all, delete-orphan')
    explanation = db.relationship('Explanation', back_populates='medical_record', uselist=False, cascade='all, delete-orphan')
    safety_flags = db.relationship('SafetyFlag', back_populates='medical_record', cascade='all, delete-orphan')
    processing_jobs = db.relationship('ProcessingJob', back_populates='medical_record', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_hash': self.file_hash,
            'patient_id': self.patient_id,
            'document_type': self.document_type,
            'pages': self.pages,
            'size_mb': self.size_mb,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'status': self.status
        }


class FHIRBundle(db.Model):
    """
    Stores FHIR R4 bundles generated from medical records
    """
    __tablename__ = 'fhir_bundles'
    
    id = db.Column(db.Integer, primary_key=True)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id', ondelete='CASCADE'), nullable=False)
    json_data = db.Column(db.Text, nullable=False)  # FHIR bundle as JSON string
    valid = db.Column(db.Boolean, nullable=False, default=False)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    medical_record = db.relationship('MedicalRecord', back_populates='fhir_bundle')
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'medical_record_id': self.medical_record_id,
            'fhir_bundle': json.loads(self.json_data) if self.json_data else None,
            'valid': self.valid,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }


class Explanation(db.Model):
    """
    Stores patient-friendly explanations of medical records
    """
    __tablename__ = 'explanations'
    
    id = db.Column(db.Integer, primary_key=True)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id', ondelete='CASCADE'), nullable=False)
    summary_md = db.Column(db.Text)  # Summary in markdown/text
    pathway_md = db.Column(db.Text)  # Treatment pathways
    risks_md = db.Column(db.Text)  # Risk assessment
    low_confidence = db.Column(db.Boolean, nullable=False, default=False)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    medical_record = db.relationship('MedicalRecord', back_populates='explanation')
    safety_flags = db.relationship('SafetyFlag', back_populates='explanation', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_id': self.medical_record_id,
            'summary': self.summary_md,
            'pathways': self.pathway_md,
            'risks': self.risks_md,
            'low_confidence': self.low_confidence,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }


class SafetyFlag(db.Model):
    """
    Stores safety alerts and red flags from medical records
    """
    __tablename__ = 'safety_flags'
    
    id = db.Column(db.Integer, primary_key=True)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id', ondelete='CASCADE'))
    explanation_id = db.Column(db.Integer, db.ForeignKey('explanations.id', ondelete='CASCADE'))
    flag_type = db.Column(db.String(50), nullable=False)  # Contraindication, Emergency, Allergy, Interaction
    severity = db.Column(db.String(20), nullable=False)  # Low, Medium, High, Critical
    details = db.Column(db.Text)
    evidence = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    medical_record = db.relationship('MedicalRecord', back_populates='safety_flags')
    explanation = db.relationship('Explanation', back_populates='safety_flags')
    
    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_id': self.medical_record_id,
            'explanation_id': self.explanation_id,
            'type': self.flag_type,
            'severity': self.severity,
            'details': self.details,
            'evidence': self.evidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ProcessingJob(db.Model):
    """
    Tracks AI processing jobs for medical records
    """
    __tablename__ = 'processing_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id', ondelete='CASCADE'))
    job_kind = db.Column(db.String(20), nullable=False)  # OCR, NER, EXPLAIN, SAFETY
    status = db.Column(db.String(20), nullable=False, default='Queued')  # Queued, Running, Succeeded, Failed
    latency_ms = db.Column(db.Integer)
    error_code = db.Column(db.String(50))
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    pipeline_version = db.Column(db.String(20))
    
    # Relationships
    medical_record = db.relationship('MedicalRecord', back_populates='processing_jobs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'medical_record_id': self.medical_record_id,
            'kind': self.job_kind,
            'status': self.status,
            'latency_ms': self.latency_ms,
            'error_code': self.error_code,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'pipeline_version': self.pipeline_version
        }


class AuditLog(db.Model):
    """
    Audit trail for all system actions
    """
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    actor_user_id = db.Column(db.String(50))
    action = db.Column(db.String(100), nullable=False)  # Upload, Process, View, Export, etc.
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    object_type = db.Column(db.String(50), nullable=False)  # MedicalRecord, FHIRBundle, etc.
    object_id = db.Column(db.String(50), nullable=False)
    details_hash = db.Column(db.String(64))
    pipeline_version = db.Column(db.String(20))
    
    def to_dict(self):
        return {
            'id': self.id,
            'actor': self.actor_user_id,
            'action': self.action,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'object_type': self.object_type,
            'object_id': self.object_id
        }


# =====================
# Helper Functions
# =====================

def log_action(user_id, action, object_type, object_id, details=None):
    """
    Create an audit log entry
    """
    log = AuditLog(
        actor_user_id=user_id,
        action=action,
        object_type=object_type,
        object_id=str(object_id),
        details_hash=details
    )
    db.session.add(log)
    db.session.commit()
    return log


def get_patient_medical_records(patient_id, limit=50):
    """
    Get all medical records for a patient, ordered by date
    """
    return MedicalRecord.query.filter_by(patient_id=patient_id)\
        .order_by(MedicalRecord.uploaded_at.desc())\
        .limit(limit)\
        .all()


def get_patient_fhir_bundles(patient_id):
    """
    Get all FHIR bundles for a patient through their medical records
    """
    records = get_patient_medical_records(patient_id)
    bundles = []
    for record in records:
        if record.fhir_bundle and record.fhir_bundle.valid:
            bundles.append(record.fhir_bundle)
    return bundles


def get_patient_safety_flags(patient_id, severity=None):
    """
    Get all safety flags for a patient
    """
    records = get_patient_medical_records(patient_id)
    record_ids = [r.id for r in records]
    
    query = SafetyFlag.query.filter(SafetyFlag.medical_record_id.in_(record_ids))
    
    if severity:
        query = query.filter_by(severity=severity)
    
    return query.order_by(SafetyFlag.created_at.desc()).all()

