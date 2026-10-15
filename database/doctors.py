from database.repository import Repository

repository = Repository(
    table="doctors",
    primary_key="doctor_id",
    fields=("full_name", "role", "specialty", "phone_number", "email", "active"),
    form_fields=(
        ("full_name", "Full name", True, "text"),
        ("role", "Role", True, "text"),
        ("specialty", "Specialty", True, "text"),
        ("phone_number", "Phone number", False, "text"),
        ("email", "Email", False, "text"),
        ("active", "Active", True, "boolean"),
    ),
    headers=(("doctor_id", "ID"), ("full_name", "Doctor"), ("role", "Role"), ("specialty", "Specialty"),
             ("phone_number", "Phone"), ("email", "Email"), ("active", "Active")),
    list_sql="""SELECT doctor_id, full_name, role, specialty, phone_number, email, active
                FROM doctors ORDER BY full_name""",
)
