from db import fetch_all


def appointments_for_patient(patient_id):
    return fetch_all(
        """SELECT a.appointment_id, d.full_name AS doctor, a.appointment_date,
                  a.appointment_time, a.status, a.reason
           FROM appointments a JOIN doctors d ON d.doctor_id = a.doctor_id
           WHERE a.patient_id = %s ORDER BY a.appointment_date DESC, a.appointment_time""",
        (patient_id,),
    )


def records_for_patient(patient_id):
    return fetch_all(
        """SELECT m.medical_record_id, m.appointment_id, d.full_name AS doctor,
                  m.medical_history, m.diagnosis, m.notes, m.created_at
           FROM medical_records m JOIN doctors d ON d.doctor_id = m.doctor_id
           WHERE m.patient_id = %s ORDER BY m.created_at DESC""",
        (patient_id,),
    )
