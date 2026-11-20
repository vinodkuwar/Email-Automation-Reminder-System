"""
Email Automation & Reminder System - Main Program Entry Point
Provides a clean, student-friendly interactive CLI menu as well as
command-line argument flags for automated execution and grading.
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to sys.path so src imports resolve cleanly
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.logger_config import logger
from src.contacts import load_contacts_csv
from src.templates import load_template_file, render_template
from src.email_sender import email_service
from src.scheduler import (
    load_reminders_csv,
    process_due_reminders_once,
    run_continuous_scheduler
)
from src.reports import generate_csv_report, generate_text_summary

BANNER = """
================================================================================
   📬 EMAIL AUTOMATION & REMINDER SYSTEM (PYTHON)
   Autonomous Scheduler • CSV Pipeline • Dry-Run Simulation Engine
================================================================================
"""

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)

def view_contacts_action():
    print_header("Contact Inventory")
    try:
        contacts, invalid, summary = load_contacts_csv()
        print(f"\nTotal Raw Rows: {summary['total_raw']} | Valid Contacts: {summary['valid_count']} | Invalid: {summary['invalid_count']} | Duplicates: {summary['duplicate_count']}\n")
        
        print(f"{'ID':<10} {'Name':<18} {'Email':<30} {'Department':<16} {'Company':<22}")
        print("-" * 96)
        for c in contacts:
            print(f"{c['contact_id']:<10} {c['name']:<18} {c['email']:<30} {c['department']:<16} {c['company']:<22}")
        
        if invalid:
            print("\nRejected / Invalid Records:")
            for inv in invalid:
                print(f"  Row {inv['row']}: {inv['reason']}")
    except Exception as e:
        print(f"\n[ERROR] Failed to load contacts: {e}")

def view_reminders_action():
    print_header("Managed Reminders")
    try:
        reminders = load_reminders_csv()
        print(f"\nTotal Reminders Loaded: {len(reminders)}\n")
        print(f"{'ID':<10} {'Contact ID':<12} {'Type':<15} {'Scheduled Datetime':<22} {'Status':<12} {'Subject'}")
        print("-" * 96)
        for r in reminders:
            status = r.get("status", "PENDING")
            print(f"{r['reminder_id']:<10} {r['contact_id']:<12} {r['reminder_type']:<15} {r['scheduled_datetime']:<22} {status:<12} {r['subject'][:22]}")
    except Exception as e:
        print(f"\n[ERROR] Failed to load reminders: {e}")

def preview_emails_action():
    print_header("Personalized Email Preview")
    try:
        contacts, _, _ = load_contacts_csv()
        reminders = load_reminders_csv()
        template = load_template_file()

        if not contacts or not reminders:
            print("[INFO] Contacts or reminders file is empty.")
            return

        print(f"Generating preview for first 2 available reminders in template:\n")
        count = 0
        for rem in reminders:
            cid = rem.get("contact_id")
            contact = next((c for c in contacts if c["contact_id"] == cid), None)
            if not contact:
                continue

            context = {
                "name": contact["name"],
                "email": contact["email"],
                "department": contact["department"],
                "company": contact["company"],
                "subject": rem["subject"],
                "message": rem["message"],
                "reminder_type": rem["reminder_type"],
                "scheduled_datetime": rem["scheduled_datetime"]
            }

            rendered = render_template(template, context)
            print("-" * 80)
            print(f"PREVIEW: Reminder [{rem['reminder_id']}] -> {contact['email']}")
            print(f"SUBJECT: {rem['subject']}")
            print("-" * 80)
            print(rendered)
            print("-" * 80 + "\n")
            count += 1
            if count >= 2:
                break

    except Exception as e:
        print(f"\n[ERROR] Failed generating preview: {e}")

def process_due_reminders_action():
    print_header("Processing Due Reminders Once")
    mode_desc = "SIMULATION (Safe Dry-Run)" if email_service.is_dry_run() else "REAL SMTP"
    print(f"Active Mode: {mode_desc}\n")

    try:
        records, summary = process_due_reminders_once()
        print(f"\nExecution Complete:")
        print(f"  - Due Reminders Processed : {summary['processed_count']}")
        print(f"  - Total Reminders in DB   : {summary['total_reminders']}")
        print(f"  - Operating Mode          : {summary['active_mode'].upper()}")
        
        if records:
            print("\nProcessed Dispatches:")
            for r in records:
                print(f"  ✔ [{r['status']}] {r['reminder_id']} -> {r['recipient']} | '{r['subject']}'")
            print("\nAudit reports updated at:")
            print("  - outputs/email_report.csv")
            print("  - outputs/execution_summary.txt")
        else:
            print("\nNo reminders were due for processing at this time.")
    except Exception as e:
        print(f"\n[ERROR] Process failure: {e}")

def run_scheduler_action():
    print_header("Continuous Scheduler")
    interval = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", "10"))
    run_continuous_scheduler(interval)

def generate_report_action():
    print_header("Generate Execution Reports")
    try:
        contacts, _, contacts_summary = load_contacts_csv()
        reminders = load_reminders_csv()
        
        # Build synthetic records from current reminders
        records = []
        for r in reminders:
            cid = r.get("contact_id")
            contact = next((c for c in contacts if c["contact_id"] == cid), None)
            recip = contact["email"] if contact else "unknown@example.com"
            records.append({
                "reminder_id": r.get("reminder_id"),
                "contact_id": cid,
                "recipient": recip,
                "subject": r.get("subject"),
                "scheduled_datetime": r.get("scheduled_datetime"),
                "execution_datetime": r.get("scheduled_datetime"),
                "mode": email_service.mode,
                "status": r.get("status", "PENDING"),
                "error_message": ""
            })

        csv_path = generate_csv_report(records)
        summary_text = generate_text_summary(records, contacts_summary)
        
        print("\nReports successfully generated:")
        print(f"  - CSV Audit Report : {csv_path}")
        print("  - Summary Text File: outputs/execution_summary.txt\n")
        print(summary_text)
    except Exception as e:
        print(f"\n[ERROR] Report generation failed: {e}")

def interactive_menu():
    while True:
        print(BANNER)
        mode_label = "🛡️ DRY-RUN SIMULATION (SAFE)" if email_service.is_dry_run() else "⚡ REAL SMTP (LIVE)"
        print(f"  Active Mode: {mode_label}\n")
        print("  [1] View contacts")
        print("  [2] View reminders")
        print("  [3] Preview personalized emails")
        print("  [4] Process due reminders once")
        print("  [5] Run continuous scheduler (Ctrl+C to stop)")
        print("  [6] Generate execution report")
        print("  [7] Exit")
        print("-" * 80)

        choice = input("Select an option [1-7]: ").strip()
        if choice == "1":
            view_contacts_action()
        elif choice == "2":
            view_reminders_action()
        elif choice == "3":
            preview_emails_action()
        elif choice == "4":
            process_due_reminders_action()
        elif choice == "5":
            run_scheduler_action()
        elif choice == "6":
            generate_report_action()
        elif choice == "7":
            print("\nExiting. Thank you for using Email Automation & Reminder System.\n")
            sys.exit(0)
        else:
            print("\n[!] Invalid selection. Please enter a number between 1 and 7.")
        
        input("\nPress Enter to return to main menu...")

def main():
    parser = argparse.ArgumentParser(description="Email Automation & Reminder System (Python)")
    parser.add_argument("--once", action="store_true", help="Process due reminders once and exit")
    parser.add_argument("--scheduler", action="store_true", help="Run continuous scheduler loop")
    parser.add_argument("--preview", action="store_true", help="Display personalized email previews and exit")
    parser.add_argument("--report", action="store_true", help="Generate reports in outputs/ and exit")
    parser.add_argument("--dry-run", action="store_true", help="Force dry-run simulation mode")

    args = parser.parse_args()

    if args.dry_run:
        os.environ["EMAIL_MODE"] = "dry_run"
        email_service.reload_config()

    if args.once:
        process_due_reminders_action()
    elif args.scheduler:
        run_scheduler_action()
    elif args.preview:
        preview_emails_action()
    elif args.report:
        generate_report_action()
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
