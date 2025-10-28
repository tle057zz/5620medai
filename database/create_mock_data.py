import os
import random
import string
import uuid
from datetime import datetime, timedelta, date

import psycopg2


HOST = "elec5620-as02-database.c38ki6o4abha.ap-southeast-2.rds.amazonaws.com"
PORT = 5432
DBNAME = "postgres"
USER = "postgres"
PASSWORD = "ghR4BwyqbEM1xhmrCKbM"


def rand_str(prefix: str, n: int = 6) -> str:
    return f"{prefix}{''.join(random.choices(string.ascii_lowercase, k=n))}"


def get_conn():
    return psycopg2.connect(host=HOST, port=PORT, dbname=DBNAME, user=USER, password=PASSWORD)


def fetchone(cur, sql, params=None):
    cur.execute(sql, params or ())
    return cur.fetchone()


def fetchall(cur, sql, params=None):
    cur.execute(sql, params or ())
    return cur.fetchall()


def get_or_create_user(cur, username: str, name: str, email: str) -> int:
    row = fetchone(cur, "SELECT id FROM users WHERE username = %s", (username,))
    if row:
        return row[0]
    cur.execute(
        """
        INSERT INTO users(name, email, password_hash, username)
        VALUES (%s,%s,'x',%s)
        RETURNING id
        """,
        (name, email, username),
    )
    return cur.fetchone()[0]


def get_or_create_product(cur, name: str, provider: str, premium: float) -> int:
    row = fetchone(cur, "SELECT id FROM insurance_products WHERE name = %s AND provider = %s", (name, provider))
    if row:
        return row[0]
    cur.execute(
        """
        INSERT INTO insurance_products(name, coverage, premium, provider, product_link, insurance_type)
        VALUES (%s,'General cover',%s,%s,%s,'Health')
        RETURNING id
        """,
        (name, premium, provider, f"https://example.com/{name.replace(' ', '-').lower()}"),
    )
    return cur.fetchone()[0]


