# 📅 Six-Day Proof-Building Plan: Email Automation & Reminder System

> **Transparency Notice:** This document outlines a structured, pedagogical 6-day incremental build plan suitable for an internship milestone, academic portfolio, or progressive Git commit history. If this project was implemented in an intensive single-session sprint, use this roadmap to understand the engineering progression or structure your future Git branch commits.

---

## 🗓️ Day 1: Setup, Architecture & Project Foundation

### Objectives
Establish the project workspace, isolate configuration from source code, and set up the foundation files and directories.

### Tasks Completed
- Initialize the root project folder: `Python_Email_Automation_Reminder_System/`.
- Create core subdirectories: `data/`, `src/`, `templates/`, `outputs/`, `logs/`, `docs/`, `tests/`, `images/`.
- Configure environment isolation with `.gitignore` and `.env.example`.
- Define Python dependencies in `requirements.txt`.
- Draft initial system architecture and data flow diagrams.

### Files Created / Modified
- `requirements.txt`
- `.gitignore`
- `.env.example`
- `.env`
- `src/__init__.py`
- `docs/EXISTING_PROJECT_AUDIT.md`

### Suggested Commit Message
```text
feat(init): establish project directory structure, environment templates, and dependency definitions
```

### Visual Evidence to Capture
- Screenshot of the directory tree (`tree /F` or VS Code file explorer).
- Screenshot of `.env.example` showing clean placeholders and dry-run default mode.

---

## 🗓️ Day 2: Contacts CSV Pipeline & Template Engine

### Objectives
Design the contact dataset schema, implement CSV parsing with validation, and create editable email templates.

### Tasks Completed
- Author `data/contacts.csv` with safe dummy contacts across diverse departments (`@example.com`).
- Build `src/contacts.py` with RFC email regex validation, required field checks, missing value normalization, and duplicate filtering.
- Author `templates/reminder_template.txt` with `{name}`, `{company}`, `{department}`, `{subject}`, `{message}` placeholders.
- Implement `src/templates.py` with `SafeDict` placeholder substitution to prevent `KeyError` crashes.

### Files Created / Modified
- `data/contacts.csv`
- `templates/reminder_template.txt`
- `src/contacts.py`
- `src/templates.py`

### Suggested Commit Message
```text
feat(contacts): implement CSV ingestion with RFC email validation, deduplication, and template rendering engine
```

### Visual Evidence to Capture
- Screenshot of `data/contacts.csv` opened in a table viewer.
- Screenshot of `templates/reminder_template.txt` displaying placeholders.

---

## 🗓️ Day 3: Email Personalization & Dual-Mode Dispatcher

### Objectives
Implement email message generation using standard Python libraries, prioritizing a safe dry-run simulation mode.

### Tasks Completed
- Build `src/email_sender.py` utilizing Python's modern `email.message.EmailMessage`.
- Implement **Dry-Run Simulation Mode** as the default behavior: generates preview metadata, records date/time, and generates UUID message IDs without contacting SMTP servers.
- Implement **Real SMTP Mode**: integrates `smtplib` with TLS encryption (port 587) and safe `.env` credential extraction.
- Implement cross-platform file utilities in `src/file_utils.py` for sandbox resilience.

### Files Created / Modified
- `src/email_sender.py`
- `src/file_utils.py`

### Suggested Commit Message
```text
feat(email): build dual-mode email dispatcher with EmailMessage formulation and default dry-run simulation
```

### Visual Evidence to Capture
- Terminal output showing generated dry-run simulated dispatch log with Message-ID.
- Inspection of `EmailMessage` headers.

---

## 🗓️ Day 4: Scheduling Logic & Reminder Queue Management

### Objectives
Implement time-based reminder processing, avoidance of duplicate dispatches, and background ticker mechanisms.

### Tasks Completed
- Author `data/reminders.csv` with 6 diverse reminder types (Meeting, Payment, Webinar, Task deadline, Follow-up).
- Build `src/scheduler.py` to parse timestamps, evaluate due reminders (`scheduled_datetime <= now()`), and join contact metadata via `contact_id`.
- Implement atomic status updating (`PENDING` &rarr; `SIMULATED` / `SENT`) in CSV to ensure reminders are never processed twice.
- Provide both single-cycle execution (`process_due_reminders_once()`) and continuous loop polling with graceful Ctrl+C exit.

### Files Created / Modified
- `data/reminders.csv`
- `src/scheduler.py`

### Suggested Commit Message
```text
feat(scheduler): implement due reminder detection, duplicate prevention logic, and continuous polling loop
```

### Visual Evidence to Capture
- Terminal output showing single-cycle execution evaluating due reminders.
- `data/reminders.csv` showing updated status from `PENDING` to `SIMULATED`.

---

## 🗓️ Day 5: Central Logging, Audit Reports & Test Automation

### Objectives
Establish complete system observability, automated audit trail exports, and comprehensive test coverage.

### Tasks Completed
- Build `src/logger_config.py` with structured file logging to `logs/automation.log` and console output.
- Build `src/reports.py` generating `outputs/email_report.csv` and textual KPI summaries in `outputs/execution_summary.txt`.
- Author test suite in `tests/test_project.py` covering email validation, contact parsing, deduplication, template rendering, dry-run safety, and scheduler logic.
- Execute test runner, verify 100% test pass rate, and document in `docs/TEST_RESULTS.md`.

### Files Created / Modified
- `src/logger_config.py`
- `src/reports.py`
- `tests/test_project.py`
- `docs/TEST_RESULTS.md`
- `outputs/email_report.csv`
- `outputs/execution_summary.txt`
- `logs/automation.log`

### Suggested Commit Message
```text
test(core): add automated unittest suite, central logging to logs/automation.log, and audit reporting
```

### Visual Evidence to Capture
- Screenshot of terminal running `python -m unittest discover tests -v` showing 9 tests passing.
- Screenshot of `outputs/email_report.csv` and `outputs/execution_summary.txt`.

---

## 🗓️ Day 6: User Interface, Documentation & Final Polish

### Objectives
Deliver an accessible user interface, interactive dashboard, complete academic documentation, and GitHub submission bundle.

### Tasks Completed
- Build interactive CLI entry point in `main.py` with 7-option menu and CLI flags (`--once`, `--preview`, `--report`, `--scheduler`).
- Build visual web dashboard in `dashboard.py` with Streamlit KPI cards and interactive tables.
- Generate visual architecture SVG diagrams in `images/` and author `images/SCREENSHOT_CHECKLIST.md`.
- Author complete GitHub `README.md`, academic `docs/PROJECT_REPORT.md`, and 30-question `docs/INTERVIEW_QUESTIONS.md`.
- Complete final verification audit in `docs/FINAL_COMPLETION_REPORT.md`.

### Files Created / Modified
- `main.py`
- `dashboard.py`
- `README.md`
- `docs/PROJECT_REPORT.md`
- `docs/INTERVIEW_QUESTIONS.md`
- `docs/SIX_DAY_PROOF_PLAN.md`
- `docs/FINAL_COMPLETION_REPORT.md`
- `images/architecture_diagram.svg`
- `images/SCREENSHOT_CHECKLIST.md`

### Suggested Commit Message
```text
docs(submission): complete CLI interface, Streamlit dashboard, comprehensive project report, and viva guide
```

### Visual Evidence to Capture
- Screenshot of `main.py` interactive terminal menu.
- Screenshot of Streamlit dashboard running in browser (`http://localhost:8501`).
- Final project directory overview.
