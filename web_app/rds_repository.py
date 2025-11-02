import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor


def _conn():
    url = os.environ.get("DATABASE_URL")
    if url:
        return psycopg2.connect(url)
    host = os.environ.get("DB_HOST", "elec5620-as02-database.c38ki6o4abha.ap-southeast-2.rds.amazonaws.com")
    port = int(os.environ.get("DB_PORT", "5432"))
    db = os.environ.get("DB_NAME", "postgres")
    user = os.environ.get("DB_USER", "postgres")
    pwd = os.environ.get("DB_PASSWORD", "ghR4BwyqbEM1xhmrCKbM")
    return psycopg2.connect(host=host, port=port, dbname=db, user=user, password=pwd)


def get_patient_dashboard(user_id: int) -> Dict[str, Any]:
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT u.id, u.username, u.email, u.name, p.assigned_doctor_id
            FROM users u JOIN patients p ON p.user_id = u.id
            WHERE u.id = %s
            """,
            (user_id,),
        )
        profile = cur.fetchone() or {}

        cur.execute(
            "SELECT * FROM health_data WHERE patient_id=%s ORDER BY measure_date DESC LIMIT 5",
            (user_id,),
        )
        health = cur.fetchall()

        # Get most recent medical history for backward compatibility
        cur.execute(
            "SELECT * FROM medical_histories WHERE patient_id=%s ORDER BY last_updated DESC LIMIT 1",
            (user_id,),
        )
        history = cur.fetchone()
        
        # Get ALL medical history records to track when each medication/condition was first recorded
        cur.execute(
            "SELECT id, medication, past_illness, last_updated FROM medical_histories WHERE patient_id=%s ORDER BY last_updated ASC",
            (user_id,),
        )
        all_history_records = cur.fetchall()

        cur.execute(
            "SELECT * FROM income_details WHERE patient_id=%s ORDER BY effective_date DESC LIMIT 1",
            (user_id,),
        )
        income = cur.fetchone()

        cur.execute(
            "SELECT * FROM quotes WHERE patient_id=%s ORDER BY created_at DESC LIMIT 10",
            (user_id,),
        )
        quotes = cur.fetchall()

        cur.execute(
            "SELECT * FROM policy_holds WHERE patient_id=%s ORDER BY start_date DESC LIMIT 10",
            (user_id,),
        )
        policies = cur.fetchall()

        cur.execute(
            "SELECT * FROM appointments WHERE patient_id=%s ORDER BY appointment_at DESC LIMIT 10",
            (user_id,),
        )
        appts = cur.fetchall()

        # Get last visit date (from appointments or medical records)
        # Use the most recent date from either completed appointments or uploaded medical records
        cur.execute(
            """
            WITH appointment_dates AS (
                SELECT MAX(appointment_at) AS max_date FROM appointments 
                WHERE patient_id=%s AND status='Completed'
            ),
            record_dates AS (
                SELECT MAX(uploaded_at) AS max_date FROM medical_records 
                WHERE patient_id=%s
            )
            SELECT 
                CASE 
                    WHEN (SELECT max_date FROM appointment_dates) IS NULL 
                         AND (SELECT max_date FROM record_dates) IS NULL
                    THEN NULL
                    WHEN (SELECT max_date FROM appointment_dates) IS NULL
                    THEN (SELECT max_date FROM record_dates)
                    WHEN (SELECT max_date FROM record_dates) IS NULL
                    THEN (SELECT max_date FROM appointment_dates)
                    ELSE GREATEST(
                        (SELECT max_date FROM appointment_dates),
                        (SELECT max_date FROM record_dates)
                    )
                END AS last_visit
            """,
            (user_id, user_id),
        )
        last_visit_row = cur.fetchone()
        last_visit = last_visit_row.get('last_visit') if last_visit_row and last_visit_row.get('last_visit') else None

        # Get counts for dashboard stats
        # Medical Reports count
        cur.execute("SELECT COUNT(*) AS count FROM medical_records WHERE patient_id=%s", (user_id,))
        medical_reports_row = cur.fetchone()
        medical_reports_count = medical_reports_row.get('count', 0) if medical_reports_row else 0

        # Parse medications from ALL medical history records with timestamps
        medications_dict = {}  # key: lowercase name, value: {'name': original_name, 'recorded_at': datetime}
        if all_history_records:
            for record in all_history_records:
                med_str = record.get('medication', '') or ''
                recorded_at = record.get('last_updated')
                if med_str:
                    for m in med_str.split(','):
                        m = m.strip()
                        if m:
                            m_lower = m.lower()
                            # If we haven't seen this medication, or this record is older (first appearance)
                            if m_lower not in medications_dict:
                                medications_dict[m_lower] = {
                                    'name': m,  # Keep original case
                                    'recorded_at': recorded_at
                                }
        
        medications_list = [med for med in medications_dict.values()]
        active_medications_count = len(medications_list)
        
        # Parse health conditions from ALL medical history records with timestamps
        conditions_dict = {}  # key: lowercase name, value: {'name': original_name, 'recorded_at': datetime}
        if all_history_records:
            for record in all_history_records:
                conditions_str = record.get('past_illness', '') or ''
                recorded_at = record.get('last_updated')
                if conditions_str:
                    for c in conditions_str.split(','):
                        c = c.strip()
                        if c:
                            c_lower = c.lower()
                            # If we haven't seen this condition, or this record is older (first appearance)
                            if c_lower not in conditions_dict:
                                conditions_dict[c_lower] = {
                                    'name': c,  # Keep original case
                                    'recorded_at': recorded_at
                                }
        
        conditions_list = [cond for cond in conditions_dict.values()]

        # Upcoming Appointments count (future appointments that are not cancelled/completed)
        cur.execute(
            """
            SELECT COUNT(*) AS count FROM appointments 
            WHERE patient_id=%s 
            AND appointment_at > NOW() 
            AND status NOT IN ('Cancelled', 'Completed')
            """,
            (user_id,),
        )
        upcoming_appointments_row = cur.fetchone()
        upcoming_appointments_count = upcoming_appointments_row.get('count', 0) if upcoming_appointments_row else 0

        # Insurance Quotes count
        cur.execute("SELECT COUNT(*) AS count FROM quotes WHERE patient_id=%s", (user_id,))
        insurance_quotes_row = cur.fetchone()
        insurance_quotes_count = insurance_quotes_row.get('count', 0) if insurance_quotes_row else 0

        return {
            "profile": profile,
            "health_data": health,
            "medical_history": history,
            "income_details": income,
            "quotes": quotes,
            "policies": policies,
            "appointments": appts,
            "last_visit": last_visit,
            "medications": medications_list,  # Parsed list of medications
            "conditions": conditions_list,     # Parsed list of health conditions
            "stats": {
                "medical_reports": medical_reports_count,
                "active_medications": active_medications_count,
                "upcoming_appointments": upcoming_appointments_count,
                "insurance_quotes": insurance_quotes_count,
            },
        }


def get_doctor_dashboard(user_id: int) -> Dict[str, Any]:
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT u.id, u.username, u.email, u.name, d.specialization, d.license_number
            FROM users u JOIN doctors d ON d.user_id = u.id
            WHERE u.id = %s
            """,
            (user_id,),
        )
        profile = cur.fetchone() or {}

        cur.execute(
            "SELECT * FROM appointments WHERE doctor_id=%s ORDER BY appointment_at DESC LIMIT 20",
            (user_id,),
        )
        appts = cur.fetchall()

        cur.execute(
            """
            SELECT p.user_id AS patient_id, u.name, MAX(a.appointment_at) AS last_visit
            FROM patients p
            JOIN users u ON u.id = p.user_id
            LEFT JOIN appointments a ON a.patient_id = p.user_id AND a.doctor_id = %s
            WHERE p.assigned_doctor_id = %s
            GROUP BY p.user_id, u.name
            ORDER BY last_visit DESC NULLS LAST
            LIMIT 50
            """,
            (user_id, user_id),
        )
        assigned = cur.fetchall()

        return {"profile": profile, "appointments": appts, "assigned_patients": assigned}


def get_admin_overview() -> Dict[str, Any]:
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        def count(table: str) -> int:
            cur.execute(f"SELECT COUNT(*) AS c FROM {table}")
            return int(cur.fetchone()["c"])  # type: ignore[index]

        tables = [
            "users",
            "patients",
            "doctors",
            "quotes",
            "policy_holds",
            "appointments",
            "health_data",
            "medical_histories",
            "income_details",
            "medical_records",
            "fhir_bundles",
            "explanations",
            "safety_flags",
            "processing_jobs",
            "ai_approvals",
        ]
        counts = {t: count(t) for t in tables}

        cur.execute(
            "SELECT id, username, email, name FROM users ORDER BY id DESC LIMIT 25"
        )
        latest_users = cur.fetchall()
        return {"counts": counts, "latest_users": latest_users}


