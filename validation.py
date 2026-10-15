from datetime import date, time
from decimal import Decimal, InvalidOperation


def normalize_value(kind, value, label, required):
    value = value.strip() if isinstance(value, str) else value
    if value == "" or value is None:
        if required:
            raise ValueError(f"{label} is required.")
        return None
    if kind == "date":
        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} must use YYYY-MM-DD format.") from exc
    if kind == "time":
        try:
            return time.fromisoformat(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} must use HH:MM format.") from exc
    if kind == "amount":
        try:
            amount = Decimal(value)
        except (InvalidOperation, TypeError) as exc:
            raise ValueError(f"{label} must be a valid amount.") from exc
        if amount <= 0:
            raise ValueError(f"{label} must be greater than zero.")
        return amount
    if kind == "url" and not value.startswith(("https://", "http://")):
        raise ValueError(f"{label} must begin with http:// or https://.")
    return value
