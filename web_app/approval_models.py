"""
UC-04: Review AI Output & Approve (Thanh Le)
Doctor approval workflow for AI-generated medical content

Models and logic for:
- Approval decisions with audit trail
- Safety flag validation
- Digital signatures
- Multi-physician reviews
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ApprovalStatus(Enum):
    """Status of approval decision"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    ESCALATED = "escalated"  # For multi-physician review


class SafetyLevel(Enum):
    """Safety flag severity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SafetyFlag:
    """Individual safety concern"""
    flag_id: str
    severity: SafetyLevel
    category: str  # e.g., "drug_interaction", "contraindication", "allergy"
    description: str
    ai_confidence: float
    requires_override: bool = False
    override_justification: Optional[str] = None
    override_by: Optional[str] = None
    override_at: Optional[datetime] = None


@dataclass
class ApprovalDecision:
    """Doctor's approval decision"""
    decision_id: str
    analysis_id: str  # Links to clinical_analysis_processor result
    reviewer_id: str
    reviewer_name: str
    status: ApprovalStatus
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Review details
    reviewed_fhir: bool = False
    reviewed_summary: bool = False
    reviewed_safety: bool = False
    
    # Decision details
    notes: str = ""
    modifications: List[Dict[str, str]] = field(default_factory=list)
    safety_overrides: List[str] = field(default_factory=list)  # List of flag_ids
    
    # Signature
    digital_signature: Optional[str] = None
    signature_timestamp: Optional[datetime] = None
    
    # Multi-physician review
    is_complex_case: bool = False
    requires_specialist: bool = False
    specialist_reviews: List[str] = field(default_factory=list)  # List of decision_ids
    
    # Patient release
    released_to_patient: bool = False
    release_timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'decision_id': self.decision_id,
            'analysis_id': self.analysis_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer_name,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'reviewed_fhir': self.reviewed_fhir,
            'reviewed_summary': self.reviewed_summary,
            'reviewed_safety': self.reviewed_safety,
            'notes': self.notes,
            'modifications': self.modifications,
            'safety_overrides': self.safety_overrides,
            'digital_signature': self.digital_signature,
            'signature_timestamp': self.signature_timestamp.isoformat() if self.signature_timestamp else None,
            'is_complex_case': self.is_complex_case,
            'requires_specialist': self.requires_specialist,
            'specialist_reviews': self.specialist_reviews,
            'released_to_patient': self.released_to_patient,
            'release_timestamp': self.release_timestamp.isoformat() if self.release_timestamp else None
        }


@dataclass
class AIOutputReview:
    """Complete review package for doctor"""
    analysis_id: str
    patient_id: str
    document_type: str
    processed_at: datetime
    
    # AI Outputs
    fhir_data: Dict[str, Any]
    summary_md: str
    risks_md: str
    safety_flags: List[SafetyFlag]
    
    # AI Confidence
    overall_confidence: float
    low_confidence_areas: List[str] = field(default_factory=list)
    
    # Current approval status
    approval_decision: Optional[ApprovalDecision] = None
    pending_reviews: List[str] = field(default_factory=list)  # For multi-physician
    
    # Validation checks
    has_critical_flags: bool = False
    requires_mandatory_override: bool = False
    

# In-memory storage (for development)
approval_decisions_storage: Dict[str, ApprovalDecision] = {}
pending_reviews_queue: List[str] = []  # analysis_ids awaiting review


