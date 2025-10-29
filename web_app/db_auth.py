"""
Lightweight DB authentication against the RDS schema (users/doctors/patients).
Keeps demo logins intact; only used if enabled via env vars.
"""

import os
from typing import Optional
import psycopg2
from psycopg2.extras import DictCursor
from werkzeug.security import check_password_hash


def _get_conn():
    # Prefer DATABASE_URL if provided
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # psycopg2 can accept a URL directly
        return psycopg2.connect(database_url)

    # Fallback to discrete vars (defaults provided for convenience)
    host = os.environ.get("DB_HOST", "elec5620-as02-database.c38ki6o4abha.ap-southeast-2.rds.amazonaws.com")
    port = int(os.environ.get("DB_PORT", "5432"))
    dbname = os.environ.get("DB_NAME", "postgres")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "ghR4BwyqbEM1xhmrCKbM")
    return psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)


def fetch_user(username: str) -> Optional[dict]:
    """Fetch a user row and infer role from doctors/patients tables."""
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT id, username, email, password_hash, name FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
            if not row:
                return None
            user_id = row["id"]
            # infer role
            cur.execute("SELECT 1 FROM doctors WHERE user_id = %s", (user_id,))
            role = "doctor" if cur.fetchone() else None
            if not role:
                cur.execute("SELECT 1 FROM patients WHERE user_id = %s", (user_id,))
                role = "patient" if cur.fetchone() else "patient"
            return {
                "id": str(user_id),
                "username": row["username"],
                "email": row["email"],
                "password_hash": row["password_hash"],
                "display_name": row["name"],
                "role": role,
            }


def fetch_user_by_id(user_id: str) -> Optional[dict]:
    """Fetch a user by numeric/string id. Returns same shape as fetch_user."""
    with _get_conn() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            try:
                uid = int(user_id)
            except Exception:
                uid = user_id
            cur.execute("SELECT id, username, email, password_hash, name FROM users WHERE id = %s", (uid,))
            row = cur.fetchone()
            if not row:
                return None
            user_id_val = row["id"]
            cur.execute("SELECT 1 FROM doctors WHERE user_id = %s", (user_id_val,))
            role = "doctor" if cur.fetchone() else None
            if not role:
                cur.execute("SELECT 1 FROM patients WHERE user_id = %s", (user_id_val,))
                role = "patient" if cur.fetchone() else "patient"
            return {
                "id": str(user_id_val),
                "username": row["username"],
                "email": row["email"],
                "password_hash": row["password_hash"],
                "display_name": row["name"],
                "role": role,
            }


def verify_password(stored_hash: str, plain_password: str) -> bool:
    """Accept hashed checks; if not hashed, allow DEFAULT_DB_PASSWORD (demo)."""
    if stored_hash and stored_hash.startswith("pbkdf2:"):
        try:
            return check_password_hash(stored_hash, plain_password)
        except Exception:
            return False
    # Demo mode: allow a default password for imported/mock rows
    default_pwd = os.environ.get("DEFAULT_DB_PASSWORD", "password123")
    return plain_password == default_pwd


def split_name_for_display(name: str | None, username: str) -> tuple[str, str]:
    """Normalize a full name into (first_name, last_name) for UI.
    Removes honorifics like 'Dr.' to avoid 'Dr. Dr.' rendering.
    """
    if not name:
        return username, ""
    cleaned = name.strip()
    # Remove common titles
    prefixes = ["Dr.", "Dr", "MR.", "MR", "Mr.", "Mr", "Ms.", "Ms", "Mrs.", "Mrs"]
    for p in prefixes:
        if cleaned.startswith(p + " "):
            cleaned = cleaned[len(p) + 1 :].strip()
            break
    parts = cleaned.split()
    if not parts:
        return username, ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


