import os
import psycopg2

# Connection parameters
host = "elec5620-as02-database.c38ki6o4abha.ap-southeast-2.rds.amazonaws.com"
port = "5432"
database = "postgres"  # change if you have another database name
user = "postgres"
password = "ghR4BwyqbEM1xhmrCKbM"

try:
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )

    # Create a cursor object
    cursor = conn.cursor()
    print("✅ Connected successfully!")

    # Show database version
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print("Database version:", db_version)

    # List all non-system tables across schemas
    cursor.execute(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN ('pg_catalog','information_schema')
        ORDER BY table_schema, table_name;
        """
    )
    rows = cursor.fetchall()
    if rows:
        print("\n=== Tables in database ===")
        for schema, table in rows:
            print(f"{schema}.{table}")
        print(f"\nTotal tables: {len(rows)}")
    else:
        print("\n(No user tables found)")

    # Also output row counts for a quick check
    if rows:
        print("\n=== Table row counts ===")
        for schema, table in rows:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
                count = cursor.fetchone()[0]
                print(f"{schema}.{table}: {count}")
            except Exception as e:
                print(f"{schema}.{table}: (count failed) {e}")

    # =============================
    # Apply project schema (optional)
    # =============================
    should_apply_schema = os.environ.get("APPLY_PROJECT_SCHEMA", "false").lower() in {"1","true","yes"}
    if should_apply_schema:
        print("\n📦 Applying project schema (elec5620_schema_postgres_v1.sql)...")
        # Ensure no transaction is open before switching autocommit
        try:
            conn.commit()
        except Exception:
            pass
        # Ensure citext is available for CITEXT columns
        conn.autocommit = True
        cursor.execute("CREATE EXTENSION IF NOT EXISTS citext;")

        schema_path = os.path.join(
            os.path.dirname(__file__),
            "elec5620_schema_postgres_v1.sql",
        )
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        try:
            cursor.execute(schema_sql)
            print("✅ Schema applied")
        except Exception as schema_err:
            print("⚠️  Schema apply error:", schema_err)

        # Refresh table list
        cursor.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_type='BASE TABLE'
              AND table_schema NOT IN ('pg_catalog','information_schema')
            ORDER BY table_schema, table_name;
            """
        )
        rows = cursor.fetchall()
        print("\n=== Tables after schema ===")
        for schema, table in rows:
            print(f"{schema}.{table}")

        # -----------------------------
        # Insert minimal mock data
        # -----------------------------
        print("\n🧪 Inserting mock data (idempotent)...")
        def insert_one(sql, params=None):
            cursor.execute(sql, params or ())
            try:
                return cursor.fetchone()[0]
            except Exception:
                return None

        # Users (doctor + patient)
        user_doctor_id = insert_one(
            """
            INSERT INTO users(name, email, password_hash, username)
            VALUES ('Dr. Alice Smith','dr.alice@example.com','x','dr.alice')
            ON CONFLICT (username) DO UPDATE SET name=EXCLUDED.name
            RETURNING id;
            """
        )
        user_patient_id = insert_one(
            """
            INSERT INTO users(name, email, password_hash, username)
            VALUES ('John Doe','john.doe@example.com','x','john.doe')
            ON CONFLICT (username) DO UPDATE SET name=EXCLUDED.name
            RETURNING id;
            """
        )

        # Doctors / Patients subtype rows
        if user_doctor_id:
            cursor.execute(
                """
                INSERT INTO doctors(user_id, specialization, license_number, qualification, availability_status)
                VALUES (%s, 'Cardiology', 'LIC-ALICE-001', 'MBBS, FRACP', 'Available')
                ON CONFLICT (user_id) DO NOTHING;
                """,
                (user_doctor_id,),
            )
        if user_patient_id:
            cursor.execute(
                """
                INSERT INTO patients(user_id, assigned_doctor_id, consent_on_ai, consent_timestamp)
                VALUES (%s, %s, TRUE, NOW())
                ON CONFLICT (user_id) DO NOTHING;
                """,
                (user_patient_id, user_doctor_id),
            )

        # Insurance product
        product_id = insert_one(
            """
            INSERT INTO insurance_products(name, coverage, premium, provider, product_link, insurance_type)
            VALUES ('Basic Health Cover','General health cover', 99.90, 'MediCo', 'https://example.com/plan/basic', 'Health')
            ON CONFLICT DO NOTHING
            RETURNING id;
            """
        )

        # Health data
        if user_patient_id:
            cursor.execute(
                """
                INSERT INTO health_data(patient_id, weight_kg, height_cm, bp_systolic, bp_diastolic, measure_date)
                VALUES (%s, 82.5, 178.0, 120, 80, CURRENT_DATE)
                ON CONFLICT DO NOTHING;
                """,
                (user_patient_id,),
            )

        # Quote + recommendation minimal flow (quote references product + patient)
        if product_id and user_patient_id:
            quote_id = insert_one(
                """
                INSERT INTO quotes(suitability_score, cost, coverage_summary, insurance_product_id, patient_id)
                VALUES (75, 89.50, 'Standard cover with extras', %s, %s)
                RETURNING id;
                """,
                (product_id, user_patient_id),
            )
            if quote_id:
                controller_id = insert_one(
                    """
                    INSERT INTO recommendation_controllers(strategy, version)
                    VALUES ('Rules','v1')
                    RETURNING id;
                    """
                )
                if controller_id:
                    cursor.execute(
                        """
                        INSERT INTO quote_recommendations(recommendation_controller_id, quote_id, patient_id, rank, suitability_score, rationale)
                        VALUES (%s, %s, %s, 1, 80, 'Baseline rules suggest suitability')
                        ON CONFLICT DO NOTHING;
                        """,
                        (controller_id, quote_id, user_patient_id),
                    )

        # Return to regular commit mode and persist inserts
        conn.autocommit = False
        conn.commit()
        print("✅ Mock data inserted")

        # Sample queries to verify
        print("\n🔎 Sample rows:")
        for label, sql in [
            ("users", "SELECT id, username, email FROM users ORDER BY id LIMIT 5"),
            ("patients", "SELECT user_id, assigned_doctor_id FROM patients LIMIT 5"),
            ("doctors", "SELECT user_id, specialization FROM doctors LIMIT 5"),
            ("insurance_products", "SELECT id, name, premium FROM insurance_products LIMIT 5"),
            ("quotes", "SELECT id, patient_id, insurance_product_id, cost FROM quotes LIMIT 5"),
        ]:
            try:
                cursor.execute(sql)
                print(f"- {label}:", cursor.fetchall())
            except Exception as e:
                print(f"- {label}: (query failed) {e}")

    # Close connection
    cursor.close()
    conn.close()

except Exception as e:
    print("❌ Error connecting to the database:", e)


# import psycopg2
# import pandas as pd

# # Connection details
# conn = psycopg2.connect(
#     host="elec5620-as02-database.c38ki6o4abha.ap-southeast-2.rds.amazonaws.com",
#     port="5432",
#     database="postgres",  # change this if your database name is different
#     user="postgres",
#     password="ghR4BwyqbEM1xhmrCKbM"
# )

# # Create a cursor
# cur = conn.cursor()

# # Example 1: list all tables in the database
# cur.execute("""
#     SELECT table_schema, table_name
#     FROM information_schema.tables
#     WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
#     ORDER BY table_schema, table_name;
# """)

# tables = cur.fetchall()
# print("=== Tables in database ===")
# for schema, table in tables:
#     print(f"{schema}.{table}")

# # Example 2: run a SELECT query on one table (replace with your table name)
# query = "SELECT * FROM your_table_name LIMIT 10;"  # <-- change table name
# df = pd.read_sql_query(query, conn)
# print("\n=== Sample data ===")
# print(df)

# # Clean up
# cur.close()
# conn.close()