def list_users_admin() -> List[Dict[str, Any]]:
    """Return all users with inferred role and status for admin UI."""
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT u.id, u.username, u.email, u.name, u.status,
                   (CASE WHEN d.user_id IS NOT NULL THEN 'Doctor'
                         WHEN p.user_id IS NOT NULL THEN 'Patient'
                         ELSE 'User' END) AS role
            FROM users u
            LEFT JOIN doctors d ON d.user_id = u.id
            LEFT JOIN patients p ON p.user_id = u.id
            ORDER BY u.id ASC
            """
        )
        return [dict(r) for r in cur.fetchall()]



def get_quote_history_for_patient(user_id: int) -> List[Dict[str, Any]]:
    """Return summary rows for a patient's quote history from RDS.

    Fields per row:
      - rds_request_id (int) : quote_requests.id
      - display_request_id (str) : parsed from user_input if present (e.g., 'REQ-...')
      - submitted (timestamp)
      - status (text)
      - quotes_found (int) : count of recommendations for that request
      - income (numeric) : latest income value for patient
      - conditions_count (int) : parsed count from latest medical_histories.past_illness
    """
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Quote request rows with counts of recommendations and per-request income/history
        cur.execute(
            """
            SELECT qr.id AS rds_request_id,
                   qr.user_input,
                   qr.request_time AS submitted,
                   qr.processing_status AS status,
                   COALESCE(cnt.c, 0) AS quotes_found,
                   inc.annual_income AS income,
                   mh.past_illness AS past_illness
            FROM quote_requests qr
            LEFT JOIN income_details inc ON inc.id = qr.income_detail_id
            LEFT JOIN medical_histories mh ON mh.id = qr.medical_history_id
            LEFT JOIN (
              SELECT quote_request_id, COUNT(DISTINCT quote_id) AS c
              FROM quote_recommendations
              GROUP BY quote_request_id
            ) cnt ON cnt.quote_request_id = qr.id
            WHERE qr.patient_id = %s
            ORDER BY qr.request_time DESC
            LIMIT 100
            """,
            (user_id,),
        )
        rows = cur.fetchall()
        results: List[Dict[str, Any]] = []
        for r in rows:
            display = f"DB-{r['rds_request_id']}"
            ui = r.get("user_input") or ""
            if "REQ-" in ui:
                # try to extract the REQ id substring
                import re
                m = re.search(r"REQ-[0-9]+", ui)
                if m:
                    display = m.group(0)
            # per-request income and conditions
            income_val = float(r["income"]) if r.get("income") is not None else None
            cond_count = 0
            if r.get("past_illness"):
                parts = [p.strip() for p in str(r["past_illness"]).replace(";", ",").split(",") if p.strip()]
                cond_count = len(parts)
            results.append(
                {
                    "rds_request_id": int(r["rds_request_id"]),
                    "display_request_id": display,
                    "submitted": r["submitted"],
                    "status": r["status"],
                    "quotes_found": int(r["quotes_found"]),
                    "income": income_val,
                    "conditions_count": cond_count,
                }
            )
        return results


def get_quote_request_full_for_token(user_id: int, req_token: str) -> Dict[str, Any] | None:
    """Fetch a full quote request package from RDS by REQ token contained in user_input.

    Returns dict with keys:
      - request: { id, request_time, status, display_request_id, income, conditions }
      - quotes: [ { suitability_score, cost_score, coverage_score, overall_score, rationale,
                   product: { name, provider, plan_type, monthly_premium, coverage_amount,
                              annual_deductible, max_out_of_pocket, coverage_details, exclusions } } ]
    """
    pattern = f"%{req_token}%"
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT qr.id, qr.request_time, qr.processing_status,
                   inc.annual_income AS income,
                   mh.past_illness AS past_illness
            FROM quote_requests qr
            LEFT JOIN income_details inc ON inc.id = qr.income_detail_id
            LEFT JOIN medical_histories mh ON mh.id = qr.medical_history_id
            WHERE qr.patient_id=%s AND qr.user_input ILIKE %s
            ORDER BY qr.id DESC
            LIMIT 1
            """,
            (user_id, pattern),
        )
        req_row = cur.fetchone()
        if not req_row:
            return None
        req_id = int(req_row["id"])  # database internal id
        income_val = float(req_row["income"]) if req_row.get("income") is not None else None
        conditions_list: List[str] = []
        if req_row.get("past_illness"):
            txt = str(req_row["past_illness"]).replace(";", ",")
            conditions_list = [p.strip() for p in txt.split(",") if p.strip()]

        # Quotes + products for this request
        cur.execute(
            """
            SELECT q.id AS quote_id,
                   q.suitability_score, q.cost_score, q.coverage_score, q.overall_score, q.rationale,
                   ip.name AS p_name, ip.provider AS p_provider, ip.plan_type AS p_plan_type,
                   ip.monthly_premium AS p_monthly_premium, ip.coverage_amount AS p_coverage_amount,
                   ip.annual_deductible AS p_annual_deductible, ip.max_out_of_pocket AS p_max_oop,
                   ip.coverage_details AS p_coverage_details, ip.exclusions AS p_exclusions,
                   ip.product_link AS p_product_link
            FROM quote_recommendations r
            JOIN quotes q ON q.id = r.quote_id
            JOIN insurance_products ip ON ip.id = q.insurance_product_id
            WHERE r.quote_request_id = %s
            ORDER BY r.rank ASC NULLS LAST, q.id ASC
            """,
            (req_id,),
        )
        rows = cur.fetchall()
        quotes: List[Dict[str, Any]] = []
        for r in rows:
            quote_id_val = int(r["quote_id"]) if r.get("quote_id") is not None else None
            product = {
                "name": r["p_name"],
                "provider": r["p_provider"],
                "plan_type": r["p_plan_type"],
                "monthly_premium": float(r["p_monthly_premium"]) if r.get("p_monthly_premium") is not None else None,
                "coverage_amount": float(r["p_coverage_amount"]) if r.get("p_coverage_amount") is not None else None,
                "annual_deductible": float(r["p_annual_deductible"]) if r.get("p_annual_deductible") is not None else None,
                "max_out_of_pocket": float(r["p_max_oop"]) if r.get("p_max_oop") is not None else None,
                "coverage_details": r.get("p_coverage_details") or [],
                "exclusions": r.get("p_exclusions") or [],
                "product_link": r.get("p_product_link") or None,
                "quote_id": quote_id_val,  # Store quote_id for matching
            }
            quotes.append(
                {
                    "suitability_score": int(r["suitability_score"]) if r.get("suitability_score") is not None else 0,
                    "cost_score": int(r["cost_score"]) if r.get("cost_score") is not None else None,
                    "coverage_score": int(r["coverage_score"]) if r.get("coverage_score") is not None else None,
                    "overall_score": int(r["overall_score"]) if r.get("overall_score") is not None else None,
                    "rationale": r.get("rationale") or '',
                    "product": product,
                    "quote_id": quote_id_val,  # Also store at quote level for convenience
                }
            )

        package = {
            "request": {
                "rds_id": req_id,
                "display_request_id": req_token,
                "request_time": req_row["request_time"],
                "status": req_row["processing_status"],
                "income": income_val,
                "conditions": conditions_list,
            },
            "quotes": quotes,
        }
        return package


def create_user(username: str, email: str, password_hash: str, name: str, role: str,
                specialization: str = None, ahpra_number: str = None, qualification: str = None,
                clinic_address: str = None) -> Dict[str, Any]:
    """Create a new user account in RDS.
    
    Returns dict with 'success', 'user_id', and 'message' keys.
    For doctors, approval_status is set to 'Pending'.
    """
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        try:
            conn.autocommit = False
            # Check if username or email already exists
            cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            existing = cur.fetchone()
            if existing:
                return {
                    "success": False,
                    "user_id": None,
                    "message": "Username or email already exists"
                }
            
            # Create user record
            print(f"[CREATE_USER] Creating user: username={username}, email={email}, hash_prefix={password_hash[:30] if password_hash else 'N/A'}")
            cur.execute(
                """
                INSERT INTO users(name, email, password_hash, username, gender)
                VALUES (%s, %s, %s, %s, 'PreferNot')
                RETURNING id
                """,
                (name, email, password_hash, username),
            )
            user_id = cur.fetchone()["id"]
            print(f"[CREATE_USER] User created with id={user_id}")
            
            # Create role-specific record
            if role == "doctor":
                approval_status = "Pending"  # Doctors need admin approval
                cur.execute(
                    """
                    INSERT INTO doctors(user_id, specialization, license_number, ahpra_number, 
                                      qualification, clinic_address, approval_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (user_id, specialization, None, ahpra_number, qualification, clinic_address, approval_status),
                )
            elif role == "patient":
                cur.execute(
                    "INSERT INTO patients(user_id, consent_on_ai) VALUES (%s, FALSE)",
                    (user_id,),
                )
            
            conn.commit()
            return {
                "success": True,
                "user_id": user_id,
                "message": f"Account created successfully. {'Your account is pending admin approval.' if role == 'doctor' else 'You can now log in.'}"
            }
        except Exception as e:
            conn.rollback()
            return {
                "success": False,
                "user_id": None,
                "message": f"Error creating account: {str(e)}"
            }


def get_pending_doctors() -> List[Dict[str, Any]]:
    """Get all doctors pending approval"""
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT u.id, u.username, u.email, u.name, u.created_at,
                   d.specialization, d.ahpra_number, d.qualification, d.clinic_address,
                   d.approval_status, d.created_at AS doctor_created_at
            FROM users u
            JOIN doctors d ON d.user_id = u.id
            WHERE d.approval_status = 'Pending'
            ORDER BY d.created_at ASC
            """,
        )
        return cur.fetchall() or []


