import unittest
from datetime import date
from decimal import Decimal

from auth import hash_password, verify_password
from database import appointments, doctors, learning_resources, medical_records, patients, payments, prescriptions
from database.repository import Repository
from validation import normalize_value


class ValidationTests(unittest.TestCase):
    def test_valid_date_and_time_are_normalized(self):
        self.assertEqual(normalize_value("date", "2026-10-09", "Visit date", True), date(2026, 10, 9))
        self.assertEqual(normalize_value("time", "09:30", "Visit time", True).isoformat(timespec="minutes"), "09:30")

    def test_invalid_date_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            normalize_value("date", "09/10/2026", "Visit date", True)

    def test_nonpositive_or_invalid_amount_is_rejected(self):
        for value in ("0", "-1", "not money"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_value("amount", value, "Amount", True)

    def test_positive_amount_and_url_are_accepted(self):
        self.assertEqual(normalize_value("amount", "50000.00", "Amount", True), Decimal("50000.00"))
        self.assertEqual(normalize_value("url", "https://example.org/resource", "URL", True), "https://example.org/resource")

    def test_required_and_optional_blank_values(self):
        with self.assertRaisesRegex(ValueError, "required"):
            normalize_value("text", "", "Patient name", True)
        self.assertIsNone(normalize_value("text", "", "Email", False))


class AuthenticationTests(unittest.TestCase):
    def test_password_hash_verifies_and_is_not_plaintext(self):
        encoded = hash_password("a-long-test-password")
        self.assertNotIn("a-long-test-password", encoded)
        self.assertTrue(verify_password("a-long-test-password", encoded))
        self.assertFalse(verify_password("incorrect-password", encoded))

    def test_malformed_hash_fails_closed(self):
        self.assertFalse(verify_password("anything", "invalid"))


class RepositoryMetadataTests(unittest.TestCase):
    def test_each_er_diagram_entity_has_a_repository(self):
        repositories = (
            patients.repository, doctors.repository, appointments.repository,
            medical_records.repository, payments.repository, prescriptions.repository,
            learning_resources.repository,
        )
        self.assertEqual(len({repository.table for repository in repositories}), 7)
        self.assertEqual(appointments.repository.lookups.keys(), {"patient_id", "doctor_id"})
        self.assertEqual(medical_records.repository.lookups.keys(), {"patient_id", "appointment_id", "doctor_id"})

    def test_resource_lists_are_separated_for_public_and_admin(self):
        self.assertIn("WHERE active = TRUE", learning_resources.repository.public_list_sql)
        self.assertNotIn("WHERE active = TRUE", learning_resources.repository.list_sql)

    def test_dynamic_identifiers_reject_sql_fragments(self):
        with self.assertRaises(ValueError):
            Repository("patients; DROP TABLE patients", "patient_id", (), (), (), "SELECT 1")


if __name__ == "__main__":
    unittest.main()
