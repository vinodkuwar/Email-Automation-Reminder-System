"""
Reporting & Audit Generation Module
Exports execution reports to CSV (outputs/email_report.csv) and generates
readable execution summaries (outputs/execution_summary.txt).
"""

import io
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.logger_config import logger
from src.file_utils import safe_write_text, safe_append_text

REPORT_COLUMNS = [
    "reminder_id",
    "contact_id",
    "recipient",
    "subject",
    "scheduled_datetime",
    "execution_datetime",
    "mode",
    "status",
    "error_message"
]

def generate_csv_report(records: List[Dict[str, Any]], output_filepath: Optional[str] = None) -> str:
    """
    Generate or append to outputs/email_report.csv using safe file utilities.
    """
    if output_filepath is None:
        base_dir = Path(__file__).resolve().parent.parent
        output_filepath = str(base_dir / "outputs" / "email_report.csv")

    path = Path(output_filepath)
    write_header = not path.exists() or path.stat().st_size == 0

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=REPORT_COLUMNS)
    if write_header:
        writer.writeheader()

    for rec in records:
        row = {
            "reminder_id": rec.get("reminder_id", ""),
            "contact_id": rec.get("contact_id", ""),
            "recipient": rec.get("recipient", ""),
            "subject": rec.get("subject", ""),
            "scheduled_datetime": rec.get("scheduled_datetime", ""),
            "execution_datetime": rec.get("timestamp") or rec.get("execution_datetime") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": rec.get("mode", "dry_run"),
            "status": rec.get("status", "SIMULATED"),
            "error_message": rec.get("error_message", "")
        }
        writer.writerow(row)

    csv_text = output.getvalue()
    if write_header:
        safe_write_text(output_filepath, csv_text)
    else:
        safe_append_text(output_filepath, csv_text)

    logger.info(f"Generated CSV report with {len(records)} records at: {output_filepath}")
    return output_filepath

def generate_text_summary(
    records: List[Dict[str, Any]],
    contacts_summary: Optional[Dict[str, Any]] = None,
    output_filepath: Optional[str] = None
) -> str:
    """
    Generate a detailed textual execution summary report at outputs/execution_summary.txt.
    """
    if output_filepath is None:
        base_dir = Path(__file__).resolve().parent.parent
        output_filepath = str(base_dir / "outputs" / "execution_summary.txt")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    simulated_count = sum(1 for r in records if r.get("status") == "SIMULATED")
    sent_count = sum(1 for r in records if r.get("status") == "SENT")
    failed_count = sum(1 for r in records if r.get("status") == "FAILED")
    total_processed = len(records)
    success_rate = ((simulated_count + sent_count) / total_processed * 100) if total_processed > 0 else 0.0

    lines = [
        "=" * 80,
        "EMAIL AUTOMATION & REMINDER SYSTEM - EXECUTION SUMMARY REPORT",
        "=" * 80,
        f"Generated At          : {now_str}",
        f"Total Reminders Run   : {total_processed}",
        f"Simulated Deliveries  : {simulated_count} (Dry-run mode, no real emails sent)",
        f"Real Emails Sent      : {sent_count}",
        f"Failures              : {failed_count}",
        f"Delivery Success Rate : {success_rate:.1f}%",
        "-" * 80
    ]

    if contacts_summary:
        lines.extend([
            "CONTACT INVENTORY SUMMARY:",
            f"  - Total Raw Contacts: {contacts_summary.get('total_raw', 0)}",
            f"  - Valid Contacts    : {contacts_summary.get('valid_count', 0)}",
            f"  - Invalid Records   : {contacts_summary.get('invalid_count', 0)}",
            f"  - Duplicate Records : {contacts_summary.get('duplicate_count', 0)}",
            "-" * 80
        ])

    lines.append("ITEMIZED DISPATCH AUDIT LOG:")
    if not records:
        lines.append("  (No reminders were processed in this cycle)")
    else:
        for idx, r in enumerate(records, start=1):
            status = r.get("status", "UNKNOWN")
            mode = r.get("mode", "dry_run").upper()
            rid = r.get("reminder_id", "N/A")
            recip = r.get("recipient", "N/A")
            subj = r.get("subject", "N/A")
            err = f" | Error: {r.get('error_message')}" if r.get("error_message") else ""
            lines.append(f"  [{idx}] {rid} | {status} ({mode}) -> {recip} | Subj: '{subj}'{err}")

    lines.extend([
        "=" * 80,
        "NOTE: In dry-run mode, all reminders are marked as SIMULATED to guarantee",
        "that dummy contact data and simulation logs are never confused with real email deliveries.",
        "=" * 80
    ])

    summary_text = "\n".join(lines)
    safe_write_text(output_filepath, summary_text)

    logger.info(f"Generated text execution summary at: {output_filepath}")
    return summary_text