def update_doctor_approval(doctor_user_id: int, admin_user_id: int = None, 
                          approval_status: str = 'Approved', approval_notes: str = None) -> bool:
    """Update doctor approval status.
    
    approval_status should be 'Approved' or 'Rejected'
    """
    with _conn() as conn, conn.cursor() as cur:
        try:
            conn.autocommit = False
            # First check if doctor exists
            cur.execute("SELECT user_id FROM doctors WHERE user_id = %s", (doctor_user_id,))
            if not cur.fetchone():
                print(f"[UPDATE_DOCTOR_APPROVAL] Doctor with user_id={doctor_user_id} not found")
                conn.rollback()
                return False
            
            print(f"[UPDATE_DOCTOR_APPROVAL] Updating doctor user_id={doctor_user_id}, status={approval_status}, admin_id={admin_user_id}")
            # approved_by can be NULL if admin is a demo account without DB record
            cur.execute(
                """
                UPDATE doctors
                SET approval_status = %s,
                    approval_notes = %s,
                    approved_by = %s,
                    approved_at = NOW()
                WHERE user_id = %s
                """,
                (approval_status, approval_notes, admin_user_id, doctor_user_id),
            )
            rows_updated = cur.rowcount
            print(f"[UPDATE_DOCTOR_APPROVAL] Rows updated: {rows_updated}")
            conn.commit()
            
            if rows_updated == 0:
                print(f"[UPDATE_DOCTOR_APPROVAL] Warning: No rows updated for user_id={doctor_user_id}")
                return False
            return True
        except Exception as e:
            import traceback
            print(f"[UPDATE_DOCTOR_APPROVAL] Exception: {e}")
            print(traceback.format_exc())
            conn.rollback()
            return False


def get_doctor_approval_status(user_id: int) -> str:
    """Get doctor approval status for a user_id. Returns None if not a doctor."""
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT approval_status FROM doctors WHERE user_id = %s",
            (user_id,),
        )
        row = cur.fetchone()
        return row.get("approval_status") if row else None


def get_patient_recent_medical_records(patient_user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent medical records for a patient.
    Returns list of records with id, uploaded_at, status, document_type (from DB or inferred from FHIR/pipeline), and doctor info.
    """
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get medical records with document_type from DB, status, and upload date
        # Try to extract document type from FHIR bundles if not in DB
        cur.execute("""
            SELECT 
                mr.id,
                mr.file_hash,
                mr.patient_id,
                mr.uploaded_at,
                mr.status,
                mr.size_mb,
                mr.pages,
                mr.document_type AS db_document_type,
                -- Try to extract document type from FHIR bundle JSON
                (SELECT 
                    COALESCE(
                        fb.json::jsonb->'entry'->0->'resource'->'type'->'coding'->0->>'display',
                        fb.json::jsonb->'entry'->0->'resource'->'type'->'coding'->0->>'code',
                        fb.json::jsonb->'type'->>'code',
                        NULL
                    )
                 FROM fhir_bundles fb 
                 WHERE fb.medical_record_id = mr.id 
                 LIMIT 1) AS fhir_doc_type,
                -- Try to get associated doctor from appointments
                (SELECT u.name 
                 FROM appointments a
                 JOIN users u ON u.id = a.doctor_id
                 WHERE a.patient_id = mr.patient_id 
                 AND a.status = 'Completed'
                 ORDER BY a.appointment_at DESC
                 LIMIT 1) AS doctor_name
            FROM medical_records mr
            WHERE mr.patient_id = %s
            ORDER BY mr.uploaded_at DESC
            LIMIT %s
        """, (patient_user_id, limit))
        
        records = cur.fetchall()
        
        # Map records to a more useful format
        result = []
        for record in records:
            # Determine document type: Use DB value, then FHIR, then infer
            doc_type = None
            doc_icon = "bi-file-earmark-text"  # Default icon
            
            # Priority 1: Use document_type from database if available
            if record.get('db_document_type'):
                doc_type_raw = record['db_document_type']
                # Map database values to display names
                doc_type_map = {
                    'medical_report': 'Medical Report',
                    'lab_results': 'Lab Results',
                    'prescription': 'Prescription',
                    'discharge_summary': 'Discharge Summary',
                    'imaging_report': 'Imaging Report',
                    'pathology': 'Pathology Report',
                    'consultation': 'Consultation Notes',
                    'other': 'Medical Document'
                }
                doc_type = doc_type_map.get(doc_type_raw, doc_type_raw.replace('_', ' ').title())
            
            # Priority 2: Try to extract from FHIR bundle
            if not doc_type:
                fhir_type = record.get('fhir_doc_type')
                if fhir_type:
                    # Map FHIR document type codes to display names
                    fhir_type_lower = fhir_type.lower()
                    if 'lab' in fhir_type_lower or 'laboratory' in fhir_type_lower:
                        doc_type = "Lab Results"
                    elif 'imaging' in fhir_type_lower or 'radiology' in fhir_type_lower:
                        doc_type = "Imaging Report"
                    elif 'pathology' in fhir_type_lower:
                        doc_type = "Pathology Report"
                    elif 'discharge' in fhir_type_lower:
                        doc_type = "Discharge Summary"
                    elif 'consultation' in fhir_type_lower or 'consult' in fhir_type_lower:
                        doc_type = "Consultation Notes"
                    elif 'prescription' in fhir_type_lower or 'prescribe' in fhir_type_lower:
                        doc_type = "Prescription"
                    else:
                        doc_type = fhir_type  # Use as-is
            
            # Priority 3: Infer from file characteristics
            if not doc_type:
                if record.get('size_mb') and record['size_mb'] > 2:
                    doc_type = "Imaging Report"
                    doc_icon = "bi-camera"
                elif record.get('pages') and record['pages'] > 5:
                    doc_type = "Medical Report"
                    doc_icon = "bi-file-earmark-text"
                else:
                    doc_type = "Lab Results"
                    doc_icon = "bi-heart-pulse"
            
            # Priority 4: Default to "Not Sure"
            if not doc_type:
                doc_type = "Not Sure"
            
            # Set icon based on document type
            if doc_type == "Lab Results":
                doc_icon = "bi-heart-pulse"
            elif doc_type == "Imaging Report":
                doc_icon = "bi-camera"
            elif doc_type == "Pathology Report":
                doc_icon = "bi-microscope"
            elif doc_type == "Prescription":
                doc_icon = "bi-prescription"
            elif doc_type == "Discharge Summary":
                doc_icon = "bi-file-earmark-medical"
            elif doc_type == "Consultation Notes":
                doc_icon = "bi-chat-left-text"
            else:
                doc_icon = "bi-file-earmark-text"
            
            result.append({
                'id': record['id'],
                'date': record['uploaded_at'],
                'document_type': doc_type,
                'document_icon': doc_icon,
                'doctor': record.get('doctor_name') or 'Not Sure',
                'status': record['status'],
                'file_hash': record.get('file_hash'),
                'size_mb': record.get('size_mb'),
                'pages': record.get('pages')
            })
        
        return result


def save_medical_record_to_rds(patient_user_id: int, file_hash: str, document_type: str = None,
                               pages: int = None, size_mb: float = None,
                               status: str = 'Uploaded', uploaded_at: datetime = None,
                               file_path: str = None, original_filename: str = None) -> Optional[int]:
    """Save a medical record to RDS.
    Ensures patient record exists before saving (required by foreign key constraint).
    Returns the medical_record_id if successful, None otherwise.
    """
    if uploaded_at is None:
        uploaded_at = datetime.now()
    
    with _conn() as conn, conn.cursor() as cur:
        try:
            conn.autocommit = False
            
            # Ensure patient record exists (required by foreign key constraint)
            # medical_records.patient_id REFERENCES patients(user_id)
            cur.execute("""
                INSERT INTO patients(user_id)
                VALUES (%s)
                ON CONFLICT (user_id) DO NOTHING
            """, (patient_user_id,))
            
            # Check if file_path column exists in medical_records
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'medical_records' AND column_name = 'file_path'
                ) AS has_file_path
            """)
            result = cur.fetchone()
            has_file_path_col = result[0] if result else False
            print(f"[RDS Save Debug] Checking columns: has_file_path_col={has_file_path_col}")
            
            if not has_file_path_col:
                print(f"[RDS Save Debug] ⚠️ WARNING: file_path column does not exist. Attempting to add columns...")
                try:
                    # Try to add the columns if they don't exist
                    cur.execute("ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS file_path TEXT")
                    cur.execute("ALTER TABLE medical_records ADD COLUMN IF NOT EXISTS original_filename TEXT")
                    conn.commit()
                    print(f"[RDS Save Debug] ✅ Successfully added file_path and original_filename columns")
                    has_file_path_col = True  # Update flag after adding columns
                except Exception as alter_error:
                    print(f"[RDS Save Debug] ❌ Failed to add columns: {alter_error}")
                    conn.rollback()
            
            # Build INSERT query based on whether columns exist
            if has_file_path_col:
                # Insert with file_path and original_filename columns
                cur.execute("""
                    INSERT INTO medical_records(file_hash, patient_id, document_type, pages, size_mb, 
                                              file_path, original_filename, uploaded_at, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::medical_record_status)
                    ON CONFLICT (file_hash) DO UPDATE SET
                        document_type = COALESCE(EXCLUDED.document_type, medical_records.document_type),
                        file_path = EXCLUDED.file_path,
                        original_filename = EXCLUDED.original_filename,
                        status = EXCLUDED.status,
                        uploaded_at = EXCLUDED.uploaded_at
                    RETURNING id
                """, (file_hash, patient_user_id, document_type, pages, size_mb, file_path, original_filename, uploaded_at, status))
            else:
                # Fallback: insert without file_path columns (for databases that haven't migrated yet)
                cur.execute("""
                    INSERT INTO medical_records(file_hash, patient_id, document_type, pages, size_mb, 
                                              uploaded_at, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::medical_record_status)
                    ON CONFLICT (file_hash) DO UPDATE SET
                        document_type = COALESCE(EXCLUDED.document_type, medical_records.document_type),
                        status = EXCLUDED.status,
                        uploaded_at = EXCLUDED.uploaded_at
                    RETURNING id
                """, (file_hash, patient_user_id, document_type, pages, size_mb, uploaded_at, status))
            
            result = cur.fetchone()
            record_id = result[0] if result else None
            conn.commit()
            
            if record_id:
                print(f"[RDS] Saved medical record: id={record_id}, patient={patient_user_id}, type={document_type}, status={status}")
                print(f"[RDS Save Debug] has_file_path_col={has_file_path_col}, file_path={file_path}, original_filename={original_filename}")
                if has_file_path_col:
                    # Verify the values were actually saved
                    cur.execute("""
                        SELECT file_path, original_filename 
                        FROM medical_records 
                        WHERE id = %s
                    """, (record_id,))
                    verify_row = cur.fetchone()
                    if verify_row:
                        print(f"[RDS Save Debug] Verified saved: file_path={verify_row[0]}, original_filename={verify_row[1]}")
            return record_id
        except Exception as e:
            conn.rollback()
            print(f"[RDS] Failed to save medical record: {e}")
            import traceback
            traceback.print_exc()
            return None


