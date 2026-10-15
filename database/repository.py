import re

from db import execute, fetch_all, fetch_one

_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")


def _identifier(value):
    if not _IDENTIFIER.fullmatch(value):
        raise ValueError("Invalid database identifier")
    return value


class Repository:
    def __init__(self, table, primary_key, fields, form_fields, headers, list_sql,
                 lookups=None, actor_column=None, options=None, patient_list_sql=None,
                 public_list_sql=None):
        self.table = _identifier(table)
        self.primary_key = _identifier(primary_key)
        self.fields = tuple(_identifier(field) for field in fields)
        self.form_fields = form_fields
        self.headers = headers
        self.list_sql = list_sql
        self.lookups = lookups or {}
        self.actor_column = _identifier(actor_column) if actor_column else None
        self.options = options or {}
        self.patient_list_sql = patient_list_sql
        self.public_list_sql = public_list_sql

    def list_all(self):
        return fetch_all(self.list_sql)

    def list_public(self):
        return fetch_all(self.public_list_sql or self.list_sql)

    def list_for_patient(self, patient_id):
        if not self.patient_list_sql:
            raise ValueError("Patient-specific listing is not configured")
        return fetch_all(self.patient_list_sql, (patient_id,))

    def get(self, record_id):
        columns = ", ".join((self.primary_key, *self.fields))
        return fetch_one(
            f"SELECT {columns} FROM {self.table} WHERE {self.primary_key} = %s",
            (record_id,),
        )

    def choices(self, field):
        if field not in self.lookups:
            return []
        table, id_column, label_column = self.lookups[field]
        table, id_column, label_column = map(_identifier, (table, id_column, label_column))
        return fetch_all(f"SELECT {id_column}, {label_column} FROM {table} ORDER BY {label_column}")

    def create(self, data, actor_id=None):
        clean = {key: data.get(key) for key in self.fields}
        if self.actor_column and actor_id is not None:
            clean[self.actor_column] = actor_id
        columns = tuple(clean)
        sql_columns = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        row = fetch_one(
            f"INSERT INTO {self.table} ({sql_columns}) VALUES ({placeholders}) RETURNING {self.primary_key}",
            tuple(clean[column] for column in columns),
        )
        return row[self.primary_key]

    def update(self, record_id, data):
        clean = {key: data.get(key) for key in self.fields}
        assignments = ", ".join(f"{column} = %s" for column in clean)
        execute(
            f"UPDATE {self.table} SET {assignments} WHERE {self.primary_key} = %s",
            (*clean.values(), record_id),
        )
