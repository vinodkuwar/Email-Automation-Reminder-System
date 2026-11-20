"""
Email Dispatcher Module
Implements RFC 5322 EmailMessage formulation, Dry-Run Simulation (default),
and optional Real SMTP delivery with TLS and safe credential loading.
"""

import os
import smtplib
import uuid
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from src.logger_config import logger

def load_environment_variables():
    """
    Load environment variables from .env file safely.
    Attempts python-dotenv first; falls back to pure Python parser.
    """
    base_dir = Path(__file__).resolve().parent.parent
    env_path = base_dir / ".env"

    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path)
    except ImportError:
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("\"'")
                        if k not in os.environ:
                            os.environ[k] = v

load_environment_variables()

class EmailService:
    """Email Service supporting Dry-Run Simulation and Real SMTP transmission."""

    def __init__(self):
        self.reload_config()

    def reload_config(self):
        """Read and normalize current configuration from environment."""
        load_environment_variables()
        self.mode = os.getenv("EMAIL_MODE", "dry_run").strip().lower()
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
        self.smtp_port = int(os.getenv("SMTP_PORT", "587").strip())
        self.smtp_user = os.getenv("SMTP_USER", "").strip()
        self.smtp_pass = os.getenv("SMTP_PASS", "").strip()
        self.from_name = os.getenv("FROM_NAME", "Email Automation Reminder System").strip()
        self.from_email = os.getenv("FROM_EMAIL", "reminders@system.local").strip()

        # Enforce dry_run as safe default if credentials are missing
        if self.mode == "real" and (not self.smtp_user or not self.smtp_pass):
            logger.warning(
                "EMAIL_MODE was set to 'real' but SMTP_USER or SMTP_PASS is missing. "
                "Defaulting to safe 'dry_run' mode."
            )
            self.mode = "dry_run"

    def is_dry_run(self) -> bool:
        """Check if operating in safe simulation mode."""
        return self.mode != "real"

    def build_message(self, to_email: str, subject: str, body_text: str) -> EmailMessage:
        """
        Formulate a standard RFC 5322 EmailMessage.
        """
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email
        msg["Date"] = datetime.now().astimezone().strftime("%a, %d %b %Y %H:%M:%S %z")
        
        # Unique tracking message ID
        domain = self.smtp_host if self.smtp_host else "automation.local"
        msg["Message-ID"] = f"<{uuid.uuid4()}@{domain}>"

        msg.set_content(body_text)
        return msg

    def dispatch_email(self, to_email: str, subject: str, body_text: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send or simulate email dispatch based on active mode.
        
        Returns:
            Dictionary containing:
                success: bool
                status: 'SIMULATED' | 'SENT' | 'FAILED'
                mode: 'dry_run' | 'real'
                message_id: str
                timestamp: ISO string
                details: str
                error_message: Optional[str]
        """
        self.reload_config()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = self.build_message(to_email, subject, body_text)
        message_id = msg["Message-ID"]

        # ======================================================================
        # 1. DRY-RUN SIMULATION MODE (Default & Safe)
        # ======================================================================
        if self.is_dry_run():
            logger.info(
                f"[SIMULATION] Generated reminder email for <{to_email}> | "
                f"Subject: '{subject}' | Message-ID: {message_id}"
            )
            return {
                "success": True,
                "status": "SIMULATED",
                "mode": "dry_run",
                "recipient": to_email,
                "subject": subject,
                "message_id": message_id,
                "timestamp": timestamp,
                "details": "Simulated successfully. No external SMTP server was contacted.",
                "error_message": ""
            }

        # ======================================================================
        # 2. REAL SMTP TRANSMISSION MODE (Opt-in only)
        # ======================================================================
        logger.info(f"[REAL SMTP] Connecting to {self.smtp_host}:{self.smtp_port} for <{to_email}>...")
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            logger.info(f"[REAL SMTP] Email delivered to <{to_email}>. Server response 250 OK.")
            return {
                "success": True,
                "status": "SENT",
                "mode": "real",
                "recipient": to_email,
                "subject": subject,
                "message_id": message_id,
                "timestamp": timestamp,
                "details": f"Delivered via SMTP ({self.smtp_host}:{self.smtp_port})",
                "error_message": ""
            }
        except smtplib.SMTPAuthenticationError as auth_err:
            error_msg = f"SMTP Authentication failed. Check your username/app password. ({auth_err})"
            logger.error(f"[REAL SMTP] {error_msg}")
            return {
                "success": False,
                "status": "FAILED",
                "mode": "real",
                "recipient": to_email,
                "subject": subject,
                "message_id": message_id,
                "timestamp": timestamp,
                "details": "Authentication rejected by SMTP host.",
                "error_message": error_msg
            }
        except Exception as e:
            error_msg = f"SMTP Transmission error: {str(e)}"
            logger.error(f"[REAL SMTP] {error_msg}")
            return {
                "success": False,
                "status": "FAILED",
                "mode": "real",
                "recipient": to_email,
                "subject": subject,
                "message_id": message_id,
                "timestamp": timestamp,
                "details": "Socket or network error during SMTP exchange.",
                "error_message": error_msg
            }

# Module-level singleton
email_service = EmailService()
