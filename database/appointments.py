from database.repository import Repository

repository = Repository(
    table="appointments",
    primary_key="appointment_id",
    fields=("patient_id", "doctor_id", "appointment_date", "appointment_time", "status", "reason"),
    form_fields=(
        ("patient_id", "Patient", True, "lookup"),
        ("doctor_id", "Doctor", True, "lookup"),
        ("appointment_date", "Date (YYYY-MM-DD)", True, "date"),
        ("appointment_time", "Time (HH:MM)", True, "time"),
        ("status", "Status", True, "choice"),
        ("reason", "Reason", False, "text"),
    ),
    headers=(("appointment_id", "ID"), ("patient", "Patient"), ("doctor", "Doctor"),
             ("appointment_date", "Date"), ("appointment_time", "Time"), ("status", "Status"),
             ("reason", "Reason")),
    list_sql="""SELECT a.appointment_id, p.full_name AS patient, d.full_name AS doctor,
                       a.appointment_date, a.appointment_time, a.status, a.reason
                FROM appointments a
                JOIN patients p ON p.patient_id = a.patient_id
                JOIN doctors d ON d.doctor_id = a.doctor_id
                ORDER BY a.appointment_date DESC, a.appointment_time""",
    lookups={"patient_id": ("patients", "patient_id", "full_name"),
             "doctor_id": ("doctors", "doctor_id", "full_name")},
    actor_column="created_by",
    options={"status": ("Scheduled", "Completed", "Cancelled", "No-show")},
    patient_list_sql="""SELECT a.appointment_id, d.full_name AS doctor, a.appointment_date,
                               a.appointment_time, a.status, a.reason
                        FROM appointments a JOIN doctors d ON d.doctor_id = a.doctor_id
                        WHERE a.patient_id = %s
                        ORDER BY a.appointment_date DESC, a.appointment_time""",
)
