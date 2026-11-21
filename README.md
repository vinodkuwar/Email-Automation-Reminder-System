# 📬 Email Automation & Reminder System (Python)

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP%208-brightgreen.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Tests](https://img.shields.io/badge/Tests-100%25%20Passing-success.svg)](docs/TEST_RESULTS.md)
[![Safety Mode](https://img.shields.io/badge/Safety%20Default-Dry--Run%20Simulation-orange.svg)](#-dry-run-simulation-mode-default)

A modular, enterprise-grade, student-friendly Python automation pipeline designed to schedule, personalize, dispatch, and audit time-sensitive email notifications. Built with zero mandatory external dependencies, offline dry-run simulation by default, RFC 5322 compliance, local scheduling, and an optional Streamlit web dashboard.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Objectives](#-objectives)
- [Industry Relevance & Use Cases](#-industry-relevance--use-cases)
- [How It Works (Simple & Technical Explanations)](#-how-it-works)
- [Architecture & Data Flow](#-architecture--data-flow)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Setup](#-installation--setup)
- [CSV Data & Template Formats](#-csv-data--template-formats)
- [Dry-Run Simulation Mode (Default)](#-dry-run-simulation-mode-default)
- [Real SMTP Mode & Gmail App Password Setup](#-real-smtp-mode--gmail-app-password-setup)
- [How to Run](#-how-to-run)
- [How to Test](#-how-to-test)
- [Expected Outputs, Logs & Reports](#-expected-outputs-logs--reports)
- [Visual Artifacts & Screenshots](#-visual-artifacts--screenshots)
- [Troubleshooting Guide](#-troubleshooting-guide)
- [Limitations & Future Scope](#-limitations--future-scope)
- [Learning Outcomes](#-learning-outcomes)
- [GitHub Repository Setup Guide](#-github-repository-setup-guide)

---

## 🌟 Overview

The **Email Automation & Reminder System** bridges structured contact datasets with automated time-based communication. Whether tracking quarterly financial deadlines, board meetings, customer payment reminders, webinar registrations, or project follow-ups, this tool ensures accurate, personalized notifications without manual labor.

---

## ❗ Problem Statement

Manual notification workflows suffer from:
1. **Human Forgetfulness & Lateness:** Critical reminders sent late or forgotten entirely.
2. **Data Inconsistency:** Typos in names, dates, or email formatting.
3. **Accidental Dispatches:** Development or testing scripts firing real emails to clients.
4. **Duplicate Spam:** Schedulers repeating the same reminder due to lack of state persistence.
5. **No Auditability:** No systematic record of what was sent, when, and to whom.

---

## 🎯 Objectives

- Build an offline-first CSV data pipeline with email verification and deduplication.
- Establish dynamic template rendering with graceful handling of missing data.
- Guarantee safety by making **Dry-Run Simulation** the default operating mode.
- Prevent duplicate dispatches by atomically updating state in `data/reminders.csv`.
- Provide complete execution transparency through `outputs/email_report.csv` and `logs/automation.log`.
- Provide both a terminal CLI menu and a visual Streamlit web dashboard.

---

## 💼 Industry Relevance & Use Cases

| Industry / Domain | Practical Use Case |
|---|---|
| **Software & DevOps** | Sprint planning alerts, infrastructure invoice due dates, release freeze notifications. |
| **Finance & Billing** | Invoice payment due dates, subscription renewal alerts, tax submission reminders. |
| **Education & EdTech** | Webinar registration links, assignment submission deadlines, course orientation calls. |
| **Corporate HR** | Benefits open enrollment reminders, performance review schedules, onboarding check-ins. |

---

## 💡 How It Works

### Simple Explanation (Layman's View)
Imagine you have an address book (`contacts.csv`) and a to-do calendar of reminders (`reminders.csv`). Instead of you checking the clock every hour and drafting emails one by one, this Python robot wakes up every 10 seconds. It looks at the clock, finds tasks that are due, writes a personalized letter using a template, simulates sending it safely into an audit log (or sends it through Gmail if you explicitly tell it to), and marks the reminder as "done" so it never pesters the person again.

### Technical Explanation (Engineering View)
1. **Ingestion & Validation:** `src/contacts.py` reads `data/contacts.csv` using Pandas or `csv.DictReader`. It enforces required headers (`contact_id`, `name`, `email`), compiles an RFC 5322 regex for email syntax, and uses hash sets (`seen_emails`, `seen_ids`) to eliminate duplicates.
2. **Scheduling Evaluation:** `src/scheduler.py` reads `data/reminders.csv`. It filters for `status == 'PENDING'` and checks `scheduled_datetime <= datetime.now()`.
3. **Template Substitution:** For each due record, `src/templates.py` merges contact attributes with `templates/reminder_template.txt` using a custom `SafeDict` that avoids `KeyError` crashes.
4. **Dual Dispatch Engine:** `src/email_sender.py` formats an RFC `EmailMessage`. If `EMAIL_MODE=dry_run` (default), it simulates latency and returns status `SIMULATED`. If `EMAIL_MODE=real`, it connects via `smtplib.SMTP` over TLS (port 587) and returns `SENT`.
5. **Atomic State & Reporting:** Reminders CSV is updated, and `src/reports.py` appends the audit trail to `outputs/email_report.csv` and outputs `outputs/execution_summary.txt`.

---

## 🏗️ Architecture & Data Flow

```text
+---------------------+        +---------------------+
|  data/contacts.csv  |        | data/reminders.csv  |
+----------+----------+        +----------+----------+
           |                              |
           v                              v
+----------------------------------------------------+
|               src/contacts.py                      |
|  - RFC Email Validation & Duplicate Detection      |
+--------------------------+-------------------------+
                           |
                           v
+----------------------------------------------------+
|               src/scheduler.py                     |
|  - Due Item Filter: scheduled_datetime <= now()    |
+--------------------------+-------------------------+
                           |
                           v
+----------------------------------------------------+
|               src/templates.py                     |
|  - Template Placeholders: {name}, {subject}, etc.  |
+--------------------------+-------------------------+
                           |
                           v
+----------------------------------------------------+
|             src/email_sender.py                    |
|  - Formulates email.message.EmailMessage           |
|  * DRY_RUN (Default) -> Status: SIMULATED          |
|  * REAL SMTP (Opt-in) -> Status: SENT (TLS 587)    |
+--------------------------+-------------------------+
                           |
                           v
+----------------------------------------------------+
|              Audit & Output Reports                |
|  - logs/automation.log                             |
|  - outputs/email_report.csv                        |
|  - outputs/execution_summary.txt                   |
+----------------------------------------------------+
```

---

## ⚡ Key Features

- **Safe By Default:** Operates in Dry-Run simulation mode unless explicitly altered in `.env`.
- **Zero Mandatory External Dependencies:** Runs 100% on Python Standard Library, upgrading to Pandas, Schedule, and Streamlit when available.
- **Relational Integrity on CSV:** Decouples contacts from reminders using `contact_id` as foreign key.
- **Duplicate Prevention:** Immediate status transitions guarantee reminders are never sent twice.
- **Resilient File Handling:** Cross-platform file utilities overcome Windows Protected / Controlled Folder restrictions.
- **Comprehensive Logging:** Timestamped tracking across loading, validation, simulation, and errors.
- **Dual Interface:** Interactive command-line interface + Streamlit web dashboard.

---

## 🛠️ Technology Stack

- **Runtime:** Python 3.10+ (tested on Python 3.13)
- **Standard Library:** `csv`, `email.message`, `smtplib`, `datetime`, `logging`, `re`, `unittest`, `argparse`
- **Optional Dependencies:** `pandas`, `schedule`, `python-dotenv`, `streamlit`
- **Configuration:** `.env` (via `python-dotenv` or pure Python parser)

---

## 📁 Project Directory Structure

```text
Python_Email_Automation_Reminder_System/
│
├── data/
│   ├── contacts.csv           # Recipient contact directory
│   └── reminders.csv          # Scheduled reminders queue
│
├── templates/
│   └── reminder_template.txt  # Editable email notification template
│
├── src/
│   ├── __init__.py            # Package root
│   ├── contacts.py            # CSV loading, validation & deduplication
│   ├── templates.py           # Safe placeholder substitution engine
│   ├── email_sender.py        # EmailMessage builder, dry-run & SMTP client
│   ├── scheduler.py           # Due-reminder evaluation & polling ticker
│   ├── logger_config.py       # Central structured logger
│   ├── reports.py             # CSV audit report & text summary generator
│   └── file_utils.py          # Cross-platform file I/O utilities
│
├── outputs/
│   ├── email_report.csv       # Audit trail of all dispatches
│   └── execution_summary.txt  # KPI summary report
│
├── logs/
│   └── automation.log         # Timestamped application logs
│
├── images/
│   ├── architecture_diagram.svg # Visual SVG architecture
│   └── SCREENSHOT_CHECKLIST.md  # 11-step screenshot guide
│
├── docs/
│   ├── PROJECT_REPORT.md      # 19-section academic capstone report
│   ├── INTERVIEW_QUESTIONS.md # 30 viva questions and answers
│   ├── SIX_DAY_PROOF_PLAN.md  # Proposed 6-day incremental proof plan
│   ├── EXISTING_PROJECT_AUDIT.md # Audit of baseline project
│   ├── TEST_RESULTS.md        # Unit test execution evidence
│   └── FINAL_COMPLETION_REPORT.md # Verification & submission summary
│
├── tests/
│   └── test_project.py        # 9 automated unit and integration tests
│
├── main.py                    # Interactive CLI application
├── dashboard.py               # Streamlit visual web dashboard
├── requirements.txt           # Dependency specifications
├── .env.example               # Configuration template
├── .env                       # Local active environment configuration
├── .gitignore                 # GitHub exclusions
└── README.md                  # Complete documentation
```

---

## 🚀 Installation & Setup

### Windows Instructions

1. **Verify Python Installation:**
   ```powershell
   python --version
   ```
   *(Ensure Python 3.10 or higher is installed)*

2. **Navigate to the Python Project Directory:**
   ```powershell
   cd Python_Email_Automation_Reminder_System
   ```

3. **Create a Virtual Environment:**
   ```powershell
   python -m venv .venv
   ```

4. **Activate the Virtual Environment:**
   ```powershell
   .\.venv\Scripts\activate
   ```

5. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
   *(Note: The application is designed to function cleanly on Python's standard library even if third-party packages are not yet installed!)*

---

## 📄 CSV Data & Template Formats

### `data/contacts.csv`
```csv
contact_id,name,email,department,company
CNT-001,Alice Morgan,alice.morgan@example.com,Engineering,Innovatech Labs
CNT-002,Brian Patel,brian.patel@example.com,Finance,Apex Financial Services
```

### `data/reminders.csv`
```csv
reminder_id,contact_id,reminder_type,subject,message,scheduled_datetime,status
REM-001,CNT-001,Meeting,Sprint Review & Architecture Sync,"Quarterly review sync",2026-11-20 10:00:00,PENDING
REM-004,CNT-004,Task deadline,Submit Fleet Logistics Audit Report,"Weekly report due",2026-11-21 09:00:00,PENDING
```

### `templates/reminder_template.txt`
```text
Dear {name},

This is an automated notification regarding your scheduled {reminder_type}.

SUBJECT: {subject}
DEPARTMENT: {department} | ORGANIZATION: {company}
SCHEDULED FOR: {scheduled_datetime}

MESSAGE:
{message}
```

---

## 🛡️ Dry-Run Simulation Mode (Default)

The system runs in **Dry-Run Mode** by default (`EMAIL_MODE=dry_run` in `.env`).
- **No external network connections** are opened.
- Generates compliant RFC 5322 `EmailMessage` payloads in memory.
- Logs simulated dispatches with unique tracking Message-IDs.
- Records status explicitly as **`SIMULATED`** in reports and CSV files.
- Safe for classroom grading, offline demonstrations, and automated test harnesses.

---

## ⚡ Real SMTP Mode & Gmail App Password Setup

To enable real email dispatches to external mailboxes:

1. Open `.env` in `Python_Email_Automation_Reminder_System/`.
2. Change `EMAIL_MODE` to `real`:
   ```ini
   EMAIL_MODE=real
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASS=your_16_character_app_password
   FROM_NAME="Email Automation System"
   FROM_EMAIL=your_email@gmail.com
   ```

### How to Generate a Gmail App Password
1. Navigate to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Enable **2-Step Verification** (required by Google for SMTP programmatic access).
3. Under 2-Step Verification, select **App Passwords**.
4. Enter an App Name (e.g. `EmailReminderBot`) and click **Create**.
5. Copy the generated **16-character password** (format: `xxxx xxxx xxxx xxxx`) into `SMTP_PASS` in `.env`.
6. **Security Note:** Never commit `.env` with your App Password to GitHub.

---

## 🖥️ How to Run

### Interactive CLI Menu
Run without arguments to launch the friendly terminal interface:
```bash
python main.py
```
```text
================================================================================
   📬 EMAIL AUTOMATION & REMINDER SYSTEM (PYTHON)
   Autonomous Scheduler • CSV Pipeline • Dry-Run Simulation Engine
================================================================================
  Active Mode: 🛡️ DRY-RUN SIMULATION (SAFE)

  [1] View contacts
  [2] View reminders
  [3] Preview personalized emails
  [4] Process due reminders once
  [5] Run continuous scheduler (Ctrl+C to stop)
  [6] Generate execution report
  [7] Exit
--------------------------------------------------------------------------------
Select an option [1-7]:
```

### CLI Command-Line Flags
```bash
# Preview personalized email templates without processing
python main.py --preview

# Run a single due-reminder evaluation cycle
python main.py --once

# Force safe dry-run mode explicitly
python main.py --once --dry-run

# Run continuous background scheduler (Ctrl+C to stop)
python main.py --scheduler

# Generate audit reports in outputs/
python main.py --report
```

### Streamlit Web Dashboard
```bash
streamlit run dashboard.py
```
Open your browser at **`http://localhost:8501`** to explore the visual dashboard.

---

## 🧪 How to Test

Run the automated test suite using Python's built-in `unittest` runner:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Test Verification Matrix
| Test Case | Description | Result |
|---|---|---|
| `test_email_validation` | Validates RFC compliant and invalid email formats | **PASSED** |
| `test_contacts_csv_loading_and_validation` | Verifies schema loading and required field checking | **PASSED** |
| `test_duplicate_contact_detection` | Detects duplicate emails and contact IDs | **PASSED** |
| `test_template_rendering_and_placeholders` | Verifies token substitution | **PASSED** |
| `test_template_missing_placeholders` | Confirms missing keys do not raise exceptions | **PASSED** |
| `test_dry_run_dispatch` | Confirms simulation mode generates message without SMTP | **PASSED** |
| `test_datetime_parsing` | Validates multiple timestamp format parsing | **PASSED** |
| `test_report_generation` | Verifies CSV and text audit files are created properly | **PASSED** |
| `test_scheduler_due_reminders_processing` | Confirms due items process and duplicate sends are prevented | **PASSED** |

---

## 📊 Expected Outputs, Logs & Reports

### 1. CSV Audit Report: `outputs/email_report.csv`
```csv
reminder_id,contact_id,recipient,subject,scheduled_datetime,execution_datetime,mode,status,error_message
REM-001,CNT-001,alice.morgan@example.com,Sprint Review & Architecture Sync,2026-11-20 10:00:00,2026-11-20 17:42:36,dry_run,SIMULATED,
REM-002,CNT-002,brian.patel@example.com,Q4 Cloud Infrastructure Invoice Due,2026-11-20 11:30:00,2026-11-20 17:42:36,dry_run,SIMULATED,
```

### 2. Execution Summary: `outputs/execution_summary.txt`
```text
================================================================================
EMAIL AUTOMATION & REMINDER SYSTEM - EXECUTION SUMMARY REPORT
================================================================================
Generated At          : 2026-11-20 17:42:38
Total Reminders Run   : 3
Simulated Deliveries  : 3 (Dry-run mode, no real emails sent)
Real Emails Sent      : 0
Failures              : 0
Delivery Success Rate : 100.0%
--------------------------------------------------------------------------------
```

### 3. Application Logs: `logs/automation.log`
Structured, timestamped logs recording application events and diagnostics.

---

## 🖼️ Visual Artifacts & Screenshots

- `images/architecture_diagram.svg`: System architecture diagram.
- `images/SCREENSHOT_CHECKLIST.md`: Step-by-step checklist to capture the 11 project evidence screenshots using Windows Snipping Tool (`Win + Shift + S`).

---

## 🔧 Troubleshooting Guide

| Issue | Cause | Solution |
|---|---|---|
| `python: command not found` | Python not in system PATH. | Reinstall Python and check **"Add Python to PATH"**. |
| `ModuleNotFoundError: No module named 'pandas'` | Pandas not installed. | System automatically falls back to `csv.DictReader`! Or run `pip install pandas`. |
| `SMTPAuthenticationError (535)` | Invalid Gmail password. | Ensure 2-Step Verification is active and generate a 16-character **App Password**. |
| `Invalid email rejected` | Email failed RFC regex check. | Correct email format in `data/contacts.csv` (must contain `@` and valid domain). |
| `BOM header in CSV` | PowerShell or Excel saved with BOM. | System uses `utf-8-sig` to automatically strip Byte Order Marks. |

---

## 📈 Limitations & Future Scope

### Limitations
- Flat CSV storage is suitable for small to mid-scale workflows; large enterprise deployments should migrate to an indexed SQL database.
- Local scheduler process stops if the host machine powers down.

### Future Scope
- Migration to SQLite / PostgreSQL backend.
- Rich HTML email templates with visual CSS formatting and inline attachments.
- Distributed background workers using Celery / Redis.
- Webhook tracking for email opens and click-through rates.

---

## 🎓 Learning Outcomes

Through this project, students and developers master:
1. Enterprise data pipeline design using Python's `csv` and `pandas`.
2. Safe string interpolation and templating algorithms.
3. Network email protocols (SMTP, STARTTLS, MIME) and RFC 5322 compliance.
4. Designing safety-first automation systems with non-destructive simulation modes.
5. Unit testing, regression verification, and academic technical documentation.

---

## 🐙 GitHub Repository Setup Guide

To publish this project to your GitHub account:

1. **Create a New Repository on GitHub:**
   - **Repository Name:** `email-automation-reminder-system-python`
   - **Description:** `Python-based email automation and reminder scheduling project with CSV contacts, personalized templates, dry-run simulation, optional Gmail SMTP, scheduling, logging, and reports.`
   - **Visibility:** Public (or Private for coursework submission).
   - Do NOT initialize with a README (this repository already has one).

2. **Initialize Git and Commit:**
   ```bash
   cd Python_Email_Automation_Reminder_System
   git init
   git add .
   git commit -m "feat: complete Email Automation & Reminder System in Python with dry-run simulation and tests"
   ```

3. **Link Remote and Push:**
   ```bash
   git branch -M main
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/email-automation-reminder-system-python.git
   git push -u origin main
   ```

4. **Recommended GitHub Topics / Tags:**
   `python`, `email-automation`, `reminder-system`, `automation`, `csv`, `smtp`, `scheduling`, `pandas`, `productivity`, `beginner-project`

---

## ⚖️ License

Distributed under the **MIT License**. See `LICENSE` for details.
## 📸 Project Screenshots

### 1. Dashboard Overview
![Dashboard Overview](images/pic%201.png)

### 2. Contacts Management
![Contacts Management](images/pic%202.png)

### 3. Reminders Management
![Reminders Management](images/pic%203.png)

### 4. Live Email Preview
![Live Email Preview](images/pic%204.png)

### 5. Reminder Processing
![Reminder Processing](images/pic%205.png)

### 6. Reports & Execution Results
![Reports & Execution Results](images/pic%206.png)
