from datetime import date, timedelta

from auth import hash_password
from db import get_connection


DEMO_USERS = (
    ("admin", "Admin123!", "administrator"),
    ("receptionist", "Reception123!", "receptionist"),
    ("doctor", "Doctor123!", "doctor"),
)

DOCTORS = (
    ("Dr. Sarah Kiden", "Physician", "General Medicine", "+256700100101", "sarah.kiden@example.test"),
    ("Dr. Joseph Kwomu", "Dentist", "Dentistry", "+256700100102", "joseph.kwomu@example.test"),
    ("Dr. Albert Ahereza", "Physician", "Family Medicine", "+256700100103", "albert.ahereza@example.test"),
)

PATIENTS = (
    ("Mary Natu", "1998-02-12", "Female", "+256770200101", "mary.natu@example.test"),
    ("Peter Ssemanda", "1985-07-30", "Male", "+256770200102", "peter.ssemanda@example.test"),
    ("Amina Nakato", "2001-11-05", "Female", "+256770200103", "amina.nakato@example.test"),
    ("David Kato", "1977-04-21", "Male", "+256770200104", "david.kato@example.test"),
    ("Grace Namusoke", "1993-09-16", "Female", "+256770200105", "grace.namusoke@example.test"),
    ("Isaac Lubega", "1968-01-08", "Male", "+256770200106", "isaac.lubega@example.test"),
    ("Ruth Atim", "2005-06-03", "Female", "+256770200107", "ruth.atim@example.test"),
    ("Michael Ssentongo", "1990-12-27", "Male", "+256770200108", "michael.ssentongo@example.test"),
)

RESOURCES = (
    ("Healthy living", "Wellness", "WHO guidance on healthy diets and everyday wellbeing.", "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"),
    ("Oral health", "Dental care", "Practical information on oral health and prevention.", "https://www.who.int/news-room/fact-sheets/detail/oral-health"),
    ("Malaria prevention", "Prevention", "WHO information about malaria prevention and treatment.", "https://www.who.int/news-room/fact-sheets/detail/malaria"),
    ("HIV information", "Sexual health", "WHO overview of HIV testing, prevention, and care.", "https://www.who.int/news-room/fact-sheets/detail/hiv-aids"),
    ("Physical activity", "Wellness", "WHO recommendations for physical activity and health.", "https://www.who.int/news-room/fact-sheets/detail/physical-activity"),
)


def _one(cursor, sql, params, select_sql, select_params):
    cursor.execute(sql, params)
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(select_sql, select_params)
    return cursor.fetchone()[0]


