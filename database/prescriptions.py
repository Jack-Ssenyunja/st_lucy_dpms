from database.repository import Repository

repository = Repository(
    table="prescriptions",
    primary_key="prescription_id",
    fields=("medical_record_id", "medication", "dosage", "instructions", "start_date", "end_date"),
    form_fields=(
        ("medical_record_id", "Medical record ID", True, "lookup"),
        ("medication", "Medication", True, "text"),
        ("dosage", "Dosage", True, "text"),
        ("instructions", "Instructions", False, "text"),
        ("start_date", "Start date (YYYY-MM-DD)", True, "date"),
        ("end_date", "End date (YYYY-MM-DD)", False, "date"),
    ),
    headers=(("prescription_id", "ID"), ("medical_record_id", "Record"), ("medication", "Medication"),
             ("dosage", "Dosage"), ("instructions", "Instructions"), ("start_date", "Start"),
             ("end_date", "End")),
    list_sql="""SELECT prescription_id, medical_record_id, medication, dosage, instructions,
                       start_date, end_date FROM prescriptions ORDER BY prescription_id DESC""",
    lookups={"medical_record_id": ("medical_records", "medical_record_id", "medical_record_id")},
)
