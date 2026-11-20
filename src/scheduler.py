"""
Reminder Scheduling Engine Module
Loads reminders, matches them with contacts, detects due items,
dispatches notifications, updates status to avoid duplicates,
and supports both one-time execution and continuous scheduling with graceful exit.
"""

import os
import io
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from src.logger_config import logger
from src.contacts import load_contacts_csv, get_contact_by_id
from src.templates import load_template_file, render_template
from src.email_sender import email_service
from src.reports import generate_csv_report, generate_text_summary
from src.file_utils import safe_write_text

REMINDER_COLUMNS = [
    "reminder_id",
    "contact_id",
    "reminder_type",
    "subject",
    "message",
    "scheduled_datetime",
    "status"
]

def load_reminders_csv(filepath: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Load all reminder records from data/reminders.csv.
    """
    if filepath is None:
        base_dir = Path(__file__).resolve().parent.parent
        filepath = str(base_dir / "data" / "reminders.csv")

    path = Path(filepath)
    if not path.exists():
        logger.error(f"Reminders file not found: {filepath}")
        raise FileNotFoundError(f"Reminders file does not exist: {filepath}")

    reminders = []
    try:
        import pandas as pd
        df = pd.read_csv(filepath, dtype=str)
        df = df.fillna("")
        reminders = df.to_dict(orient="records")
    except ImportError:
        with open(filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                reminders.append({k.strip(): (v.strip() if v else "") for k, v in row.items()})

    logger.info(f"Loaded {len(reminders)} reminders from: {filepath}")
    return reminders

def save_reminders_csv(reminders: List[Dict[str, str]], filepath: Optional[str] = None):
    """
    Atomically save updated reminders back to CSV using safe file writer.
    """
    if filepath is None:
        base_dir = Path(__file__).resolve().parent.parent
        filepath = str(base_dir / "data" / "reminders.csv")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=REMINDER_COLUMNS)
    writer.writeheader()
    for r in reminders:
        writer.writerow({col: r.get(col, "") for col in REMINDER_COLUMNS})

    safe_write_text(filepath, output.getvalue())
    logger.info(f"Saved {len(reminders)} reminders to: {filepath}")

def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse standard datetime string into datetime object."""
    if not dt_str:
        return None
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str.strip(), fmt)
        except ValueError:
            continue
    return None

def process_due_reminders_once(
    contacts_path: Optional[str] = None,
    reminders_path: Optional[str] = None,
    template_path: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Execute a single sweep:
      1. Load contacts and template
      2. Identify PENDING reminders whose scheduled_datetime <= now()
      3. Render personalized email
      4. Dispatch (Simulated or Real SMTP based on EMAIL_MODE)
      5. Update reminder status in reminders.csv (prevents duplicate sending)
      6. Generate outputs/ reports
      
    Returns:
        (execution_records, summary_stats)
    """
    contacts, invalid_contacts, contacts_summary = load_contacts_csv(contacts_path)
    reminders = load_reminders_csv(reminders_path)
    template_content = load_template_file(template_path)

    now = datetime.now()
    execution_records: List[Dict[str, Any]] = []
    updated = False

    logger.info(f"Processing check at: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    for rem in reminders:
        status = rem.get("status", "").strip().upper()
        if status != "PENDING":
            continue

        sched_dt = parse_datetime(rem.get("scheduled_datetime", ""))
        if not sched_dt:
            logger.warning(f"Reminder {rem.get('reminder_id')} has invalid date: {rem.get('scheduled_datetime')}")
            continue

        # Check if due
        if sched_dt <= now:
            cid = rem.get("contact_id")
            contact = get_contact_by_id(contacts, cid)
            if not contact:
                logger.error(f"Contact ID '{cid}' not found for reminder {rem.get('reminder_id')}")
                rem["status"] = "FAILED"
                execution_records.append({
                    **rem,
                    "recipient": "UNKNOWN",
                    "status": "FAILED",
                    "mode": email_service.mode,
                    "error_message": f"Contact '{cid}' not found"
                })
                updated = True
                continue

            # Build personalization context
            context = {
                "name": contact.get("name", "Valued Colleague"),
                "email": contact.get("email", ""),
                "department": contact.get("department", "General"),
                "company": contact.get("company", "Organization"),
                "subject": rem.get("subject", "Notification"),
                "message": rem.get("message", ""),
                "reminder_type": rem.get("reminder_type", "Reminder"),
                "scheduled_datetime": rem.get("scheduled_datetime", "")
            }

            body_text = render_template(template_content, context)
            to_email = contact["email"]
            subject = rem["subject"]

            # Dispatch via email service
            result = email_service.dispatch_email(to_email, subject, body_text, context)
            
            # Update reminder status
            new_status = result["status"]
            rem["status"] = new_status
            updated = True

            record = {
                "reminder_id": rem["reminder_id"],
                "contact_id": cid,
                "recipient": to_email,
                "subject": subject,
                "scheduled_datetime": rem.get("scheduled_datetime", ""),
                "execution_datetime": result["timestamp"],
                "mode": result["mode"],
                "status": new_status,
                "error_message": result.get("error_message", "")
            }
            execution_records.append(record)

    if updated:
        save_reminders_csv(reminders, reminders_path)

    # Generate audit reports if any were processed
    if execution_records:
        generate_csv_report(execution_records)
        generate_text_summary(execution_records, contacts_summary)

    logger.info(f"Cycle completed. Processed {len(execution_records)} due reminder(s).")
    return execution_records, {
        "processed_count": len(execution_records),
        "total_reminders": len(reminders),
        "active_mode": email_service.mode
    }

def run_continuous_scheduler(interval_seconds: int = 10):
    """
    Run continuous background scheduler.
    Uses 'schedule' library if available; otherwise uses a clean time.sleep loop.
    Supports graceful termination via Ctrl+C (KeyboardInterrupt).
    """
    logger.info(f"Starting continuous scheduler loop (polling every {interval_seconds}s). Press Ctrl+C to stop.")
    print(f"\n[SCHEDULER ACTIVE] Polling for due reminders every {interval_seconds} seconds...")
    print("Press Ctrl+C at any time to return to menu or exit cleanly.\n")

    has_schedule_lib = False
    try:
        import schedule
        schedule.every(interval_seconds).seconds.do(process_due_reminders_once)
        has_schedule_lib = True
    except ImportError:
        has_schedule_lib = False

    try:
        # Run an initial check immediately
        process_due_reminders_once()

        while True:
            if has_schedule_lib:
                import schedule
                schedule.run_pending()
                time.sleep(1)
            else:
                time.sleep(interval_seconds)
                process_due_reminders_once()

    except KeyboardInterrupt:
        logger.info("Continuous scheduler interrupted by user (Ctrl+C). Shutting down gracefully.")
        print("\n[SCHEDULER STOPPED] Graceful shutdown complete.")
