from database.repository import Repository

repository = Repository(
    table="medical_records",
    primary_key="medical_record_id",
    fields=("patient_id", "appointment_id", "doctor_id", "medical_history", "diagnosis", "notes"),
    form_fields=(
        ("patient_id", "Patient", True, "lookup"),
        ("appointment_id", "Appointment ID", True, "lookup"),
        ("doctor_id", "Doctor", True, "lookup"),
        ("medical_history", "Medical history", False, "text"),
        ("diagnosis", "Diagnosis", True, "text"),
        ("notes", "Clinical notes", False, "text"),
    ),
    headers=(("medical_record_id", "ID"), ("patient", "Patient"), ("appointment_id", "Appointment"),
             ("doctor", "Doctor"), ("diagnosis", "Diagnosis"), ("created_at", "Recorded")),
    list_sql="""SELECT m.medical_record_id, p.full_name AS patient, m.appointment_id,
                       d.full_name AS doctor, m.diagnosis, m.created_at
                FROM medical_records m
                JOIN patients p ON p.patient_id = m.patient_id
                JOIN doctors d ON d.doctor_id = m.doctor_id
                ORDER BY m.created_at DESC""",
    lookups={"patient_id": ("patients", "patient_id", "full_name"),
             "appointment_id": ("appointments", "appointment_id", "appointment_id"),
             "doctor_id": ("doctors", "doctor_id", "full_name")},
    actor_column="created_by",
    patient_list_sql="""SELECT m.medical_record_id, m.appointment_id, d.full_name AS doctor,
                               m.medical_history, m.diagnosis, m.notes, m.created_at
                        FROM medical_records m JOIN doctors d ON d.doctor_id = m.doctor_id
                        WHERE m.patient_id = %s ORDER BY m.created_at DESC""",
)
