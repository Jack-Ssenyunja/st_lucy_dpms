from database.repository import Repository

repository = Repository(
    table="patients",
    primary_key="patient_id",
    fields=("full_name", "date_of_birth", "gender", "phone_number", "email"),
    form_fields=(
        ("full_name", "Full name", True, "text"),
        ("date_of_birth", "Date of birth (YYYY-MM-DD)", True, "date"),
        ("gender", "Gender", True, "choice"),
        ("phone_number", "Phone number", True, "text"),
        ("email", "Email", False, "text"),
    ),
    headers=(("patient_id", "ID"), ("full_name", "Patient"), ("date_of_birth", "Date of birth"),
             ("gender", "Gender"), ("phone_number", "Phone"), ("email", "Email")),
    list_sql="""SELECT patient_id, full_name, date_of_birth, gender, phone_number, email
                FROM patients ORDER BY full_name""",
    options={"gender": ("Female", "Male", "Other", "Prefer not to say")},
)
