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
    # Apply/Migrate schema (optional)
    # =============================
    def migrate_schema(cur, connection):
        print("\n🛠  Migrating schema for approvals and enums (idempotent)...")
        # Ensure we're not inside a transaction before changing autocommit
        try:
            connection.commit()
        except Exception:
            try:
                connection.rollback()
            except Exception:
                pass
        connection.set_session(autocommit=True)
        # 1) Create approval_decision enum if missing
        cur.execute(
            """
            DO $$
            BEGIN
              IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'approval_decision') THEN
                CREATE TYPE approval_decision AS ENUM ('Approved','Rejected','NeedsChanges');
              END IF;
            END$$;
            """
        )
        # 2) Add InPerson to appointment_type if missing
        cur.execute(
            """
            DO $$
            BEGIN
              IF NOT EXISTS (
                SELECT 1 FROM pg_enum e JOIN pg_type t ON t.oid = e.enumtypid
                WHERE t.typname = 'appointment_type' AND e.enumlabel = 'InPerson') THEN
                ALTER TYPE appointment_type ADD VALUE 'InPerson';
              END IF;
            END$$;
            """
        )
        # 3) Create ai_approvals table if not exists
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_approvals (
              id BIGSERIAL PRIMARY KEY,
              medical_record_id BIGINT NOT NULL REFERENCES medical_records(id) ON DELETE CASCADE,
              explanation_id BIGINT REFERENCES explanations(id) ON DELETE SET NULL,
              doctor_id BIGINT NOT NULL REFERENCES doctors(user_id) ON DELETE CASCADE,
              decision approval_decision NOT NULL,
              notes TEXT,
              signature_ref TEXT,
              pipeline_version TEXT,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              signed_at TIMESTAMPTZ
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ai_approvals_record ON ai_approvals(medical_record_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ai_approvals_doctor ON ai_approvals(doctor_id);")
        # ---- Align insurance_products with web_app insurance_models.py ----
        def ensure_col(table, column, type_sql):
            cur.execute(
                f"""
                DO $$
                BEGIN
                  IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = '{table}' AND column_name = '{column}'
                  ) THEN
                    EXECUTE 'ALTER TABLE {table} ADD COLUMN {column} {type_sql}';
                  END IF;
                END$$;
                """
            )
        print("   • Ensuring insurance_products extended columns…")
        ensure_col('insurance_products','plan_type','TEXT')
        ensure_col('insurance_products','monthly_premium','NUMERIC(12,2)')
        ensure_col('insurance_products','coverage_amount','NUMERIC(14,2)')
        ensure_col('insurance_products','annual_deductible','NUMERIC(12,2)')
        ensure_col('insurance_products','copay','NUMERIC(12,2)')
        ensure_col('insurance_products','coinsurance','NUMERIC(12,2)')
        ensure_col('insurance_products','max_out_of_pocket','NUMERIC(12,2)')
        ensure_col('insurance_products','coverage_details','JSONB')
        ensure_col('insurance_products','exclusions','JSONB')
        print("   • Ensuring quotes score columns…")
        ensure_col('quotes','cost_score','INT')
        ensure_col('quotes','coverage_score','INT')
        ensure_col('quotes','overall_score','INT')
        ensure_col('quotes','rationale','TEXT')
        print("   • Ensuring health_data lifestyle columns…")
        ensure_col('health_data','smoking_status','TEXT')
        ensure_col('health_data','alcohol_consumption','TEXT')
        print("   • Ensuring explanations mistral_analysis column…")
        ensure_col('explanations','mistral_analysis','TEXT')
        print("   • Ensuring doctors approval columns…")
        ensure_col('doctors','ahpra_number','TEXT')
        ensure_col('doctors','approval_status','TEXT')
        ensure_col('doctors','approval_notes','TEXT')
        ensure_col('doctors','approved_by','BIGINT')
        ensure_col('doctors','approved_at','TIMESTAMPTZ')
        ensure_col('doctors','created_at','TIMESTAMPTZ')
        
        print("   • Ensuring medical_records document_type column…")
        ensure_col('medical_records','document_type','TEXT')
        print("   • Ensuring medical_records file_path and original_filename columns…")
        ensure_col('medical_records','file_path','TEXT')
        ensure_col('medical_records','original_filename','TEXT')
        # Set default approval_status for existing doctors
        connection.set_session(autocommit=True)
        try:
            cur.execute("""
                UPDATE doctors 
                SET approval_status = 'Approved' 
                WHERE approval_status IS NULL OR approval_status = ''
            """)
        except Exception:
            pass
        connection.set_session(autocommit=False)
        
        # Update existing products with provider URLs
        print("   • Updating provider URLs in insurance_products…")
        provider_urls = {
            "Bupa Australia": "https://www.bupa.com.au",
            "Medibank Private": "https://www.medibank.com.au",
            "ahm (by Medibank)": "https://www.ahm.com.au",
            "HCF": "https://www.hcf.com.au",
            "nib Health Funds": "https://www.nib.com.au",
            "HBF Health": "https://www.hbf.com.au",
            "Australian Unity Health": "https://www.australianunity.com.au/health-insurance",
            "GMHBA Health Insurance": "https://www.gmhba.com.au",
            "Health Partners": "https://www.healthpartners.com.au",
            "HIF": "https://www.hif.com.au",
            "St Lukes Health": "https://www.stlukes.com.au",
            "Latrobe Health Services": "https://www.latrobehealth.com.au",
            "Westfund Health Insurance": "https://www.westfund.com.au",
            "Phoenix Health Fund": "https://www.phoenixhealthfund.com.au",
            "AIA Health Insurance": "https://www.aiahealth.com.au",
            "MyOwn Health Insurance": "https://www.myownhealth.com.au",
            "Health Care Insurance (HCI)": "https://www.hciltd.com.au",
            "Queensland Country Health": "https://www.qldcountry.health",
            "Mildura Health Fund": "https://www.mildurahealthfund.com.au",
            "National Health Benefits Australia (onemedifund)": "https://www.onemedifund.com.au",
            "Defence Health": "https://www.defencehealth.com.au",
            "Police Health": "https://www.policehealth.com.au",
            "Teachers Health": "https://www.teachershealth.com.au",
            "Navy Health": "https://www.navyhealth.com.au",
            "Doctors' Health Fund": "https://www.doctorshealthfund.com.au",
            "CBHS Health Fund": "https://www.cbhs.com.au",
            "Reserve Bank Health Society": "https://www.rbhs.com.au",
            "ACA Health Benefits Fund": "https://www.acahealth.com.au",
            "RT Health Fund": "https://www.rthealth.com.au",
            "Transport Health / Union Health": "https://www.unionhealth.com.au",
        }
        connection.set_session(autocommit=True)
        updated_count = 0
        for provider_name, url in provider_urls.items():
            try:
                cur.execute(
                    """
                    UPDATE insurance_products
                    SET product_link = %s
                    WHERE provider = %s AND (product_link IS NULL OR product_link = '')
                    """,
                    (url, provider_name),
                )
                if cur.rowcount > 0:
                    updated_count += cur.rowcount
            except Exception as e:
                print(f"      Warning: Could not update {provider_name}: {e}")
        connection.set_session(autocommit=False)
        if updated_count > 0:
            print(f"      Updated {updated_count} products with provider URLs")
        else:
            print("      No products needed URL updates")
        
        print("✅ Migration complete")

    if os.environ.get("APPLY_PROJECT_SCHEMA", "false").lower() in {"1","true","yes"}:
        print("\n📦 Applying project schema (elec5620_schema_postgres_v1.sql)...")
        try:
            conn.commit()
        except Exception:
            pass
        conn.autocommit = True
        cursor.execute("CREATE EXTENSION IF NOT EXISTS citext;")
        schema_path = os.path.join(os.path.dirname(__file__), "elec5620_schema_postgres_v1.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        try:
            cursor.execute(schema_sql)
            print("✅ Base schema applied")
        except Exception as schema_err:
            print("⚠️  Base schema error (continuing with migration):", schema_err)
        migrate_schema(cursor, conn)
    elif os.environ.get("MIGRATE_SCHEMA", "true").lower() in {"1","true","yes"}:
        migrate_schema(cursor, conn)

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
            INSERT INTO insurance_products(
              name, provider, product_link, insurance_type,
              coverage, premium,
              plan_type, monthly_premium, coverage_amount, annual_deductible,
              copay, coinsurance, max_out_of_pocket, coverage_details, exclusions
            )
            VALUES (
              'Basic Health Cover','MediCo','https://example.com/plan/basic','Health',
              'General health cover', 99.90,
              'HMO', 99.90, 150000, 3000,
              25, 30, 7500, '["Hospitalization","Outpatient","Drugs"]'::jsonb, '["Cosmetic procedures"]'::jsonb
            )
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
                INSERT INTO quotes(
                  suitability_score, cost, cost_score, coverage_score, overall_score,
                  coverage_summary, rationale, insurance_product_id, patient_id
                )
                VALUES (75, 89.50, 80, 70, 75,
                        'Standard cover with extras', 'Baseline rules suggest suitability', %s, %s)
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

        # Persist inserts
        try:
            conn.commit()
        except Exception:
            conn.rollback()
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