def create_review_package(analysis_result) -> AIOutputReview:
    """
    Convert clinical analysis result to review package
    """
    from uuid import uuid4
    
    # Extract safety flags
    safety_flags = []
    if hasattr(analysis_result, 'red_flags') and analysis_result.red_flags:
        for flag in analysis_result.red_flags:
            severity = SafetyLevel.CRITICAL if 'critical' in flag.lower() else SafetyLevel.HIGH
            safety_flags.append(SafetyFlag(
                flag_id=str(uuid4()),
                severity=severity,
                category="safety_concern",
                description=flag,
                ai_confidence=0.85,
                requires_override=severity == SafetyLevel.CRITICAL
            ))
    
    # Assess if critical flags exist
    has_critical = any(f.severity == SafetyLevel.CRITICAL for f in safety_flags)
    requires_override = any(f.requires_override for f in safety_flags)
    
    review = AIOutputReview(
        analysis_id=analysis_result.analysis_id,
        patient_id=getattr(analysis_result, 'patient_id', 'unknown'),
        document_type=analysis_result.document_type,
        processed_at=analysis_result.timestamp,
        fhir_data=analysis_result.fhir_bundle or {},
        summary_md=analysis_result.explanation_text or "",
        risks_md='\n'.join(analysis_result.red_flags) if analysis_result.red_flags else "",
        safety_flags=safety_flags,
        overall_confidence=0.85,  # Could calculate from analysis
        has_critical_flags=has_critical,
        requires_mandatory_override=requires_override
    )
    
    # Add to pending queue if not yet reviewed
    if analysis_result.analysis_id not in pending_reviews_queue:
        pending_reviews_queue.append(analysis_result.analysis_id)
    
    return review


def save_approval_decision(decision: ApprovalDecision) -> str:
    """Save approval decision with audit trail"""
    approval_decisions_storage[decision.decision_id] = decision
    
    # Remove from pending queue if approved/rejected
    if decision.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]:
        if decision.analysis_id in pending_reviews_queue:
            pending_reviews_queue.remove(decision.analysis_id)
    
    # Log to audit trail (in production, save to database)
    print(f"✓ Approval decision saved: {decision.decision_id}")
    print(f"   Analysis: {decision.analysis_id}")
    print(f"   Status: {decision.status.value}")
    print(f"   Reviewer: {decision.reviewer_name}")
    
    return decision.decision_id


def get_approval_decision(decision_id: str) -> Optional[ApprovalDecision]:
    """Retrieve approval decision by ID"""
    return approval_decisions_storage.get(decision_id)


def get_pending_reviews() -> List[str]:
    """Get list of analysis IDs pending review"""
    return pending_reviews_queue.copy()


def validate_approval(review: AIOutputReview, decision: ApprovalDecision) -> tuple[bool, str]:
    """
    Validate approval decision against safety rules
    Returns (is_valid, error_message)
    """
    # Rule 1: Cannot approve with critical flags unless override provided
    if review.has_critical_flags:
        critical_flags = [f for f in review.safety_flags if f.severity == SafetyLevel.CRITICAL]
        for flag in critical_flags:
            if flag.flag_id not in decision.safety_overrides:
                return False, f"Critical safety flag '{flag.description}' requires override justification"
    
    # Rule 2: All checklist items must be reviewed
    if decision.status == ApprovalStatus.APPROVED:
        if not all([decision.reviewed_fhir, decision.reviewed_summary, decision.reviewed_safety]):
            return False, "All review sections (FHIR, Summary, Safety) must be checked before approval"
    
    # Rule 3: Digital signature required for approval
    if decision.status == ApprovalStatus.APPROVED:
        if not decision.digital_signature:
            return False, "Digital signature required for approval"
    
    # Rule 4: Complex cases require specialist review
    if review.overall_confidence < 0.7 or len(review.safety_flags) >= 3:
        if decision.status == ApprovalStatus.APPROVED and not decision.specialist_reviews:
            return False, "This case requires specialist review before approval"
    
    return True, ""


def generate_digital_signature(reviewer_id: str, decision: ApprovalDecision) -> str:
    """
    Generate digital signature for approval
    In production, use proper cryptographic signing
    """
    import hashlib
    from datetime import datetime
    
    signature_data = f"{reviewer_id}:{decision.decision_id}:{decision.analysis_id}:{datetime.now().isoformat()}"
    signature = hashlib.sha256(signature_data.encode()).hexdigest()
    
    return signature


def escalate_for_review(review: AIOutputReview, escalated_by: str, reason: str) -> ApprovalDecision:
    """
    Escalate case for multi-physician review
    """
    from uuid import uuid4
    
    decision = ApprovalDecision(
        decision_id=str(uuid4()),
        analysis_id=review.analysis_id,
        reviewer_id=escalated_by,
        reviewer_name="System Escalation",
        status=ApprovalStatus.ESCALATED,
        notes=f"Escalated for specialist review: {reason}",
        is_complex_case=True,
        requires_specialist=True
    )
    
    save_approval_decision(decision)
    return decision

