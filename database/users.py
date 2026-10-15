from db import execute, fetch_all, fetch_one
from auth import create_user


def list_all():
    return fetch_all(
        "SELECT user_id, username, role, active, created_at FROM users ORDER BY username"
    )


def set_active(user_id, active):
    if not active:
        account = fetch_one("SELECT role, active FROM users WHERE user_id = %s", (user_id,))
        if account and account["active"] and account["role"] == "administrator":
            count = fetch_one("SELECT count(*) AS total FROM users WHERE role = 'administrator' AND active")
            if count["total"] <= 1:
                raise ValueError("Create or activate another administrator before disabling the last one.")
    execute("UPDATE users SET active = %s WHERE user_id = %s", (active, user_id))


def add_staff(username, password, role):
    create_user(username, password, role)
