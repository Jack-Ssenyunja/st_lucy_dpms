CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('administrator', 'doctor', 'receptionist', 'patient')),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_case_insensitive
    ON users(lower(username));

CREATE TABLE IF NOT EXISTS patients (
    patient_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT UNIQUE REFERENCES users(user_id) ON DELETE SET NULL,
    full_name VARCHAR(120) NOT NULL,
    date_of_birth DATE NOT NULL CHECK (date_of_birth <= CURRENT_DATE),
    gender VARCHAR(20) NOT NULL CHECK (gender IN ('Female', 'Male', 'Other', 'Prefer not to say')),
    phone_number VARCHAR(25) NOT NULL,
    email VARCHAR(254),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS doctors (
    doctor_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id BIGINT UNIQUE REFERENCES users(user_id) ON DELETE SET NULL,
    full_name VARCHAR(120) NOT NULL,
    role VARCHAR(100) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    phone_number VARCHAR(25),
    email VARCHAR(254) UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patients(patient_id) ON DELETE RESTRICT,
    doctor_id BIGINT NOT NULL REFERENCES doctors(doctor_id) ON DELETE RESTRICT,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Scheduled'
        CHECK (status IN ('Scheduled', 'Completed', 'Cancelled', 'No-show')),
    reason TEXT NOT NULL DEFAULT '',
    created_by BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medical_records (
    medical_record_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patients(patient_id) ON DELETE RESTRICT,
    appointment_id BIGINT NOT NULL UNIQUE REFERENCES appointments(appointment_id) ON DELETE RESTRICT,
    doctor_id BIGINT NOT NULL REFERENCES doctors(doctor_id) ON DELETE RESTRICT,
    medical_history TEXT NOT NULL DEFAULT '',
    diagnosis TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_by BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    patient_id BIGINT NOT NULL REFERENCES patients(patient_id) ON DELETE RESTRICT,
    service_type VARCHAR(100) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    payment_method VARCHAR(30) NOT NULL
        CHECK (payment_method IN ('Cash', 'Mobile Money', 'Card', 'Insurance', 'Bank Transfer')),
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    receipt_number VARCHAR(40) NOT NULL UNIQUE,
    received_by BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    medical_record_id BIGINT NOT NULL REFERENCES medical_records(medical_record_id) ON DELETE CASCADE,
    medication VARCHAR(160) NOT NULL,
    dosage VARCHAR(120) NOT NULL,
    instructions TEXT NOT NULL DEFAULT '',
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE IF NOT EXISTS learning_resources (
    resource_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(160) NOT NULL UNIQUE,
    category VARCHAR(80) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    url TEXT NOT NULL CHECK (url LIKE 'https://%' OR url LIKE 'http://%'),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_appointments_patient_date
    ON appointments(patient_id, appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_date
    ON appointments(doctor_id, appointment_date);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient
    ON medical_records(patient_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_payments_date
    ON payments(payment_date);

CREATE OR REPLACE FUNCTION validate_appointment_slot()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status <> 'Cancelled' AND EXISTS (
        SELECT 1
        FROM appointments a
        WHERE a.appointment_date = NEW.appointment_date
          AND a.appointment_time = NEW.appointment_time
          AND a.status <> 'Cancelled'
          AND a.appointment_id IS DISTINCT FROM NEW.appointment_id
          AND (a.doctor_id = NEW.doctor_id OR a.patient_id = NEW.patient_id)
    ) THEN
        RAISE EXCEPTION 'This patient or doctor already has an appointment at that date and time';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validate_appointment_slot ON appointments;
CREATE TRIGGER trg_validate_appointment_slot
BEFORE INSERT OR UPDATE ON appointments
FOR EACH ROW EXECUTE FUNCTION validate_appointment_slot();

CREATE OR REPLACE FUNCTION validate_medical_record_links()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM appointments a
        WHERE a.appointment_id = NEW.appointment_id
          AND a.patient_id = NEW.patient_id
          AND a.doctor_id = NEW.doctor_id
    ) THEN
        RAISE EXCEPTION 'Medical record patient and doctor must match its appointment';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_validate_medical_record_links ON medical_records;
CREATE TRIGGER trg_validate_medical_record_links
BEFORE INSERT OR UPDATE ON medical_records
FOR EACH ROW EXECUTE FUNCTION validate_medical_record_links();

CREATE OR REPLACE FUNCTION update_medical_record_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_medical_record_timestamp ON medical_records;
CREATE TRIGGER trg_update_medical_record_timestamp
BEFORE UPDATE ON medical_records
FOR EACH ROW EXECUTE FUNCTION update_medical_record_timestamp();