def seed_demo_data():
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                user_ids = {}
                for username, password, role in DEMO_USERS:
                    user_ids[username] = _one(
                        cur,
                        """INSERT INTO users (username, password_hash, role)
                           VALUES (%s, %s, %s) ON CONFLICT (username) DO NOTHING
                           RETURNING user_id""",
                        (username, hash_password(password), role),
                        "SELECT user_id FROM users WHERE username = %s",
                        (username,),
                    )

                doctor_ids = []
                for full_name, role, specialty, phone, email in DOCTORS:
                    doctor_ids.append(_one(
                        cur,
                        """INSERT INTO doctors (full_name, role, specialty, phone_number, email)
                           VALUES (%s, %s, %s, %s, %s) ON CONFLICT (email) DO NOTHING
                           RETURNING doctor_id""",
                        (full_name, role, specialty, phone, email),
                        "SELECT doctor_id FROM doctors WHERE email = %s",
                        (email,),
                    ))
                cur.execute(
                    """UPDATE doctors SET user_id = %s
                       WHERE doctor_id = %s AND (user_id IS NULL OR user_id = %s)""",
                    (user_ids["doctor"], doctor_ids[0], user_ids["doctor"]),
                )

                patient_ids = []
                for full_name, birth, gender, phone, email in PATIENTS:
                    cur.execute(
                        "SELECT patient_id FROM patients WHERE full_name = %s AND date_of_birth = %s",
                        (full_name, birth),
                    )
                    row = cur.fetchone()
                    if row:
                        patient_ids.append(row[0])
                    else:
                        cur.execute(
                            """INSERT INTO patients (full_name, date_of_birth, gender, phone_number, email)
                               VALUES (%s, %s, %s, %s, %s) RETURNING patient_id""",
                            (full_name, birth, gender, phone, email),
                        )
                        patient_ids.append(cur.fetchone()[0])

                today = date.today()
                appointment_ids = []
                for index in range(8):
                    patient_id = patient_ids[index]
                    doctor_id = doctor_ids[index % len(doctor_ids)]
                    day = today + timedelta(days=index - 3)
                    time_value = f"{9 + index}:00"
                    cur.execute(
                        """SELECT appointment_id FROM appointments
                           WHERE patient_id = %s AND doctor_id = %s
                             AND appointment_date = %s AND appointment_time = %s""",
                        (patient_id, doctor_id, day, time_value),
                    )
                    row = cur.fetchone()
                    if row:
                        appointment_ids.append(row[0])
                    else:
                        status = "Completed" if day < today else "Scheduled"
                        cur.execute(
                            """INSERT INTO appointments
                               (patient_id, doctor_id, appointment_date, appointment_time, status, reason, created_by)
                               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING appointment_id""",
                            (patient_id, doctor_id, day, time_value, status,
                             ("Follow-up consultation", "Dental review", "General check-up")[index % 3],
                             user_ids["receptionist"]),
                        )
                        appointment_ids.append(cur.fetchone()[0])

                record_ids = []
                for index in range(5):
                    appointment_id = appointment_ids[index]
                    patient_id = patient_ids[index]
                    doctor_id = doctor_ids[index % len(doctor_ids)]
                    cur.execute(
                        """INSERT INTO medical_records
                           (patient_id, appointment_id, doctor_id, medical_history, diagnosis, notes, created_by)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)
                           ON CONFLICT (appointment_id) DO NOTHING RETURNING medical_record_id""",
                        (patient_id, appointment_id, doctor_id,
                         "No known allergies recorded." if index % 2 == 0 else "Previous routine check-up.",
                         ("Seasonal allergy", "Dental caries", "Routine review", "Malaria follow-up", "Healthy check-up")[index],
                         "Fictional sample record for coursework.", user_ids["doctor"]),
                    )
                    row = cur.fetchone()
                    if row:
                        record_ids.append(row[0])
                    else:
                        cur.execute("SELECT medical_record_id FROM medical_records WHERE appointment_id = %s", (appointment_id,))
                        record_ids.append(cur.fetchone()[0])

                for index, medical_record_id in enumerate(record_ids[:3]):
                    medication = ("Cetirizine", "Amoxicillin", "Paracetamol")[index]
                    dosage = ("10 mg once daily", "500 mg three times daily", "500 mg as needed")[index]
                    cur.execute(
                        """INSERT INTO prescriptions (medical_record_id, medication, dosage, instructions, start_date)
                           SELECT %s, %s, %s, %s, CURRENT_DATE
                           WHERE NOT EXISTS (
                               SELECT 1 FROM prescriptions
                               WHERE medical_record_id = %s AND medication = %s AND dosage = %s
                           )""",
                        (medical_record_id, medication, dosage,
                         "Sample only. Follow the treating clinician's direction.",
                         medical_record_id, medication, dosage),
                    )

                for index in range(5):
                    cur.execute(
                        """INSERT INTO payments
                           (patient_id, service_type, amount, payment_method, payment_date, receipt_number, received_by)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)
                           ON CONFLICT (receipt_number) DO NOTHING""",
                        (patient_ids[index], ("Consultation", "Dental review", "Laboratory", "Follow-up", "Consultation")[index],
                         (50000, 75000, 30000, 25000, 50000)[index],
                         ("Cash", "Mobile Money", "Cash", "Insurance", "Mobile Money")[index],
                         today - timedelta(days=index), f"DEMO-2026-{index + 1:03d}", user_ids["receptionist"]),
                    )

                for title, category, description, url in RESOURCES:
                    cur.execute(
                        """INSERT INTO learning_resources (title, category, description, url)
                           VALUES (%s, %s, %s, %s) ON CONFLICT (title) DO NOTHING""",
                        (title, category, description, url),
                    )
    finally:
        conn.close()


if __name__ == "__main__":
    seed_demo_data()
    print("Demo data ready. The script inserts 40 fictional sample rows on a clean database.")
    print("Demo logins: admin / Admin123!, receptionist / Reception123!, doctor / Doctor123!")