def get_admin_dashboard_stats() -> Dict[str, Any]:
    """Get real statistics for admin dashboard cards.
    Returns: dict with total_users, documents_processed, ai_pipeline_uptime, storage_used
    """
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        stats = {}
        
        # 1. Total Users
        cur.execute("SELECT COUNT(*) AS count FROM users")
        stats['total_users'] = int(cur.fetchone()["count"])
        
        # 2. Documents Processed (from medical_records where status is 'Processed')
        cur.execute("""
            SELECT COUNT(*) AS count 
            FROM medical_records 
            WHERE status IN ('Processed', 'Explained', 'Checked')
        """)
        stats['documents_processed'] = int(cur.fetchone()["count"])
        
        # 3. AI Pipeline Uptime (calculate success rate from processing_jobs)
        # Try last 30 days first (using started_at), then fallback to all time
        cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE status = 'Succeeded') AS succeeded,
                COUNT(*) FILTER (WHERE status = 'Failed') AS failed,
                COUNT(*) AS total
            FROM processing_jobs
            WHERE started_at >= NOW() - INTERVAL '30 days'
        """)
        job_stats = cur.fetchone()
        if job_stats and job_stats["total"] > 0:
            succeeded = int(job_stats["succeeded"] or 0)
            total = int(job_stats["total"])
            uptime_pct = round((succeeded / total) * 100, 1)
            stats['ai_pipeline_uptime'] = f"{uptime_pct}%"
        else:
            # If no jobs in last 30 days, check all time
            cur.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'Succeeded') AS succeeded,
                    COUNT(*) AS total
                FROM processing_jobs
            """)
            all_time_stats = cur.fetchone()
            if all_time_stats and all_time_stats["total"] > 0:
                succeeded = int(all_time_stats["succeeded"] or 0)
                total = int(all_time_stats["total"])
                uptime_pct = round((succeeded / total) * 100, 1)
                stats['ai_pipeline_uptime'] = f"{uptime_pct}%"
            else:
                stats['ai_pipeline_uptime'] = "100%"  # Default if no jobs
        
        # 4. Storage Used (estimate from database size)
        # PostgreSQL: pg_size_pretty + pg_database_size
        try:
            cur.execute("""
                SELECT pg_size_pretty(
                    (SELECT sum(pg_total_relation_size(schemaname||'.'||tablename))
                     FROM pg_tables
                     WHERE schemaname = 'public')
                ) AS db_size
            """)
            size_result = cur.fetchone()
            if size_result and size_result.get("db_size"):
                stats['storage_used'] = size_result["db_size"]
            else:
                stats['storage_used'] = "N/A"
        except Exception as e:
            print(f"[ADMIN_STATS] Could not calculate DB size: {e}")
            # Fallback: estimate from record counts
            cur.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM medical_records) * 50 AS estimated_bytes
            """)
            est_result = cur.fetchone()
            if est_result and est_result.get("estimated_bytes"):
                est_mb = round(int(est_result["estimated_bytes"]) / 1024 / 1024, 1)
                stats['storage_used'] = f"{est_mb}MB"
            else:
                stats['storage_used'] = "N/A"
        
        return stats


def get_patient_action_history(patient_user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Get combined action history for a patient (insurance quotes + medical analyses).
    Returns list of actions with: action_type, action_name, date_time, status
    """
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        history = []
        
        # 1. Fetch insurance quote requests
        cur.execute("""
            SELECT 
                qr.id AS request_id,
                qr.request_time AS action_date,
                qr.processing_status AS status,
                COUNT(DISTINCT qrec.id) AS quotes_count
            FROM quote_requests qr
            LEFT JOIN quote_recommendations qrec ON qrec.quote_request_id = qr.id
            WHERE qr.patient_id = %s
            GROUP BY qr.id, qr.request_time, qr.processing_status
            ORDER BY qr.request_time DESC
            LIMIT %s
        """, (patient_user_id, limit))
        
        quote_requests = cur.fetchall()
        for qr in quote_requests:
            quotes_count = qr.get('quotes_count', 0) or 0
            action_name = f"Request Insurance Quote"
            if quotes_count > 0:
                action_name += f" ({quotes_count} quote{'s' if quotes_count != 1 else ''} found)"
            
            status = qr.get('status', '').lower() if qr.get('status') else 'unknown'
            status_display = 'Completed' if status == 'completed' else 'In Progress' if status in ('processing', 'pending') else status.title()
            
            history.append({
                'action_type': 'insurance_quote',
                'action_name': action_name,
                'date_time': qr.get('action_date'),
                'status': status_display,
                'status_raw': status,
                'request_id': qr.get('request_id')
            })
        
        # 2. Fetch medical record analyses
        cur.execute("""
            SELECT 
                mr.id AS record_id,
                mr.uploaded_at AS action_date,
                mr.status,
                mr.document_type AS db_document_type
            FROM medical_records mr
            WHERE mr.patient_id = %s
            ORDER BY mr.uploaded_at DESC
            LIMIT %s
        """, (patient_user_id, limit))
        
        medical_records = cur.fetchall()
        for mr in medical_records:
            doc_type = mr.get('db_document_type', 'Medical Document')
            if doc_type:
                doc_type_map = {
                    'medical_report': 'Medical Report',
                    'lab_results': 'Lab Results',
                    'prescription': 'Prescription',
                    'discharge_summary': 'Discharge Summary',
                    'imaging_report': 'Imaging Report',
                    'pathology': 'Pathology Report',
                    'consultation': 'Consultation Notes',
                    'other': 'Medical Document'
                }
                doc_type = doc_type_map.get(doc_type, doc_type.replace('_', ' ').title())
            else:
                doc_type = 'Medical Document'
            
            action_name = f"Medical Analysis - {doc_type}"
            
            status = mr.get('status', '').lower() if mr.get('status') else 'unknown'
            status_display = 'Completed' if status in ('processed', 'explained', 'checked') else 'Uploaded' if status == 'uploaded' else status.title()
            
            history.append({
                'action_type': 'medical_analysis',
                'action_name': action_name,
                'date_time': mr.get('action_date'),
                'status': status_display,
                'status_raw': status,
                'record_id': mr.get('record_id')
            })
        
        # 3. Sort by date/time descending
        history.sort(key=lambda x: x.get('date_time') or datetime.min, reverse=True)
        
        # 4. Limit results
        return history[:limit]


