# St. Lucy Digital Patient Management System

A coursework desktop application for St. Lucy Medical Clinic. PostgreSQL stores clinic data; Python 3 and Tkinter provide the interface. The model follows the supplied ERDs and data dictionary, and extends them with an active learning-resource catalogue for patient health education.

**This is a fictional-data coursework demonstration, not clinical software.** Do not enter real patient information. The demo login credentials are public in this repository, and the app uses one PostgreSQL connection identity with role checks in the desktop UI; it is not production-grade authorization or a compliant medical-record platform.

## Quick Start

Prerequisites: Python 3.10 or newer, Tkinter, and PostgreSQL 14 or newer. On macOS, install and start PostgreSQL if needed:

```sh
brew install postgresql@16
brew services start postgresql@16
createdb st_lucy_dpms
```

From this project folder, create an environment and install packages:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` to match your local PostgreSQL username/password. Then initialize and seed the database, and launch the app:

```sh
python init_db.py
python seed.py
python app.py
```

Demo staff accounts (change them before any shared demonstration):

| Username | Password | Role |
| --- | --- | --- |
| `admin` | `Admin123!` | Administrator |
| `receptionist` | `Reception123!` | Receptionist |
| `doctor` | `Doctor123!` | Doctor |

Patients can create their own account from the sign-in window. `python seed.py` creates 40 fictional sample rows on a clean database and can be run again without duplicating the included records.

## Project Map

- `app.py`: Tkinter sign-in, patient registration, role-based screens, forms, dashboard, and reports.
- `sql/schema.sql`: PostgreSQL tables, keys, checks, indexes, and validation triggers.
- `db.py`: PostgreSQL connection and query helpers.
- `auth.py`: PBKDF2 password hashing and account workflows.
- `database/`: one repository module per clinic entity, plus reports and patient-scoped queries.
- `init_db.py`: applies the schema to an already-created database.
- `seed.py`: inserts fictional demo accounts, clinic records, and health-resource links.
- `validation.py`: shared date, time, amount, and URL validation used by forms.
- `tests/test_core.py`: offline unit tests that do not require a running PostgreSQL server.
- `PROJECT_GUIDE.md`: detailed project workflow, requirements mapping, data dictionary, use cases, and verification limits.

## Tests

```sh
python -m unittest discover -s tests -v
python -m compileall -q .
```

The unit tests cover input validation, password hashing, and repository configuration. A real database connection is required to verify schema creation, triggers, seeding, and the end-to-end GUI data flow; see `PROJECT_GUIDE.md` for the integration checklist.
