import hashlib
import hmac
import os

from db import connection, fetch_one

_ITERATIONS = 310_000


def hash_password(password):
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${_ITERATIONS}${salt}${digest}"


def verify_password(password, encoded):
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt), int(iterations)
        ).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def authenticate(username, password):
    user = fetch_one(
        """SELECT u.user_id, u.username, u.password_hash, u.role, u.active,
                  p.patient_id
           FROM users u
           LEFT JOIN patients p ON p.user_id = u.user_id
           WHERE lower(u.username) = lower(%s)""",
        (username.strip(),),
    )
    if not user or not user["active"] or not verify_password(password, user["password_hash"]):
        return None
    return {key: value for key, value in user.items() if key != "password_hash"}


def create_user(username, password, role):
    username = username.strip().lower()
    if len(username) < 3 or len(password) < 10:
        raise ValueError("Username must be at least 3 characters and password at least 10 characters.")
    if role not in {"administrator", "doctor", "receptionist"}:
        raise ValueError("Staff account role is not allowed.")
    with connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, hash_password(password), role),
        )


def register_patient(username, password, full_name, date_of_birth, gender, phone_number, email):
    username = username.strip().lower()
    full_name = full_name.strip()
    if len(username) < 3 or len(password) < 10:
        raise ValueError("Username must be at least 3 characters and password at least 10 characters.")
    if not full_name or not phone_number.strip():
        raise ValueError("Name and phone number are required.")
    with connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'patient') RETURNING user_id",
            (username, hash_password(password)),
        )
        user_id = cur.fetchone()[0]
        cur.execute(
            """INSERT INTO patients (user_id, full_name, date_of_birth, gender, phone_number, email)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, full_name, date_of_birth, gender, phone_number.strip(), email.strip() or None),
        )
