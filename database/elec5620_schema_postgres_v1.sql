
-- ELEC5620 Healthcare/Insurance Platform - Relational Schema (PostgreSQL)
-- Generated: 2025-10-28 (Australia/Sydney)
-- Notes:
-- * Implements composition/associations from the provided class diagram.
-- * Uses separate subtype tables for Doctor and Patient that reference Users.
-- * Adds reasonable constraints, indexes, and enum types.
-- * Time columns default to NOW() where appropriate.

-- =====================
-- ENUM TYPES
-- =====================
CREATE TYPE gender AS ENUM ('Male','Female','Other','PreferNot');
CREATE TYPE user_status AS ENUM ('Active','Locked','Disabled');
CREATE TYPE doctor_availability AS ENUM ('Available','Busy','Offline');
CREATE TYPE employment_status AS ENUM ('Employed','SelfEmployed','Student','Unemployed');
CREATE TYPE request_status AS ENUM ('Draft','Submitted','InReview','Completed','Failed');
CREATE TYPE recommendation_strategy AS ENUM ('Rules','ML','Hybrid');
CREATE TYPE recommendation_status AS ENUM ('Active','Paused');
CREATE TYPE appointment_status AS ENUM ('Requested','Approved','Cancelled','Completed','Rescheduled');
CREATE TYPE appointment_type AS ENUM ('Consult','FollowUp','Telehealth','InPerson','Emergency','Other');
CREATE TYPE job_kind AS ENUM ('OCR','IE','EXPLAIN','SAFETY');
CREATE TYPE job_status AS ENUM ('Queued','Running','Succeeded','Failed');
CREATE TYPE medical_record_status AS ENUM ('Uploaded','Processed','Explained','Checked','Archived');
CREATE TYPE safety_flag_type AS ENUM ('Contraindication','Emergency','Allergy','Interaction');
CREATE TYPE safety_severity AS ENUM ('Low','Medium','High');

-- Review & Approval
CREATE TYPE approval_decision AS ENUM ('Approved','Rejected','NeedsChanges');

-- =====================
-- CORE ACTORS
-- =====================
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    email           CITEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    username        CITEXT UNIQUE NOT NULL,
    gender          gender NOT NULL DEFAULT 'PreferNot',
    status          user_status NOT NULL DEFAULT 'Active',
    mfa_enabled     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Patients and Doctors specialize Users
CREATE TABLE patients (
    user_id             BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    assigned_doctor_id  BIGINT REFERENCES users(id) ON DELETE SET NULL, -- refers to a doctor user
    consent_on_ai       BOOLEAN NOT NULL DEFAULT FALSE,
    consent_timestamp   TIMESTAMPTZ
);

CREATE INDEX idx_patients_assigned_doctor ON patients(assigned_doctor_id);