def get_clinical_analysis_history_for_user(patient_user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Get clinical analysis history for a patient from RDS.
    Returns list of analysis summaries with analysis_id, patient_name, document_type, timestamp, etc.
    """
    try:
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
            SELECT 
                mr.id AS medical_record_id,
                mr.file_hash,
                mr.document_type,
                mr.uploaded_at AS timestamp,
                mr.status,
                -- Extract analysis_id: use file_hash if it starts with 'CA-', otherwise construct from timestamp
                CASE 
                    WHEN mr.file_hash LIKE 'CA-%%' THEN mr.file_hash
                    ELSE CONCAT('CA-', TO_CHAR(mr.uploaded_at, 'YYYYMMDD-HH24MISS'))
                END AS analysis_id,
                -- Get patient name from users table (mr.patient_id = users.id via patients table)
                COALESCE(u.name, u.username, 'Unknown Patient') AS patient_name,
                -- Review status information
                aa.id AS review_approval_id,
                aa.decision AS review_decision,
                aa.created_at AS review_requested_at,
                aa.signed_at AS review_completed_at,
                doc_user.name AS review_doctor_name,
                doc_user.id AS review_doctor_id,
                -- Count conditions from FHIR bundle
                (SELECT COUNT(*)::int
                 FROM fhir_bundles fb
                 WHERE fb.medical_record_id = mr.id
                 AND fb.json::text LIKE '%%"resourceType": "Condition"%%') AS conditions_count,
                -- Count medications from FHIR bundle
                (SELECT COUNT(*)::int
                 FROM fhir_bundles fb
                 WHERE fb.medical_record_id = mr.id
                 AND (fb.json::text LIKE '%%"resourceType": "MedicationStatement"%%'
                      OR fb.json::text LIKE '%%"resourceType": "MedicationRequest"%%')) AS medications_count,
                -- Get risk level from safety flags or explanations
                -- Note: safety_severity enum values are 'Low', 'Medium', 'High' (not 'Critical' or 'Moderate')
                CASE 
                    WHEN EXISTS (SELECT 1 FROM safety_flags sf WHERE sf.medical_record_id = mr.id AND sf.severity = 'High')
                    THEN 'high'
                    WHEN EXISTS (SELECT 1 FROM safety_flags sf WHERE sf.medical_record_id = mr.id AND sf.severity = 'Medium')
                    THEN 'medium'
                    WHEN EXISTS (SELECT 1 FROM safety_flags sf WHERE sf.medical_record_id = mr.id AND sf.severity = 'Low')
                    THEN 'low'
                    WHEN EXISTS (SELECT 1 FROM safety_flags sf WHERE sf.medical_record_id = mr.id)
                    THEN 'medium'
                    WHEN EXISTS (SELECT 1 FROM explanations e WHERE e.medical_record_id = mr.id AND e.low_confidence = false)
                    THEN 'low'
                    ELSE 'unknown'
                END AS risk_level,
                -- Count red flags
                (SELECT COUNT(*)::int FROM safety_flags sf WHERE sf.medical_record_id = mr.id) AS red_flags_count
            FROM medical_records mr
            LEFT JOIN patients p ON p.user_id = mr.patient_id
            LEFT JOIN users u ON u.id = COALESCE(p.user_id, mr.patient_id)
            LEFT JOIN LATERAL (
                SELECT id, decision, created_at, signed_at, doctor_id
                FROM ai_approvals 
                WHERE medical_record_id = mr.id 
                ORDER BY created_at DESC 
                LIMIT 1
            ) aa ON true
            LEFT JOIN doctors d ON d.user_id = aa.doctor_id
            LEFT JOIN users doc_user ON doc_user.id = d.user_id
            WHERE mr.patient_id = %s
            AND mr.status IN ('Processed', 'Explained', 'Checked')
            ORDER BY mr.uploaded_at DESC
            LIMIT %s
            """, (patient_user_id, limit))
            
            rows = cur.fetchall()
            print(f"[RDS History] Fetched {len(rows)} rows for patient {patient_user_id}")
            
            # Convert to list of dicts compatible with ClinicalAnalysisResult-like objects
            history = []
            for row in rows:
                try:
                    # RealDictCursor returns dict-like objects, but be defensive
                    if not isinstance(row, dict):
                        # If somehow not a dict, skip this row
                        print(f"  ⚠ Unexpected row type: {type(row)}, skipping...")
                        continue
                    
                    # Use .get() method for safe access
                    medical_record_id = row.get('medical_record_id')
                    analysis_id = row.get('analysis_id') or ''
                    patient_name = row.get('patient_name') or 'Unknown Patient'
                    document_type = row.get('document_type') or 'medical_report'
                    timestamp = row.get('timestamp')
                    status = row.get('status') or 'Unknown'
                    conditions_count = row.get('conditions_count') or 0
                    medications_count = row.get('medications_count') or 0
                    risk_level = row.get('risk_level') or 'unknown'
                    red_flags_count = row.get('red_flags_count') or 0
                    file_hash = row.get('file_hash') or ''
                    file_path = row.get('file_path')
                    original_filename = row.get('original_filename')
                    
                    # Review status information
                    review_approval_id = row.get('review_approval_id')
                    review_decision = row.get('review_decision')
                    review_requested_at = row.get('review_requested_at')
                    review_completed_at = row.get('review_completed_at')
                    review_doctor_name = row.get('review_doctor_name')
                    review_doctor_id = row.get('review_doctor_id')
                    
                    # Determine review status
                    review_status = 'not_requested'
                    if review_approval_id:
                        if review_completed_at:
                            review_status = 'completed'
                        else:
                            review_status = 'pending'
                    
                    # If file_path is missing but we have an analysis_id, try to find the file
                    if not file_path and analysis_id and analysis_id.startswith('CA-'):
                        # Files are stored in uploads/user_id_analysis_id/filename.pdf
                        # Get upload folder path (assuming web_app/uploads structure)
                        # rds_repository.py is in web_app/, so uploads is also in web_app/
                        try:
                            current_file_dir = os.path.dirname(os.path.abspath(__file__))
                            upload_folder = os.path.join(current_file_dir, 'uploads')
                            
                            # Try to find files in folders matching the pattern
                            if patient_user_id:
                                pattern_folder = f"{patient_user_id}_{analysis_id}"
                                pattern_path = os.path.join(upload_folder, pattern_folder)
                                if os.path.exists(pattern_path):
                                    # Find any PDF or image files in that folder
                                    for f in os.listdir(pattern_path):
                                        if f.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.txt', '.doc', '.docx')):
                                            file_path = os.path.join(pattern_folder, f)
                                            if not original_filename:
                                                original_filename = f
                                            print(f"[History Debug] Found file on disk for {analysis_id}: {file_path}")
                                            break
                        except Exception as e:
                            print(f"[History Debug] Error finding file for {analysis_id}: {e}")
                    
                    history.append({
                        'medical_record_id': medical_record_id,
                        'analysis_id': analysis_id,
                        'patient_name': patient_name,
                        'document_type': document_type,
                        'timestamp': timestamp,
                        'status': status,
                        'conditions': [] if conditions_count == 0 else ['Condition'] * conditions_count,  # Placeholder
                        'medications': [] if medications_count == 0 else ['Medication'] * medications_count,  # Placeholder
                        'risk_level': risk_level,
                        'red_flags': [] if red_flags_count == 0 else ['Red flag'] * red_flags_count,  # Placeholder
                        'success': status in ('Processed', 'Explained', 'Checked'),
                        'file_hash': file_hash,
                        'file_path': file_path,
                        'original_filename': original_filename,
                        # Review status
                        'review_status': review_status,
                        'review_decision': review_decision,
                        'review_requested_at': review_requested_at,
                        'review_completed_at': review_completed_at,
                        'review_doctor_name': review_doctor_name,
                        'review_doctor_id': review_doctor_id
                    })
                except Exception as e:
                    # Skip rows that can't be processed
                    print(f"⚠ Error processing history row: {e}")
                    print(f"   Row data: {row}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            return history
    except Exception as e:
        print(f"⚠ Error executing history query: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_clinical_analysis_result_from_rds(analysis_id: str = None, medical_record_id: int = None, 
                                           file_hash: str = None, patient_user_id: int = None) -> Optional[Dict[str, Any]]:
    """Get full clinical analysis result from RDS.
    Can be retrieved by analysis_id, medical_record_id, or file_hash.
    If patient_user_id is provided, ensures the analysis belongs to that user.
    Returns a dict that can be converted to ClinicalAnalysisResult.
    """
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Build query based on available identifier
        where_clause_parts = []
        params = []
        
        if medical_record_id:
            where_clause_parts.append("mr.id = %s")
            params.append(medical_record_id)
        elif file_hash:
            where_clause_parts.append("mr.file_hash = %s")
            params.append(file_hash)
        elif analysis_id:
            # First try to match file_hash directly if analysis_id is stored there
            # Otherwise, parse timestamp from analysis_id format (CA-YYYYMMDD-HHMMSS)
            if analysis_id.startswith('CA-'):
                # Try direct file_hash match first (if analysis_id is stored in file_hash)
                # Also try timestamp match as fallback for backward compatibility
                conditions = []
                condition_params = []
                
                # Add file_hash match
                conditions.append("mr.file_hash = %s")
                condition_params.append(analysis_id)
                
                # Also try timestamp match as fallback (for old data where file_hash was hashed)
                if len(analysis_id) == 17:  # CA-YYYYMMDD-HHMMSS format
                    try:
                        date_part = analysis_id[3:11]  # YYYYMMDD
                        time_part = analysis_id[12:16]  # HHMMSS
                        year = date_part[:4]
                        month = date_part[4:6]
                        day = date_part[6:8]
                        hour = time_part[:2]
                        minute = time_part[2:4]
                        sec = time_part[4:6]
                        timestamp_str = f"{year}-{month}-{day} {hour}:{minute}:{sec}"
                        conditions.append("mr.uploaded_at::timestamp = %s::timestamp")
                        condition_params.append(timestamp_str)
                    except Exception:
                        pass  # If timestamp parsing fails, just use file_hash match
                
                # Combine conditions with OR
                if len(conditions) > 1:
                    where_clause_parts.append("(" + " OR ".join(conditions) + ")")
                else:
                    where_clause_parts.append(conditions[0])
                
                params.extend(condition_params)
            else:
                return None
        else:
            return None
        
        # Add user filtering if patient_user_id is provided
        if patient_user_id:
            where_clause_parts.append("mr.patient_id = %s")
            params.append(patient_user_id)
        
        where_clause = " AND ".join(where_clause_parts)
        
        # Debug logging
        print(f"[RDS Debug] Query: WHERE {where_clause}")
        print(f"[RDS Debug] Params: {params}")
        
        # Check if file_path column exists in medical_records
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.columns 
                WHERE table_name = 'medical_records' AND column_name = 'file_path'
            ) AS has_file_path
        """)
        result = cur.fetchone()
        has_file_path = result.get('has_file_path') if isinstance(result, dict) else (result[0] if result else False)
        
        # Build SELECT clause with conditional columns
        file_path_select = ", mr.file_path" if has_file_path else ", NULL AS file_path"
        original_filename_select = ", mr.original_filename" if has_file_path else ", NULL AS original_filename"
        
        # Get medical record
        cur.execute(f"""
            SELECT 
                mr.id AS medical_record_id,
                mr.file_hash,
                mr.document_type,
                mr.uploaded_at AS timestamp,
                mr.status,
                p.user_id AS patient_id,
                u.name AS patient_name
                {file_path_select}
                {original_filename_select}
            FROM medical_records mr
            LEFT JOIN patients p ON p.user_id = mr.patient_id
            LEFT JOIN users u ON u.id = COALESCE(p.user_id, mr.patient_id)
            WHERE {where_clause}
            LIMIT 1
        """, params)
        
        mr_row = cur.fetchone()
        if not mr_row:
            print(f"[RDS Debug] No medical record found with WHERE clause: {where_clause}")
            print(f"[RDS Debug] Search params were: {params}")
            return None
        
        medical_record_id = mr_row['medical_record_id']
        
        # Get the actual analysis_id from file_hash or construct from timestamp
        file_hash_from_db = mr_row.get('file_hash', '')
        if file_hash_from_db and file_hash_from_db.startswith('CA-'):
            actual_analysis_id = file_hash_from_db
        else:
            # Construct from timestamp as fallback
            ts = mr_row['timestamp']
            actual_analysis_id = f"CA-{ts.strftime('%Y%m%d-%H%M%S')}"
        
        print(f"[RDS Debug] Found medical record: id={medical_record_id}, file_hash={file_hash_from_db}, analysis_id={actual_analysis_id}")
        
        # Get FHIR bundle
        cur.execute("""
            SELECT json::text AS fhir_json
            FROM fhir_bundles
            WHERE medical_record_id = %s
            ORDER BY generated_at DESC
            LIMIT 1
        """, (medical_record_id,))
        
        fhir_row = cur.fetchone()
        fhir_bundle = None
        if fhir_row:
            import json as jsonlib
            fhir_bundle = jsonlib.loads(fhir_row['fhir_json'])
        
        # Get explanation
        cur.execute("""
            SELECT summary_md, risks_md, mistral_analysis, low_confidence
            FROM explanations
            WHERE medical_record_id = %s
            ORDER BY generated_at DESC
            LIMIT 1
        """, (medical_record_id,))
        
        exp_row = cur.fetchone()
        explanation_text = None
        risks_md = None
        mistral_analysis = None
        if exp_row:
            explanation_text = exp_row['summary_md']
            risks_md = exp_row['risks_md']
            mistral_analysis = exp_row.get('mistral_analysis')
        
        # Get safety flags
        cur.execute("""
            SELECT type, severity, details
            FROM safety_flags
            WHERE medical_record_id = %s
            ORDER BY severity DESC
        """, (medical_record_id,))
        
        safety_flags = cur.fetchall()
        red_flags = []
        for flag in safety_flags:
            details = flag.get('details') or f"{flag.get('type', 'Unknown')} flag"
            red_flags.append(f"{flag['severity'].upper()}: {details}")
        
        # Extract entities from FHIR bundle
        conditions = []
        medications = []
        observations = []
        procedures = []
        
        if fhir_bundle:
            for entry in fhir_bundle.get('entry', []):
                resource = entry.get('resource', {})
                res_type = resource.get('resourceType')
                
                if res_type == 'Condition':
                    code = resource.get('code', {})
                    text = code.get('text', code.get('coding', [{}])[0].get('display', ''))
                    if text:
                        conditions.append(text)
                elif res_type in ('MedicationStatement', 'MedicationRequest'):
                    med_code = resource.get('medicationCodeableConcept', {})
                    text = med_code.get('text', med_code.get('coding', [{}])[0].get('display', ''))
                    if text:
                        medications.append(text)
                elif res_type == 'Observation':
                    code = resource.get('code', {})
                    text = code.get('text', code.get('coding', [{}])[0].get('display', ''))
                    if text:
                        observations.append(text)
                elif res_type == 'Procedure':
                    code = resource.get('code', {})
                    text = code.get('text', code.get('coding', [{}])[0].get('display', ''))
                    if text:
                        procedures.append(text)
        
        # Determine risk level
        risk_level = 'unknown'
        if red_flags:
            if any('CRITICAL' in f.upper() for f in red_flags):
                risk_level = 'critical'
            elif any('HIGH' in f.upper() for f in red_flags):
                risk_level = 'high'
            else:
                risk_level = 'medium'
        elif not exp_row or not exp_row['low_confidence']:
            risk_level = 'low'
        
        # Use the actual analysis_id we determined above
        file_path_val = mr_row.get('file_path')
        original_filename_val = mr_row.get('original_filename')
        
        # Debug logging
        print(f"[RDS Retrieve Debug] Retrieved file_path: {file_path_val}")
        print(f"[RDS Retrieve Debug] Retrieved original_filename: {original_filename_val}")
        
        return {
            'analysis_id': actual_analysis_id,
            'medical_record_id': medical_record_id,
            'timestamp': mr_row['timestamp'],
            'success': mr_row['status'] in ('Processed', 'Explained', 'Checked'),
            'error_message': None if mr_row['status'] in ('Processed', 'Explained', 'Checked') else 'Processing failed',
            'patient_name': mr_row['patient_name'],
            'document_type': mr_row['document_type'],
            'conditions': conditions,
            'medications': medications,
            'observations': observations,
            'procedures': procedures,
            'red_flags': red_flags,
            'risk_level': risk_level,
            'fhir_bundle': fhir_bundle,
            'explanation_text': explanation_text,
            'risks_md': risks_md,
            'mistral_analysis': mistral_analysis,
            'file_path': file_path_val,
            'original_filename': original_filename_val
        }


def delete_clinical_analysis_from_rds(analysis_id: str, patient_user_id: int) -> bool:
    """
    Delete a clinical analysis from RDS.
    Verifies ownership by checking patient_id matches the current user.
    Returns True if deletion was successful, False otherwise.
    """
    try:
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            conn.autocommit = False
            
            # Try to match by file_hash (analysis_id) first
            # Also try matching by timestamp if analysis_id follows CA-YYYYMMDD-HHMMSS format
            cur.execute("""
                SELECT id, file_hash, patient_id, uploaded_at
                FROM medical_records
                WHERE patient_id = %s
                AND (
                    file_hash = %s
                    OR file_hash LIKE %s
                    OR (
                        file_hash IS NULL 
                        AND uploaded_at::text LIKE %s
                    )
                )
                LIMIT 1
            """, (
                patient_user_id,
                analysis_id,
                f"%{analysis_id}%",
                f"%{analysis_id.replace('CA-', '')}%"
            ))
            
            mr_row = cur.fetchone()
            
            if not mr_row:
                print(f"[RDS Delete] No medical record found for analysis_id={analysis_id}, patient_id={patient_user_id}")
                return False
            
            medical_record_id = mr_row['id']
            
            # Verify ownership
            if mr_row['patient_id'] != patient_user_id:
                print(f"[RDS Delete] Ownership mismatch: record belongs to patient_id={mr_row['patient_id']}, but user is {patient_user_id}")
                return False
            
            print(f"[RDS Delete] Found medical record: id={medical_record_id}, file_hash={mr_row.get('file_hash')}, patient_id={mr_row['patient_id']}")
            
            # Delete from related tables (cascading deletes will handle most, but we'll be explicit)
            # Delete processing jobs
            cur.execute("DELETE FROM processing_jobs WHERE medical_record_id = %s", (medical_record_id,))
            
            # Delete safety flags
            cur.execute("DELETE FROM safety_flags WHERE medical_record_id = %s", (medical_record_id,))
            
            # Delete explanations (which may cascade to safety_flags via explanation_id)
            cur.execute("DELETE FROM explanations WHERE medical_record_id = %s", (medical_record_id,))
            
            # Delete FHIR bundles
            cur.execute("DELETE FROM fhir_bundles WHERE medical_record_id = %s", (medical_record_id,))
            
            # Delete from clinical_analysis_data if it exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'clinical_analysis_data'
                )
            """)
            result = cur.fetchone()
            has_clinical_data_table = result[0] if result else False
            
            if has_clinical_data_table:
                cur.execute("DELETE FROM clinical_analysis_data WHERE medical_record_id = %s", (medical_record_id,))
            
            # Delete AI approvals if any
            cur.execute("DELETE FROM ai_approvals WHERE medical_record_id = %s", (medical_record_id,))
            
            # Finally, delete the medical record itself (cascades will handle references)
            cur.execute("DELETE FROM medical_records WHERE id = %s", (medical_record_id,))
            
            conn.commit()
            
            print(f"[RDS Delete] Successfully deleted analysis {analysis_id} (medical_record_id={medical_record_id})")
            return True
            
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            print(f"[RDS Delete] Error deleting analysis from RDS: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_all_approved_doctors() -> List[Dict[str, Any]]:
    """Get all approved doctors with their specializations and details.
    Returns list of doctors with id, username, name, email, specialization, 
    license_number, ahpra_number, qualification, clinic_address, approval_status.
    """
    try:
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    u.id,
                    u.username,
                    u.email,
                    u.name,
                    d.specialization,
                    d.license_number,
                    d.ahpra_number,
                    d.qualification,
                    d.clinic_address,
                    d.approval_status
                FROM users u
                JOIN doctors d ON d.user_id = u.id
                WHERE d.approval_status = 'Approved'
                ORDER BY u.name, d.specialization
            """)
            doctors = cur.fetchall()
            return [dict(doctor) for doctor in doctors] if doctors else []
    except Exception as e:
        print(f"[RDS] Error fetching approved doctors: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_review_request(patient_user_id: int, doctor_user_id: int, 
                       medical_record_id: int, analysis_id: str, 
                       notes: str = None) -> Optional[int]:
    """Save a review request from patient to doctor.
    Creates a pending review entry in ai_approvals table.
    Returns the approval record id if successful, None otherwise.
    """
    try:
        with _conn() as conn, conn.cursor() as cur:
            # First, get the explanation_id if available
            explanation_id = None
            cur.execute("""
                SELECT id FROM explanations 
                WHERE medical_record_id = %s 
                LIMIT 1
            """, (medical_record_id,))
            exp_row = cur.fetchone()
            if exp_row:
                explanation_id = exp_row[0]
            
            # Check if review request already exists
            cur.execute("""
                SELECT id FROM ai_approvals 
                WHERE medical_record_id = %s AND doctor_id = %s AND signed_at IS NULL
            """, (medical_record_id, doctor_user_id))
            existing = cur.fetchone()
            if existing:
                print(f"[RDS] Review request already exists: approval_id={existing[0]}")
                return existing[0]
            
            # Insert review request with decision='NeedsChanges' as pending review
            # (We'll update it to 'Approved' or 'Rejected' when doctor reviews)
            cur.execute("""
                INSERT INTO ai_approvals (
                    medical_record_id,
                    explanation_id,
                    doctor_id,
                    decision,
                    notes,
                    created_at
                )
                VALUES (%s, %s, %s, %s::approval_decision, %s, NOW())
                RETURNING id
            """, (medical_record_id, explanation_id, doctor_user_id, 'NeedsChanges', notes))
            
            result = cur.fetchone()
            if result:
                approval_id = result[0]
                conn.commit()
                print(f"[RDS] Saved review request: approval_id={approval_id}, patient={patient_user_id}, doctor={doctor_user_id}, analysis={analysis_id}")
                return approval_id
            else:
                conn.commit()
                return None
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"[RDS] Error saving review request: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_pending_reviews_for_doctor(doctor_user_id: int) -> List[Dict[str, Any]]:
    """Get all pending reviews for a specific doctor from database.
    Returns list of review requests with analysis details.
    """
    try:
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First, let's verify what's in the database for debugging
            cur.execute("""
                SELECT 
                    aa.id AS approval_id,
                    aa.medical_record_id,
                    aa.doctor_id,
                    aa.decision,
                    aa.signed_at,
                    aa.created_at,
                    mr.file_hash AS analysis_id
                FROM ai_approvals aa
                JOIN medical_records mr ON mr.id = aa.medical_record_id
                WHERE aa.doctor_id = %s
                ORDER BY aa.created_at DESC
                LIMIT 10
            """, (doctor_user_id,))
            
            all_reviews = cur.fetchall()
            print(f"[Pending Reviews Debug] All reviews for doctor {doctor_user_id}:")
            for r in all_reviews:
                print(f"  - Approval {r.get('approval_id')}: decision={r.get('decision')}, signed_at={r.get('signed_at')}, analysis_id={r.get('analysis_id')}")
            
            # Now get only pending ones (signed_at IS NULL)
            cur.execute("""
                SELECT 
                    aa.id AS approval_id,
                    aa.medical_record_id,
                    aa.doctor_id,
                    aa.decision,
                    aa.notes,
                    aa.created_at AS requested_at,
                    aa.signed_at,
                    mr.file_hash AS analysis_id,
                    mr.patient_id,
                    mr.document_type,
                    mr.uploaded_at,
                    mr.file_path,
                    mr.original_filename,
                    u.name AS patient_name,
                    u.email AS patient_email,
                    u.username AS patient_username
                FROM ai_approvals aa
                JOIN medical_records mr ON mr.id = aa.medical_record_id
                JOIN users u ON u.id = mr.patient_id
                WHERE aa.doctor_id = %s
                AND aa.signed_at IS NULL  -- Not yet reviewed (this is the key filter)
                ORDER BY aa.created_at DESC
            """, (doctor_user_id,))
            
            reviews = cur.fetchall()
            print(f"[Pending Reviews] Found {len(reviews)} pending reviews for doctor {doctor_user_id}")
            for r in reviews:
                print(f"  - Pending: approval_id={r.get('approval_id')}, analysis_id={r.get('analysis_id')}, signed_at={r.get('signed_at')}")
            
            return [dict(review) for review in reviews] if reviews else []
    except Exception as e:
        print(f"[RDS] Error fetching pending reviews: {e}")
        import traceback
        traceback.print_exc()
        return []


def update_approval_decision_in_rds(approval_id: int, doctor_user_id: int, 
                                   decision: str, notes: str = None,
                                   signed_at: datetime = None) -> bool:
    """Update approval decision in ai_approvals table.
    
    Args:
        approval_id: The ai_approvals.id to update
        doctor_user_id: The doctor's user_id (for verification)
        decision: 'Approved' or 'Rejected' (approval_decision enum)
        notes: Optional notes from the doctor
        signed_at: Timestamp when signed (defaults to NOW())
    
    Returns:
        True if successful, False otherwise
    """
    try:
        with _conn() as conn, conn.cursor() as cur:
            # Verify the approval belongs to this doctor
            cur.execute("""
                SELECT id FROM ai_approvals 
                WHERE id = %s AND doctor_id = %s
            """, (approval_id, doctor_user_id))
            verify = cur.fetchone()
            
            if not verify:
                print(f"[RDS Update Approval] Approval {approval_id} not found for doctor {doctor_user_id}")
                return False
            
            # Update the approval decision
            update_time = signed_at or datetime.now()
            
            # First verify current state
            cur.execute("""
                SELECT id, decision, signed_at FROM ai_approvals 
                WHERE id = %s AND doctor_id = %s
            """, (approval_id, doctor_user_id))
            before = cur.fetchone()
            if before:
                print(f"[RDS Update] Before update - approval {approval_id}: decision={before[1]}, signed_at={before[2]}")
            
            cur.execute("""
                UPDATE ai_approvals
                SET decision = %s::approval_decision,
                    notes = COALESCE(%s, notes),
                    signed_at = %s
                WHERE id = %s AND doctor_id = %s
            """, (decision, notes, update_time, approval_id, doctor_user_id))
            
            rows_updated = cur.rowcount
            conn.commit()
            
            # Verify after update
            cur.execute("""
                SELECT id, decision, signed_at FROM ai_approvals 
                WHERE id = %s AND doctor_id = %s
            """, (approval_id, doctor_user_id))
            after = cur.fetchone()
            if after:
                print(f"[RDS Update] After update - approval {approval_id}: decision={after[1]}, signed_at={after[2]}, rows_updated={rows_updated}")
            
            if rows_updated == 0:
                print(f"[RDS Update] ⚠️ WARNING: No rows updated for approval {approval_id}")
                return False
            
            print(f"[RDS] ✅ Updated approval {approval_id}: decision={decision}, signed_at={update_time}")
            return True
            
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f"[RDS] Error updating approval decision: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_review_status_for_analysis(medical_record_id: int) -> Dict[str, Any]:
    """Get review status for an analysis.
    Returns dict with review_status, doctor_id, doctor_name, decision, etc.
    """
    try:
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    aa.id AS approval_id,
                    aa.doctor_id,
                    aa.decision,
                    aa.notes,
                    aa.created_at AS requested_at,
                    aa.signed_at AS reviewed_at,
                    d.user_id,
                    u.name AS doctor_name,
                    u.email AS doctor_email
                FROM ai_approvals aa
                JOIN doctors d ON d.user_id = aa.doctor_id
                JOIN users u ON u.id = d.user_id
                WHERE aa.medical_record_id = %s
                ORDER BY aa.created_at DESC
                LIMIT 1
            """, (medical_record_id,))
            
            review = cur.fetchone()
            if review:
                status = 'pending' if review.get('signed_at') is None else 'reviewed'
                return {
                    'status': status,
                    'doctor_id': review.get('doctor_id'),
                    'doctor_name': review.get('doctor_name'),
                    'decision': review.get('decision'),
                    'requested_at': review.get('requested_at'),
                    'reviewed_at': review.get('reviewed_at'),
                    'notes': review.get('notes')
                }
            return {'status': 'not_requested'}
    except Exception as e:
        print(f"[RDS] Error fetching review status: {e}")
        import traceback
        traceback.print_exc()
        return {'status': 'error'}


