"""
Unit and Integration Test Suite
Tests Contacts CSV loading, validation, template rendering, dry-run dispatch,
scheduler logic, report generation, and error handling.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta

# Ensure src modules are resolvable
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.contacts import validate_email, load_contacts_csv, get_contact_by_id
from src.templates import load_template_file, render_template
from src.email_sender import email_service
from src.reports import generate_csv_report, generate_text_summary
from src.scheduler import parse_datetime, process_due_reminders_once, load_reminders_csv

class TestEmailAutomationSystem(unittest.TestCase):

    def setUp(self):
        """Set up temporary directory for test fixtures."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.test_dir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.test_dir.cleanup()

    # 1. Test Email Validation
    def test_email_validation(self):
        valid_emails = [
            "alice@example.com",
            "john.doe@sub.company.org",
            "support+alerts@service.io",
            "user_name-12@domain.co"
        ]
        invalid_emails = [
            "invalid-email",
            "@missinguser.com",
            "missingdomain@",
            "spaces in@email.com",
            "",
            None
        ]
        for email in valid_emails:
            self.assertTrue(validate_email(email), f"Expected valid: {email}")

        for email in invalid_emails:
            self.assertFalse(validate_email(email), f"Expected invalid: {email}")

    # 2. Test Contact CSV Loading & Required Fields Validation
    def test_contacts_csv_loading_and_validation(self):
        csv_content = (
            "contact_id,name,email,department,company\n"
            "C-1,Valid User,valid@example.com,IT,TechCorp\n"
            "C-2,Missing Email,,HR,Corp\n"
            "C-3,,no_name@example.com,Ops,Corp\n"
        )
        csv_file = self.temp_path / "contacts_test.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        valid, invalid, summary = load_contacts_csv(str(csv_file))
        self.assertEqual(len(valid), 1)
        self.assertEqual(valid[0]["email"], "valid@example.com")
        self.assertEqual(summary["valid_count"], 1)
        self.assertEqual(summary["invalid_count"], 2)

    # 3. Test Duplicate Contact Detection
    def test_duplicate_contact_detection(self):
        csv_content = (
            "contact_id,name,email,department,company\n"
            "C-1,Original,dup@example.com,Sales,Company\n"
            "C-2,Duplicate Email,dup@example.com,Marketing,Company\n"
            "C-1,Duplicate ID,other@example.com,HR,Company\n"
        )
        csv_file = self.temp_path / "dup_contacts.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        valid, invalid, summary = load_contacts_csv(str(csv_file))
        self.assertEqual(len(valid), 1)
        self.assertEqual(summary["duplicate_count"], 2)

    # 4. Test Template Loading & Personalization
    def test_template_rendering_and_placeholders(self):
        raw_template = "Hello {name}, your {reminder_type} on {subject} is at {scheduled_datetime}. Dept: {department}."
        context = {
            "name": "Sarah Connor",
            "reminder_type": "Briefing",
            "subject": "Cyber Security Sync",
            "scheduled_datetime": "2026-12-01 10:00:00",
            "department": "Defense"
        }
        rendered = render_template(raw_template, context)
        self.assertIn("Hello Sarah Connor", rendered)
        self.assertIn("Cyber Security Sync", rendered)
        self.assertIn("Dept: Defense", rendered)

    # 5. Test Template Missing Placeholders Gracefulness
    def test_template_missing_placeholders(self):
        raw_template = "Hello {name}, your note is {missing_key}."
        rendered = render_template(raw_template, {"name": "Alex"})
        self.assertIn("Hello Alex", rendered)
        # Should not raise exception
        self.assertTrue(len(rendered) > 0)

    # 6. Test Dry-Run Email Dispatcher (No Real SMTP Calls)
    def test_dry_run_dispatch(self):
        email_service.reload_config()
        # Guarantee dry_run mode in test
        email_service.mode = "dry_run"
        self.assertTrue(email_service.is_dry_run())

        result = email_service.dispatch_email(
            to_email="test.recipient@example.com",
            subject="Test Notification",
            body_text="This is a test notification message body."
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "SIMULATED")
        self.assertEqual(result["mode"], "dry_run")
        self.assertIn("@", result["message_id"])
        self.assertEqual(result["recipient"], "test.recipient@example.com")

    # 7. Test Datetime Parsing Helper
    def test_datetime_parsing(self):
        dt1 = parse_datetime("2026-11-20 14:30:00")
        self.assertIsNotNone(dt1)
        self.assertEqual(dt1.year, 2026)
        self.assertEqual(dt1.minute, 30)

        dt2 = parse_datetime("invalid-date")
        self.assertIsNone(dt2)

    # 8. Test Report Generation (CSV and Text Summary)
    def test_report_generation(self):
        records = [
            {
                "reminder_id": "REM-T1",
                "contact_id": "CNT-T1",
                "recipient": "recip1@example.com",
                "subject": "Test Task 1",
                "scheduled_datetime": "2026-11-20 10:00:00",
                "execution_datetime": "2026-11-20 10:01:00",
                "mode": "dry_run",
                "status": "SIMULATED",
                "error_message": ""
            }
        ]
        csv_out = self.temp_path / "test_report.csv"
        txt_out = self.temp_path / "test_summary.txt"

        generate_csv_report(records, str(csv_out))
        self.assertTrue(csv_out.exists())
        content = csv_out.read_text(encoding="utf-8")
        self.assertIn("REM-T1", content)
        self.assertIn("SIMULATED", content)

        summary_text = generate_text_summary(records, {"valid_count": 1}, str(txt_out))
        self.assertTrue(txt_out.exists())
        self.assertIn("SIMULATED", summary_text)
        self.assertIn("REM-T1", summary_text)

    # 9. Test Scheduler Due Reminder Detection & Status Transition
    def test_scheduler_due_reminders_processing(self):
        # Create test contacts CSV
        contacts_csv = self.temp_path / "contacts.csv"
        contacts_csv.write_text(
            "contact_id,name,email,department,company\n"
            "CNT-101,John Pilot,john.pilot@example.com,Flight Ops,AeroCorp\n",
            encoding="utf-8"
        )

        # Create reminders: one DUE in past, one in FUTURE
        past_time = (datetime.now() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        future_time = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")

        reminders_csv = self.temp_path / "reminders.csv"
        reminders_csv.write_text(
            "reminder_id,contact_id,reminder_type,subject,message,scheduled_datetime,status\n"
            f"REM-DUE,CNT-101,Meeting,Urgent Sync,Check flight schedule,{past_time},PENDING\n"
            f"REM-FUT,CNT-101,Follow-up,Future Check,Routine check,{future_time},PENDING\n",
            encoding="utf-8"
        )

        template_file = self.temp_path / "template.txt"
        template_file.write_text("Hello {name}, reminder for {subject}.", encoding="utf-8")

        # Process due reminders
        records, summary = process_due_reminders_once(
            contacts_path=str(contacts_csv),
            reminders_path=str(reminders_csv),
            template_path=str(template_file)
        )

        # Only the DUE reminder should have processed
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["reminder_id"], "REM-DUE")
        self.assertEqual(records[0]["status"], "SIMULATED")

        # Verify reminders.csv was updated and REM-DUE is now SIMULATED
        updated_reminders = load_reminders_csv(str(reminders_csv))
        due_item = next(r for r in updated_reminders if r["reminder_id"] == "REM-DUE")
        fut_item = next(r for r in updated_reminders if r["reminder_id"] == "REM-FUT")
        self.assertEqual(due_item["status"], "SIMULATED")
        self.assertEqual(fut_item["status"], "PENDING")

        # Re-running immediately should process ZERO due reminders (prevent duplicate dispatch)
        records_second_run, _ = process_due_reminders_once(
            contacts_path=str(contacts_csv),
            reminders_path=str(reminders_csv),
            template_path=str(template_file)
        )
        self.assertEqual(len(records_second_run), 0)

if __name__ == "__main__":
    unittest.main()
