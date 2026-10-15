from database.repository import Repository

repository = Repository(
    table="payments",
    primary_key="payment_id",
    fields=("patient_id", "service_type", "amount", "payment_method", "payment_date", "receipt_number"),
    form_fields=(
        ("patient_id", "Patient", True, "lookup"),
        ("service_type", "Service", True, "text"),
        ("amount", "Amount (UGX)", True, "amount"),
        ("payment_method", "Payment method", True, "choice"),
        ("payment_date", "Payment date (YYYY-MM-DD)", True, "date"),
        ("receipt_number", "Receipt number", True, "text"),
    ),
    headers=(("payment_id", "ID"), ("patient", "Patient"), ("service_type", "Service"),
             ("amount", "Amount (UGX)"), ("payment_method", "Method"), ("payment_date", "Date"),
             ("receipt_number", "Receipt")),
    list_sql="""SELECT x.payment_id, p.full_name AS patient, x.service_type, x.amount,
                       x.payment_method, x.payment_date, x.receipt_number
                FROM payments x JOIN patients p ON p.patient_id = x.patient_id
                ORDER BY x.payment_date DESC, x.payment_id DESC""",
    lookups={"patient_id": ("patients", "patient_id", "full_name")},
    actor_column="received_by",
    options={"payment_method": ("Cash", "Mobile Money", "Card", "Insurance", "Bank Transfer")},
)
