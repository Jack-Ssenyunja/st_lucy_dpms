from db import fetch_all, fetch_one


def dashboard_summary():
    return fetch_one(
        """SELECT
             (SELECT count(*) FROM patients) AS patients,
             (SELECT count(*) FROM doctors WHERE active) AS active_doctors,
             (SELECT count(*) FROM appointments WHERE status = 'Scheduled'
                AND appointment_date >= CURRENT_DATE) AS upcoming_appointments,
             (SELECT COALESCE(sum(amount), 0) FROM payments
                WHERE payment_date = CURRENT_DATE) AS revenue_today"""
    )


def appointment_report(start_date, end_date):
    return fetch_all(
        """SELECT a.appointment_date, a.appointment_time, p.full_name AS patient,
                  d.full_name AS doctor, a.status, a.reason
           FROM appointments a
           JOIN patients p ON p.patient_id = a.patient_id
           JOIN doctors d ON d.doctor_id = a.doctor_id
           WHERE a.appointment_date BETWEEN %s AND %s
           ORDER BY a.appointment_date, a.appointment_time""",
        (start_date, end_date),
    )


def revenue_by_month(months=6):
    return fetch_all(
        """SELECT date_trunc('month', payment_date)::date AS month,
                  COALESCE(sum(amount), 0) AS total
           FROM payments
           WHERE payment_date >= date_trunc('month', CURRENT_DATE) - (%s - 1) * interval '1 month'
           GROUP BY date_trunc('month', payment_date)
           ORDER BY month""",
        (months,),
    )