def get_doctor_complete_profile(doctor_user_id: int) -> Optional[Dict[str, Any]]:
    """Get complete doctor profile for viewing (used by admins and patients).
    Returns dict with all user and doctor-specific details.
    """
    try:
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check if user exists in doctors table (that's how we identify doctors)
            cur.execute("""
                SELECT 
                    u.id,
                    u.username,
                    u.email,
                    u.name,
                    u.created_at AS user_created_at,
                    d.specialization,
                    d.license_number,
                    d.ahpra_number,
                    d.qualification,
                    d.clinic_address,
                    d.approval_status,
                    d.created_at AS doctor_created_at
                FROM users u
                INNER JOIN doctors d ON d.user_id = u.id
                WHERE u.id = %s
            """, (doctor_user_id,))
            
            profile = cur.fetchone()
            if profile:
                return dict(profile)
            
            # Debug: Check if user exists at all
            cur.execute("SELECT id, username, name, email FROM users WHERE id = %s", (doctor_user_id,))
            user_check = cur.fetchone()
            if user_check:
                print(f"[RDS Debug] User {doctor_user_id} exists but is not in doctors table")
            else:
                print(f"[RDS Debug] User {doctor_user_id} does not exist")
            
            return None
    except Exception as e:
        print(f"[RDS] Error fetching doctor profile: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_review_history_from_rds(doctor_user_id: int = None, limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Fetch all review history (approval decisions) from AWS RDS.
    
    Args:
        doctor_user_id: Optional filter by specific doctor. If None, returns all reviews.
        limit: Maximum number of records to return (default 1000)
    
    Returns:
        List of dictionaries containing review history data with structure:
        {
            'approval_id': int,
            'medical_record_id': int,
            'analysis_id': str (file_hash),
            'doctor_id': int,
            'doctor_name': str,
            'decision': str ('Approved', 'Rejected', 'NeedsChanges'),
            'notes': str,
            'signed_at': datetime,
            'created_at': datetime,
            'patient_name': str
        }
    """
    try:
        from psycopg2.extras import RealDictCursor
        
        with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT 
                    aa.id AS approval_id,
                    aa.medical_record_id,
                    aa.doctor_id,
                    aa.decision,
                    aa.notes,
                    aa.signed_at,
                    aa.created_at,
                    mr.file_hash AS analysis_id,
                    mr.patient_id,
                    COALESCE(u.name, u.username, 'Unknown Doctor') AS doctor_name,
                    COALESCE(pu.name, pu.username, 'Unknown Patient') AS patient_name
                FROM ai_approvals aa
                JOIN medical_records mr ON mr.id = aa.medical_record_id
                JOIN doctors d ON d.user_id = aa.doctor_id
                JOIN users u ON u.id = d.user_id
                LEFT JOIN users pu ON pu.id = mr.patient_id
                WHERE aa.signed_at IS NOT NULL
            """
            
            params = []
            if doctor_user_id:
                query += " AND aa.doctor_id = %s"
                params.append(doctor_user_id)
            
            query += " ORDER BY aa.signed_at DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            rows = cur.fetchall()
            
            reviews = []
            for row in rows:
                review = {
                    'approval_id': row.get('approval_id'),
                    'medical_record_id': row.get('medical_record_id'),
                    'analysis_id': row.get('analysis_id') or f"MR-{row.get('medical_record_id')}",
                    'doctor_id': row.get('doctor_id'),
                    'doctor_name': row.get('doctor_name') or 'Unknown Doctor',
                    'decision': row.get('decision'),
                    'notes': row.get('notes') or '',
                    'signed_at': row.get('signed_at'),
                    'created_at': row.get('created_at'),
                    'patient_name': row.get('patient_name') or 'Unknown Patient',
                    'patient_id': row.get('patient_id')
                }
                reviews.append(review)
            
            print(f"[RDS Review History] Fetched {len(reviews)} reviews from database")
            return reviews
            
    except Exception as e:
        print(f"[RDS Review History] Error fetching review history: {e}")
        import traceback
        traceback.print_exc()
        return []


def update_user_password(user_id: int, new_password_hash: str) -> bool:
    """
    Update user's password in the database.
    
    Args:
        user_id: The user's ID (integer)
        new_password_hash: The hashed password (already hashed with werkzeug.security.generate_password_hash)
    
    Returns:
        True if update was successful, False otherwise
    """
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (new_password_hash, user_id)
            )
            conn.commit()
            
            if cur.rowcount > 0:
                print(f"[RDS] Successfully updated password for user {user_id}")
                return True
            else:
                print(f"[RDS] No user found with id {user_id} to update password")
                return False
    except Exception as e:
        print(f"[RDS] Error updating password for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return False