CREATE TABLE doctors (
    user_id             BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    specialization      TEXT,
    license_number      TEXT,
    ahpra_number        TEXT,              -- AHPRA Provider/Registration Number
    qualification       TEXT,
    clinic_address      TEXT,
    digital_signature_ref TEXT,
    availability_status doctor_availability NOT NULL DEFAULT 'Offline',
    approval_status     TEXT NOT NULL DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
    approval_notes      TEXT,              -- Admin notes when approving/rejecting
    approved_by          BIGINT REFERENCES users(id) ON DELETE SET NULL, -- Admin who approved/rejected
    approved_at          TIMESTAMPTZ,       -- When approval/rejection happened
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================
-- INSURANCE PRODUCTS & QUOTES
-- =====================
CREATE TABLE insurance_products (
    id                  BIGSERIAL PRIMARY KEY,
    name                TEXT NOT NULL,
    provider            TEXT NOT NULL,
    product_link        TEXT,            -- URL to the provider's website (e.g., https://www.bupa.com.au)
    insurance_type      TEXT,
    -- legacy/basic fields
    coverage            TEXT,
    premium             NUMERIC(12,2) CHECK (premium IS NULL OR premium >= 0),
    -- model-aligned fields (nullable for backward compatibility)
    plan_type           TEXT,
    monthly_premium     NUMERIC(12,2) CHECK (monthly_premium IS NULL OR monthly_premium >= 0),
    coverage_amount     NUMERIC(14,2) CHECK (coverage_amount IS NULL OR coverage_amount >= 0),
    annual_deductible   NUMERIC(12,2) CHECK (annual_deductible IS NULL OR annual_deductible >= 0),
    copay               NUMERIC(12,2) CHECK (copay IS NULL OR copay >= 0),
    coinsurance         NUMERIC(12,2) CHECK (coinsurance IS NULL OR coinsurance >= 0),
    max_out_of_pocket   NUMERIC(12,2) CHECK (max_out_of_pocket IS NULL OR max_out_of_pocket >= 0),
    coverage_details    JSONB,
    exclusions          JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE quotes (
    id                   BIGSERIAL PRIMARY KEY,
    suitability_score    INT NOT NULL CHECK (suitability_score BETWEEN 0 AND 100),
    -- legacy numeric cost; may be NULL if score-based is used only
    cost                 NUMERIC(12,2) CHECK (cost IS NULL OR cost >= 0),
    -- model-aligned score fields
    cost_score           INT CHECK (cost_score IS NULL OR (cost_score BETWEEN 0 AND 100)),
    coverage_score       INT CHECK (coverage_score IS NULL OR (coverage_score BETWEEN 0 AND 100)),
    overall_score        INT CHECK (overall_score IS NULL OR (overall_score BETWEEN 0 AND 100)),
    coverage_summary     TEXT,
    rationale            TEXT,
    insurance_product_id BIGINT NOT NULL REFERENCES insurance_products(id) ON DELETE RESTRICT,
    patient_id           BIGINT NOT NULL REFERENCES patients(user_id) ON DELETE CASCADE,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_quotes_patient ON quotes(patient_id);
CREATE INDEX idx_quotes_product ON quotes(insurance_product_id);

CREATE TABLE policy_holds (
    id                  BIGSERIAL PRIMARY KEY,
    insurance_product_id BIGINT NOT NULL REFERENCES insurance_products(id) ON DELETE RESTRICT,
    patient_id          BIGINT NOT NULL REFERENCES patients(user_id) ON DELETE CASCADE,
    start_date          DATE NOT NULL,
    end_date            DATE,
    CHECK (end_date IS NULL OR end_date >= start_date),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (insurance_product_id, patient_id, start_date)
);

-- =====================
-- CLINICAL DATA
-- =====================
CREATE TABLE health_data (
    id              BIGSERIAL PRIMARY KEY,
    patient_id      BIGINT NOT NULL REFERENCES patients(user_id) ON DELETE CASCADE,
    weight_kg       NUMERIC(6,2),    -- allows up to 9999.99 if needed
    height_cm       NUMERIC(6,2),
    bp_systolic     INT,
    bp_diastolic    INT,
    smoking_status  TEXT,            -- 'Never', 'Former', 'Current', 'Smoker', etc.
    alcohol_consumption TEXT,        -- 'None', 'Rarely', 'Occasionally', 'Regularly', etc.
    measure_date    DATE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_health_data_patient_date ON health_data(patient_id, measure_date DESC);

CREATE TABLE medical_histories (
    id              BIGSERIAL PRIMARY KEY,
    patient_id      BIGINT NOT NULL REFERENCES patients(user_id) ON DELETE CASCADE,
    surgeries       TEXT,
    medication      TEXT,
    past_illness    TEXT,
    last_updated    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================
-- SOCIO-ECONOMIC DATA
-- =====================
CREATE TABLE income_details (
    id                  BIGSERIAL PRIMARY KEY,
    patient_id          BIGINT NOT NULL REFERENCES patients(user_id) ON DELETE CASCADE,
    annual_income       NUMERIC(12,2) CHECK (annual_income >= 0),
    employment_status   employment_status,
    dependents          INT CHECK (dependents >= 0),
    effective_date      DATE NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_income_details_patient_date ON income_details(patient_id, effective_date DESC);

-- =====================
-- QUOTE REQUEST PIPELINE
-- =====================
CREATE TABLE quote_requests (
    id                  BIGSERIAL PRIMARY KEY,             -- requestId
    request_time        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_input          TEXT,
    patient_id          BIGINT NOT NULL REFERENCES patients(user_id) ON DELETE CASCADE,
    medical_history_id  BIGINT REFERENCES medical_histories(id) ON DELETE SET NULL,
    income_detail_id    BIGINT REFERENCES income_details(id) ON DELETE SET NULL,
    processing_status   request_status NOT NULL DEFAULT 'Draft',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- A request may point to many health_data entries
CREATE TABLE quote_request_health_data (
    quote_request_id BIGINT NOT NULL REFERENCES quote_requests(id) ON DELETE CASCADE,
    health_data_id   BIGINT NOT NULL REFERENCES health_data(id) ON DELETE CASCADE,
    PRIMARY KEY (quote_request_id, health_data_id)
);

-- =====================
-- AI AGENTS
-- =====================
CREATE TABLE ai_agents (
    id              BIGSERIAL PRIMARY KEY,
    agent_name      TEXT NOT NULL,
    api_key         TEXT,
    api_address     TEXT,
    model_version   TEXT,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================
-- RECOMMENDATION ENGINE
-- =====================
CREATE TABLE recommendation_controllers (
    id              BIGSERIAL PRIMARY KEY,
    strategy        recommendation_strategy NOT NULL,
    version         TEXT,
    status          recommendation_status NOT NULL DEFAULT 'Active',
    last_run_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE quote_recommendations (
    id                  BIGSERIAL PRIMARY KEY,
    recommendation_controller_id BIGINT NOT NULL REFERENCES recommendation_controllers(id) ON DELETE CASCADE,
    quote_id            BIGINT NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
    patient_id          BIGINT REFERENCES patients(user_id) ON DELETE CASCADE,
    quote_request_id    BIGINT REFERENCES quote_requests(id) ON DELETE CASCADE,
    rank                INT NOT NULL CHECK (rank >= 1),
    suitability_score   INT CHECK (suitability_score BETWEEN 0 AND 100),
    rationale           TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (recommendation_controller_id, quote_id),
    UNIQUE (recommendation_controller_id, quote_request_id, rank)
);

CREATE INDEX idx_qrec_patient ON quote_recommendations(patient_id);
CREATE INDEX idx_qrec_request ON quote_recommendations(quote_request_id);

-- =====================
-- APPOINTMENTS
-- =====================
CREATE TABLE appointments (
    id              BIGSERIAL PRIMARY KEY,
    doctor_id       BIGINT NOT NULL REFERENCES doctors(user_id) ON DELETE CASCADE,
    patient_id      BIGINT NOT NULL REFERENCES patients(user_id) ON DELETE CASCADE,
    appointment_at  TIMESTAMPTZ NOT NULL,
    status          appointment_status NOT NULL DEFAULT 'Requested',
    type            appointment_type NOT NULL DEFAULT 'Consult',
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_appts_doc_time ON appointments(doctor_id, appointment_at DESC);
CREATE INDEX idx_appts_patient_time ON appointments(patient_id, appointment_at DESC);

-- =====================
-- MEDICAL RECORD INGESTION & EXPLANATION
-- =====================
CREATE TABLE medical_records (
    id              BIGSERIAL PRIMARY KEY,
    file_hash       TEXT UNIQUE,
    patient_id      BIGINT NOT NULL REFERENCES patients(user_id) ON DELETE CASCADE,
    pages           INT CHECK (pages >= 0),
    size_mb         NUMERIC(10,3) CHECK (size_mb >= 0),
    document_type   TEXT,  -- 'medical_report', 'lab_results', 'imaging_report', 'prescription', 'discharge_summary', 'pathology', 'consultation', 'other'
    file_path       TEXT,  -- Path to the uploaded file (relative to uploads folder, organized by user_id_analysis_id)
    original_filename TEXT,  -- Original filename when uploaded
    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status          medical_record_status NOT NULL DEFAULT 'Uploaded'
);

CREATE TABLE fhir_bundles (
    id              BIGSERIAL PRIMARY KEY,
    medical_record_id BIGINT NOT NULL REFERENCES medical_records(id) ON DELETE CASCADE,
    json            TEXT NOT NULL,
    valid           BOOLEAN NOT NULL DEFAULT FALSE,
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fhir_record ON fhir_bundles(medical_record_id);

CREATE TABLE explanations (
    id              BIGSERIAL PRIMARY KEY,
    medical_record_id BIGINT NOT NULL REFERENCES medical_records(id) ON DELETE CASCADE,
    summary_md      TEXT,
    pathway_md      TEXT,
    risks_md        TEXT,
    mistral_analysis TEXT,  -- AI analysis from mistral:7b-instruct LLM
    low_confidence  BOOLEAN NOT NULL DEFAULT FALSE,
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_expl_record ON explanations(medical_record_id);

CREATE TABLE safety_flags (
    id              BIGSERIAL PRIMARY KEY,
    medical_record_id BIGINT REFERENCES medical_records(id) ON DELETE CASCADE,
    explanation_id  BIGINT REFERENCES explanations(id) ON DELETE CASCADE,
    type            safety_flag_type NOT NULL,
    severity        safety_severity NOT NULL,
    details         TEXT,
    evidence        TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sflag_record ON safety_flags(medical_record_id);
CREATE INDEX idx_sflag_expl ON safety_flags(explanation_id);

CREATE TABLE processing_jobs (
    id              BIGSERIAL PRIMARY KEY,
    medical_record_id BIGINT REFERENCES medical_records(id) ON DELETE CASCADE,
    kind            job_kind NOT NULL,
    status          job_status NOT NULL DEFAULT 'Queued',
    latency_ms      INT CHECK (latency_ms IS NULL OR latency_ms >= 0),
    error_code      TEXT,
    started_at      TIMESTAMPTZ,
    finished_at     TIMESTAMPTZ,
    pipeline_version TEXT
);

CREATE INDEX idx_jobs_record ON processing_jobs(medical_record_id);
CREATE INDEX idx_jobs_status ON processing_jobs(status);

-- =====================
-- AI OUTPUT APPROVALS (UC‑05)
-- =====================
CREATE TABLE ai_approvals (
    id              BIGSERIAL PRIMARY KEY,
    medical_record_id BIGINT NOT NULL REFERENCES medical_records(id) ON DELETE CASCADE,
    explanation_id  BIGINT REFERENCES explanations(id) ON DELETE SET NULL,
    doctor_id       BIGINT NOT NULL REFERENCES doctors(user_id) ON DELETE CASCADE,
    decision        approval_decision NOT NULL,
    notes           TEXT,
    signature_ref   TEXT,              -- points to doctors.digital_signature_ref or external vault
    pipeline_version TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    signed_at       TIMESTAMPTZ
);

CREATE INDEX idx_ai_approvals_record ON ai_approvals(medical_record_id);
CREATE INDEX idx_ai_approvals_doctor ON ai_approvals(doctor_id);

-- =====================
-- AUDIT
-- =====================
CREATE TABLE audit_logs (
    id              BIGSERIAL PRIMARY KEY,
    actor_user_id   BIGINT REFERENCES users(id) ON DELETE SET NULL,
    action          TEXT NOT NULL, -- e.g., Upload, Process, Approve, Export...
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    object_type     TEXT NOT NULL,
    object_id       TEXT NOT NULL,
    details_hash    TEXT,
    pipeline_version TEXT
);

CREATE INDEX idx_audit_actor_time ON audit_logs(actor_user_id, timestamp DESC);
CREATE INDEX idx_audit_object ON audit_logs(object_type, object_id);

-- =====================
-- HOUSEKEEPING: updated_at triggers (optional)
-- =====================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_appts_updated
BEFORE UPDATE ON appointments
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
