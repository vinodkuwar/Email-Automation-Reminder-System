"""
Contact Management & CSV Ingestion Module
Handles loading, schema validation, email verification, duplicate detection,
and missing value normalization for contacts.
"""

import os
import re
import csv
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from src.logger_config import logger

# RFC 5322 compliant email regex pattern
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def validate_email(email: str) -> bool:
    """Validate email formatting against standard RFC regex."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def load_contacts_csv(filepath: Optional[str] = None) -> Tuple[List[Dict[str, str]], List[Dict], Dict[str, int]]:
    """
    Load contacts from CSV.
    Supports both Pandas (if installed) and Python's standard csv module.
    
    Returns:
        valid_contacts: List of normalized, valid contact dictionaries.
        invalid_records: List of invalid records with failure reasons.
        summary: Metrics dictionary with total, valid, invalid, and duplicate counts.
    """
    if filepath is None:
        base_dir = Path(__file__).resolve().parent.parent
        filepath = str(base_dir / "data" / "contacts.csv")

    path = Path(filepath)
    if not path.exists():
        logger.error(f"Contacts file not found at: {filepath}")
        raise FileNotFoundError(f"Contacts file does not exist: {filepath}")

    logger.info(f"Loading contacts from: {filepath}")

    raw_rows: List[Dict[str, str]] = []

    # Attempt loading using pandas if available; otherwise use csv.DictReader
    try:
        import pandas as pd
        df = pd.read_csv(filepath, dtype=str)
        # Fill missing values with empty strings
        df = df.fillna("")
        raw_rows = df.to_dict(orient="records")
        logger.info(f"Loaded {len(raw_rows)} raw records via Pandas.")
    except ImportError:
        logger.info("Pandas not installed; using standard library csv.DictReader.")
        with open(filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_rows.append({k.strip(): (v.strip() if v else "") for k, v in row.items()})

    valid_contacts: List[Dict[str, str]] = []
    invalid_records: List[Dict] = []
    seen_emails = set()
    seen_ids = set()
    duplicate_count = 0

    required_fields = ["contact_id", "name", "email"]

    for idx, row in enumerate(raw_rows, start=1):
        clean_row = {k.strip().lstrip("\ufeff"): v.strip() for k, v in row.items() if k}
        
        # 1. Check required fields
        missing_fields = [f for f in required_fields if not clean_row.get(f)]
        if missing_fields:
            reason = f"Missing required field(s): {', '.join(missing_fields)}"
            invalid_records.append({"row": idx, "data": clean_row, "reason": reason})
            logger.warning(f"Row {idx} rejected: {reason}")
            continue

        cid = clean_row["contact_id"]
        email = clean_row["email"].lower()
        name = clean_row["name"]

        # 2. Check email format
        if not validate_email(email):
            reason = f"Invalid email format: '{clean_row['email']}'"
            invalid_records.append({"row": idx, "data": clean_row, "reason": reason})
            logger.warning(f"Row {idx} rejected: {reason}")
            continue

        # 3. Check for duplicates
        if email in seen_emails or cid in seen_ids:
            reason = f"Duplicate contact detected (ID: {cid}, Email: {email})"
            invalid_records.append({"row": idx, "data": clean_row, "reason": reason})
            duplicate_count += 1
            logger.warning(f"Row {idx} skipped: {reason}")
            continue

        # 4. Normalize optional fields
        department = clean_row.get("department") or "General"
        company = clean_row.get("company") or "Organization"

        normalized_contact = {
            "contact_id": cid,
            "name": name,
            "email": email,
            "department": department,
            "company": company
        }

        seen_emails.add(email)
        seen_ids.add(cid)
        valid_contacts.append(normalized_contact)

    summary = {
        "total_raw": len(raw_rows),
        "valid_count": len(valid_contacts),
        "invalid_count": len(invalid_records),
        "duplicate_count": duplicate_count
    }

    logger.info(
        f"Contacts summary: {summary['valid_count']} valid, "
        f"{summary['invalid_count']} invalid, {summary['duplicate_count']} duplicates."
    )

    return valid_contacts, invalid_records, summary

def get_contact_by_id(contacts: List[Dict[str, str]], contact_id: str) -> Optional[Dict[str, str]]:
    """Lookup a contact by contact_id."""
    for c in contacts:
        if c.get("contact_id") == contact_id:
            return c
    return None