def main():
    random.seed(5620)
    with get_conn() as conn:
        conn.autocommit = False
        cur = conn.cursor()

        # quick short-circuit: if we already loaded data, skip to avoid dupes
        row = fetchone(cur, "SELECT COUNT(*) FROM users")
        if row and row[0] > 0:
            print(f"ℹ️ Existing users: {row[0]} (script will add only idempotent rows)")

        # ---- doctors and patients ----
        doctor_ids = []
        for i in range(5):
            username = f"dr.{['smith','jones','lee','patel','nguyen'][i]}"
            name = f"Dr. {username.split('.')[1].capitalize()}"
            email = f"{username.replace('.', '')}@example.com"
            uid = get_or_create_user(cur, username, name, email)
            doctor_ids.append(uid)
            cur.execute(
                """
                INSERT INTO doctors(user_id, specialization, license_number, qualification, availability_status)
                VALUES (%s, %s, %s, %s, 'Available')
                ON CONFLICT (user_id) DO NOTHING
                """,
                (uid, random.choice(['Cardiology','GP','Dermatology','Endocrinology','Neurology']), f"LIC-{uid:05d}", 'MBBS'),
            )

        patient_ids = []
        for i in range(20):
            username = f"patient{i+1}"
            name = f"Patient {i+1}"
            email = f"{username}@example.com"
            uid = get_or_create_user(cur, username, name, email)
            patient_ids.append(uid)
            cur.execute(
                """
                INSERT INTO patients(user_id, assigned_doctor_id, consent_on_ai, consent_timestamp)
                VALUES (%s, %s, TRUE, NOW())
                ON CONFLICT (user_id) DO NOTHING
                """,
                (uid, random.choice(doctor_ids)),
            )

        # ---- insurance products ----
        product_ids = []
        for i in range(5):
            pid = get_or_create_product(cur, f"Health Plan {i+1}", random.choice(['MediCo','HealthPlus','CareOne']), round(random.uniform(60, 180), 2))
            product_ids.append(pid)

        # ---- health data / histories / income ----
        for pid in patient_ids:
            # 3 health rows each
            base_date = date.today()
            for d in range(3):
                cur.execute(
                    """
                    INSERT INTO health_data(patient_id, weight_kg, height_cm, bp_systolic, bp_diastolic, measure_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        pid,
                        round(random.uniform(55, 100), 1),
                        round(random.uniform(150, 190), 1),
                        random.randint(110, 135),
                        random.randint(70, 90),
                        base_date - timedelta(days=30 * d),
                    ),
                )
            cur.execute(
                """
                INSERT INTO medical_histories(patient_id, surgeries, medication, past_illness)
                VALUES (%s, 'appendectomy', 'metformin', 'asthma')
                ON CONFLICT DO NOTHING
                """,
                (pid,),
            )
            cur.execute(
                """
                INSERT INTO income_details(patient_id, annual_income, employment_status, dependents, effective_date)
                VALUES (%s, %s, %s, %s, CURRENT_DATE)
                ON CONFLICT DO NOTHING
                """,
                (pid, round(random.uniform(45000, 140000), 2), random.choice(['Employed','SelfEmployed','Student','Unemployed']), random.randint(0, 3)),
            )

        # ---- quotes + policy holds ----
        quote_ids = []
        policy_count = 0
        for pid in patient_ids:
            prod = random.choice(product_ids)
            cur.execute(
                """
                INSERT INTO quotes(suitability_score, cost, coverage_summary, insurance_product_id, patient_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (random.randint(50, 95), round(random.uniform(70, 200), 2), 'Auto-generated coverage', prod, pid),
            )
            quote_ids.append(cur.fetchone()[0])
            # policy hold for subset
            if random.random() < 0.5:
                start = date.today() - timedelta(days=random.randint(0, 400))
                end = None if random.random() < 0.7 else start + timedelta(days=random.randint(30, 365))
                cur.execute(
                    """
                    INSERT INTO policy_holds(insurance_product_id, patient_id, start_date, end_date)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (prod, pid, start, end),
                )
                policy_count += 1

        # ensure at least one policy
        if policy_count == 0 and product_ids and patient_ids:
            cur.execute(
                """
                INSERT INTO policy_holds(insurance_product_id, patient_id, start_date)
                VALUES (%s, %s, CURRENT_DATE)
                ON CONFLICT DO NOTHING
                """,
                (product_ids[0], patient_ids[0]),
            )
            policy_count = 1

        # ---- requests ----
        request_ids = []
        for pid in patient_ids:
            cur.execute(
                """
                INSERT INTO quote_requests(user_input, patient_id, processing_status)
                VALUES ('need a plan', %s, 'Submitted')
                RETURNING id
                """,
                (pid,),
            )
            request_ids.append(cur.fetchone()[0])

        # link some health rows to requests
        for rid in request_ids:
            rows = fetchall(cur, "SELECT id FROM health_data ORDER BY random() LIMIT 2")
            for (hd_id,) in rows:
                cur.execute(
                    """
                    INSERT INTO quote_request_health_data(quote_request_id, health_data_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (rid, hd_id),
                )

        # ensure at least one link exists
        (links_cnt,) = fetchone(cur, "SELECT COUNT(*) FROM quote_request_health_data")
        if links_cnt == 0 and request_ids:
            (one_hd,) = fetchone(cur, "SELECT id FROM health_data LIMIT 1")
            if one_hd:
                cur.execute(
                    """
                    INSERT INTO quote_request_health_data(quote_request_id, health_data_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (request_ids[0], one_hd),
                )

        # ---- AI + recs ----
        cur.execute(
            """
            INSERT INTO ai_agents(agent_name, api_address, model_version)
            VALUES ('Local-Ollama','http://127.0.0.1:11434','llama2')
            ON CONFLICT DO NOTHING
            """
        )
        cur.execute(
            """
            INSERT INTO recommendation_controllers(strategy, version)
            VALUES ('Hybrid','v1')
            ON CONFLICT DO NOTHING
            RETURNING id
            """
        )
        row = cur.fetchone()
        controller_id = row[0] if row else fetchone(cur, "SELECT id FROM recommendation_controllers ORDER BY id LIMIT 1")[0]

        rec_count = 0
        for qid in quote_ids[: min(len(quote_ids), 20)]:
            pid = fetchone(cur, "SELECT patient_id FROM quotes WHERE id = %s", (qid,))[0]
            cur.execute(
                """
                INSERT INTO quote_recommendations(recommendation_controller_id, quote_id, patient_id, rank, suitability_score, rationale)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (controller_id, qid, pid, 1, random.randint(60, 95), 'Mock recommendation'),
            )
            rec_count += 1

        if rec_count == 0 and quote_ids:
            pid = fetchone(cur, "SELECT patient_id FROM quotes WHERE id = %s", (quote_ids[0],))[0]
            cur.execute(
                """
                INSERT INTO quote_recommendations(recommendation_controller_id, quote_id, patient_id, rank, suitability_score, rationale)
                VALUES (%s, %s, %s, 1, 80, 'Seed rec')
                ON CONFLICT DO NOTHING
                """,
                (controller_id, quote_ids[0], pid),
            )

        # ---- appointments ----
        for pid in patient_ids[:15]:
            did = random.choice(doctor_ids)
            apptime = datetime.utcnow() + timedelta(days=random.randint(-10, 20))
            cur.execute(
                """
                INSERT INTO appointments(doctor_id, patient_id, appointment_at, status, type, notes)
                VALUES (%s, %s, %s, 'Requested', 'Consult', 'Initial consult')
                ON CONFLICT DO NOTHING
                """,
                (did, pid, apptime),
            )

        # ---- medical records + downstream artifacts ----
        mr_count = 0
        for pid in patient_ids[:10]:
            file_hash = uuid.uuid4().hex
            cur.execute(
                """
                INSERT INTO medical_records(file_hash, patient_id, pages, size_mb)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (file_hash, pid, random.randint(1, 12), round(random.uniform(0.2, 3.5), 3)),
            )
            mr_id = cur.fetchone()[0]
            cur.execute(
                """
                INSERT INTO fhir_bundles(medical_record_id, json, valid)
                VALUES (%s, '{"resourceType":"Bundle"}', TRUE)
                """,
                (mr_id,),
            )
            cur.execute(
                """
                INSERT INTO explanations(medical_record_id, summary_md, pathway_md, risks_md, low_confidence)
                VALUES (%s, 'Summary text', 'Pathway text', 'Risk text', FALSE)
                RETURNING id
                """,
                (mr_id,),
            )
            expl_id = cur.fetchone()[0]
            cur.execute(
                """
                INSERT INTO safety_flags(medical_record_id, explanation_id, type, severity, details)
                VALUES (%s, %s, 'Allergy', 'Low', 'No serious risks')
                """,
                (mr_id, expl_id),
            )
            cur.execute(
                """
                INSERT INTO processing_jobs(medical_record_id, kind, status, latency_ms)
                VALUES (%s, 'OCR', 'Succeeded', 1200)
                """,
                (mr_id,),
            )
            mr_count += 1

        # Ensure at least one record path exists
        if mr_count == 0 and patient_ids:
            pid = patient_ids[0]
            file_hash = uuid.uuid4().hex
            cur.execute(
                """
                INSERT INTO medical_records(file_hash, patient_id, pages, size_mb)
                VALUES (%s, %s, 1, 0.5)
                RETURNING id
                """,
                (file_hash, pid),
            )
            mr_id = cur.fetchone()[0]
            cur.execute("INSERT INTO fhir_bundles(medical_record_id, json, valid) VALUES (%s, '{""resourceType"":""Bundle""}', TRUE)", (mr_id,))
            cur.execute("INSERT INTO explanations(medical_record_id, summary_md) VALUES (%s, 'Seed explanation') RETURNING id", (mr_id,))
            expl_id = cur.fetchone()[0]
            cur.execute("INSERT INTO safety_flags(medical_record_id, explanation_id, type, severity) VALUES (%s,%s,'Allergy','Low')", (mr_id, expl_id))
            cur.execute("INSERT INTO processing_jobs(medical_record_id, kind, status) VALUES (%s,'OCR','Succeeded')", (mr_id,))

        # ---- audit logs ----
        for _ in range(20):
            cur.execute(
                """
                INSERT INTO audit_logs(actor_user_id, action, object_type, object_id, details_hash)
                VALUES (NULL, 'Insert', 'mock', %s, %s)
                """,
                (uuid.uuid4().hex[:8], uuid.uuid4().hex),
            )

        conn.commit()
        print("✅ Mock data created.")

        # Print quick counts per table
        q = """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type='BASE TABLE'
          AND table_schema NOT IN ('pg_catalog','information_schema')
        ORDER BY 1,2
        """
        for schema, table in fetchall(cur, q):
            (cnt,) = fetchone(cur, f"SELECT COUNT(*) FROM {schema}.{table}")
            print(f"{schema}.{table}: {cnt}")


if __name__ == "__main__":
    main()


