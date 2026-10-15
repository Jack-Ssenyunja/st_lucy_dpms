from pathlib import Path

from db import get_connection


SCHEMA_FILE = Path(__file__).parent / "sql" / "schema.sql"


def initialize_database():
    schema = SCHEMA_FILE.read_text(encoding="utf-8")
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(schema)
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_database()
    print("Database schema created or updated.")
