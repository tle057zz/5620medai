import os
from typing import Dict, Any, List
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

        cur.execute(
            "SELECT * FROM medical_histories WHERE patient_id=%s ORDER BY last_updated DESC LIMIT 1",
            (user_id,),
        )
        history = cur.fetchone()

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

        return {
            "profile": profile,
            "health_data": health,
            "medical_history": history,
            "income_details": income,
            "quotes": quotes,
            "policies": policies,
            "appointments": appts,
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


