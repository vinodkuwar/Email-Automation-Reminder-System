# 📘 Academic Project Report: Email Automation & Reminder System

---

## 1. Title Page Content

- **Project Title:** Email Automation & Reminder System
- **Domain:** Software Engineering / Workflow Automation / Cloud Communication Systems
- **Language / Core Tech:** Python 3.13, Pandas, smtplib, EmailMessage, Streamlit
- **Author / Developer:** Senior Automation Engineer & Student Candidate
- **Academic Year:** 2026 – 2027
- **Submission Type:** Capstone Project / Course Evaluation / Internship Proof-of-Work

---

## 2. Abstract

Manual email reminder workflows are prone to human oversight, scheduling bottlenecks, inconsistent communication, and operational inefficiencies. This project presents the **Email Automation & Reminder System**, an autonomous, Python-driven automation pipeline designed to schedule, personalize, dispatch, and track time-sensitive email notifications.

The system features an offline-first, local CSV architecture that decouples recipient directories (`data/contacts.csv`) from reminder tasks (`data/reminders.csv`). It implements rigorous schema validation, RFC 5322 email verification, and duplicate contact filtering. An external template engine personalizes message content dynamically across multiple reminder types (meetings, payments, webinars, task deadlines, and follow-ups). 

A critical safety design feature is the **default Dry-Run Simulation Mode**, which generates compliant `EmailMessage` objects and comprehensive audit logs without contacting external mail servers. When explicitly configured, a **Real SMTP Mode** provides encrypted TLS delivery over standard SMTP ports. An autonomous background scheduler continuously evaluates due timestamps and updates task statuses atomically to prevent duplicate dispatches. Automated CSV and text audit reports (`outputs/`) provide full transparency. The application is accessible via an interactive command-line interface (CLI) and an optional Streamlit web dashboard.

---

## 3. Introduction

In modern business and organizational settings, timely communication is critical. Organizations routinely notify employees, clients, and partners regarding project deadlines, upcoming conferences, financial dues, and team syncs. Executing these dispatches manually via standard email clients introduces several failure modes:
1. Significant labor overhead and manual data transcription errors.
2. Missed deadlines when employees forget to send notices at exact designated hours.
3. Inability to audit delivery attempts systematically.

Automated reminder pipelines solve these challenges by programmatically bridging structured data stores with email transmission protocols. This project establishes an enterprise-grade, beginner-friendly Python solution that emphasizes code clarity, modularity, and safety.

---

## 4. Problem Statement

Organizations require a lightweight, dependable mechanism to schedule and send recurring or one-off email reminders without relying on expensive, complex SaaS platforms (such as Mailchimp or SendGrid) for internal notifications. 

Key challenges addressed include:
- Ingestion of contact lists with malformed email addresses and duplicate entries.
- Synchronization of reminders with contacts without complex relational database setups.
- Safe local testing without accidentally spamming real mailboxes during development.
- Preventing duplicate reminder dispatches if the scheduler restarts or runs concurrently.
- Providing structured audit logs for administrative review.

---

## 5. Objectives

The primary objectives of this project are:
1. **Data Ingestion & Integrity:** Ingest contacts and reminders from CSV files, validating required fields, RFC email syntax, and eliminating duplicate records.
2. **Dynamic Personalization:** Design an editable text template with placeholders (`{name}`, `{company}`, `{department}`, `{subject}`, `{message}`) that gracefully handles missing attributes.
3. **Safety-First Dispatch Engine:** Implement a dual-mode dispatcher that defaults to **Dry-Run Simulation**, recording simulated success without external network calls, while offering an optional **Real SMTP Mode** with TLS encryption.
4. **Autonomous Scheduler:** Build a local scheduling ticker that detects due reminders (`scheduled_datetime <= now()`), triggers dispatch, and updates reminder statuses atomically to prevent duplicate sending.
5. **Observability & Reporting:** Record structured, timestamped logs to `logs/automation.log` and generate exportable reports in `outputs/` (`email_report.csv` and `execution_summary.txt`).
6. **Dual Interface:** Deliver both a student-friendly interactive CLI (`main.py`) and an optional visual web dashboard (`dashboard.py`).

---

## 6. Existing System

Traditional approaches rely on either:
- **Manual Email Clients:** Composing reminders individually via desktop or web interfaces (e.g., Outlook, Gmail). This approach does not scale, lacks scheduling granularity, and relies entirely on human memory.
- **Heavy Enterprise CRMs:** Systems like Salesforce or HubSpot require complex API integrations, expensive per-seat licensing, cloud infrastructure, and continuous internet connectivity even during basic development and testing.

### Weaknesses of Existing Solutions
- High operational and financial costs.
- Risk of accidental bulk emailing during staging or development.
- Steep learning curve for small teams or academic demonstrations.

---

## 7. Proposed System

The proposed system is a modular, standalone Python software package that operates locally on flat CSV files:
- **Zero-Dependency Resilience:** Executes directly on the Python Standard Library (`csv`, `email`, `smtplib`, `datetime`, `logging`) while seamlessly leveraging Pandas and Streamlit when installed.
- **Deterministic Simulation:** Eliminates the risk of unintended external emails by making dry-run the default mode.
- **Relational Integrity on Flat Files:** Links reminders to contacts using clean foreign key mapping (`contact_id`).
- **Comprehensive Audit Trail:** Logs every evaluation step and exports structured CSV audit files.

---

## 8. Architecture & Data Flow

```text
┌──────────────────────┐      ┌──────────────────────┐
│  data/contacts.csv   │      │ data/reminders.csv   │
└──────────┬───────────┘      └──────────┬───────────┘
           │                             │
           ▼                             ▼
┌────────────────────────────────────────────────────┐
│      src/contacts.py & src/scheduler.py            │
│  - Validate RFC email syntax                       │
│  - Filter duplicate contacts                       │
│  - Identify due items: scheduled_time <= now()     │
└──────────────────────────┬─────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────┐
│             src/templates.py Engine                │
│  - Load templates/reminder_template.txt            │
│  - Substitute {name}, {subject}, {message}, etc.   │
└──────────────────────────┬─────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────┐
│            src/email_sender.py (Dual-Mode)         │
│  - Formulate RFC 5322 EmailMessage                 │
│  ├─► [DEFAULT] Dry-Run Mode: SIMULATED (no SMTP)   │
│  └─► [OPT-IN]  Real SMTP Mode: TLS 587 (Gmail/host)│
└──────────────────────────┬─────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────┐
│          Audit, Reporting & Persistence            │
│  - Update data/reminders.csv status to SIMULATED   │
│  - Append to outputs/email_report.csv              │
│  - Write outputs/execution_summary.txt             │
│  - Record to logs/automation.log                   │
└────────────────────────────────────────────────────┘
```

---

## 9. Technologies Used

- **Programming Language:** Python 3.13 (compatible with 3.10+)
- **Standard Library Modules:**
  - `csv` / `io`: Tabular data parsing and serialization.
  - `email.message.EmailMessage`: RFC 5322 MIME message construction.
  - `smtplib`: Simple Mail Transfer Protocol client with TLS.
  - `datetime` / `time`: Time delta calculations, scheduling timestamps.
  - `logging`: File and console audit tracking.
  - `re`: Regular expressions for email format verification.
  - `unittest`: Automated unit and integration testing.
  - `argparse`: Command-line interface argument parsing.
- **Optional External Libraries:**
  - `pandas`: Vectorized tabular manipulation.
  - `schedule`: Human-readable task scheduler API.
  - `python-dotenv`: Environment variable management.
  - `streamlit`: Visual web dashboard.

---

## 10. Module Descriptions

| Module | Location | Primary Responsibilities |
|---|---|---|
| **Contact Ingestion** | `src/contacts.py` | Loads CSV, validates email patterns, enforces required fields, detects duplicate IDs/emails, and normalizes optional values. |
| **Template Engine** | `src/templates.py` | Reads template file, applies `SafeDict` placeholder substitution, and prevents `KeyError` crashes on missing tokens. |
| **Email Service** | `src/email_sender.py` | Formulates `EmailMessage` headers and body, executes simulated delivery in dry-run mode, and connects via TLS in real SMTP mode. |
| **Scheduler Engine** | `src/scheduler.py` | Evaluates due timestamps, matches contacts to reminders, updates reminder CSV status to avoid duplicates, and manages polling loops. |
| **Reporting Engine** | `src/reports.py` | Exports structured CSV dispatch records and creates formatted text execution summaries with delivery metrics. |
| **Logging Config** | `src/logger_config.py` | Implements cross-platform structured logging to `logs/automation.log` and standard output. |
| **File Utilities** | `src/file_utils.py` | Provides resilient file read/write routines supporting sandboxed or restricted OS environments. |
| **CLI Controller** | `main.py` | Provides a 7-option interactive menu and CLI argument flags (`--once`, `--preview`, `--scheduler`, `--report`). |
| **Web Dashboard** | `dashboard.py` | Streamlit user interface featuring KPI metric cards, data tables, live preview, and report downloads. |

---

## 11. Workflow & Lifecycle

1. **Initialization:** Configuration is loaded from `.env` (defaulting `EMAIL_MODE=dry_run`).
2. **Ingestion & Validation:** Contacts are parsed from `data/contacts.csv`. Malformed emails and duplicate IDs are filtered out and logged.
3. **Queue Evaluation:** Reminders are read from `data/reminders.csv`. Reminders with status `PENDING` are checked against current wall-clock time (`scheduled_datetime <= datetime.now()`).
4. **Rendering:** For each due reminder, the contact is looked up via `contact_id`, and `reminder_template.txt` is personalized.
5. **Dispatch:** 
   - Under `dry_run`: A unique Message-ID is generated, simulation details are logged, and status is marked `SIMULATED`.
   - Under `real`: The system authenticates with the SMTP server over TLS and dispatches the email, marking status `SENT`.
6. **State Persistence:** The reminder's status is updated in `data/reminders.csv` to ensure it is never reprocessed.
7. **Reporting:** Audit records are written to `outputs/email_report.csv` and summarized in `outputs/execution_summary.txt`.

---

## 12. Implementation Details

### Contact Validation Algorithm
```python
if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
    reject_row("Invalid email syntax")
if email in seen_emails or contact_id in seen_ids:
    reject_row("Duplicate contact")
```

### Safe Template Substitution
```python
class SafeDict(dict):
    def __missing__(self, key):
        return f"[{key.upper()}_NOT_PROVIDED]"

rendered_body = template_content.format_map(SafeDict(context))
```

### Duplicate Dispatch Prevention
```python
for reminder in reminders:
    if reminder["status"] == "PENDING" and parse_datetime(reminder["scheduled_datetime"]) <= now:
        result = email_service.dispatch_email(...)
        reminder["status"] = result["status"]  # Transitions to SIMULATED or SENT
save_reminders_csv(reminders)
```

---

## 13. Simulation (Dry-Run Mode)

Simulation mode is the cornerstone of this system's safety model:
- **Zero Socket Connections:** Does not attempt to contact `smtp.gmail.com` or open external network ports.
- **Authentic Payload Generation:** Generates real RFC 5322 message objects with MIME headers, boundaries, and timestamps.
- **Accurate Metric Tracking:** Records simulated latency and generates unique tracking IDs (`<uuid@domain>`).
- **Academic Transparency:** Explicitly labels records as `SIMULATED` rather than claiming real delivery.

---

## 14. Testing & Verification

Automated testing was conducted using Python's built-in `unittest` framework (`tests/test_project.py`).

### Test Coverage Highlights
- **Email Regex:** Validated multiple standard and non-standard email strings.
- **Schema Validation:** Ingested test CSV files with missing required headers.
- **Deduplication:** Confirmed identical emails and IDs are filtered.
- **Template Safety:** Verified missing placeholder keys do not raise exceptions.
- **Dry-Run Integrity:** Confirmed no SMTP network calls occur during simulation.
- **State Transition:** Verified `PENDING` transitions to `SIMULATED`, and re-running immediately evaluates 0 due items.

**Test Outcome:** 9 tests executed, 9 tests passed, 0 failures, 0 errors.

---

## 15. Results

During verified test runs:
- **6 sample contacts** across 6 departments were loaded with 100% data validation.
- **6 sample reminders** (Meeting, Payment, Webinar, Task deadline, Follow-up) were tracked.
- **3 due reminders** were processed in a single cycle and marked `SIMULATED`.
- **0 duplicate dispatches** occurred on subsequent scheduler runs.
- **100% delivery success rate** was logged in `outputs/execution_summary.txt` and `outputs/email_report.csv`.

---

## 16. Limitations

1. **Storage Concurrency:** Flat CSV files do not support high-concurrency multi-threaded writes without explicit file locking.
2. **SMTP Throttling:** In Real SMTP mode, high-frequency dispatches must adhere to provider rate limits (e.g., Gmail's daily dispatch caps).
3. **Local Scheduler Daemon:** The continuous scheduler runs locally on the host machine and stops if the terminal process or host system is terminated.

---

## 17. Future Scope

1. **Database Backend:** Migrate flat CSV storage to SQLite or PostgreSQL with connection pooling.
2. **HTML Email Templates:** Support rich responsive HTML email templates with inline CSS and attachments.
3. **Distributed Task Queue:** Integrate Celery or Redis for distributed, scalable task dispatching.
4. **Cloud Deployment:** Containerize with Docker and deploy to AWS Elastic Beanstalk or Google Cloud Run.
5. **Two-Way Webhooks:** Integrate SendGrid or Mailgun webhook endpoints to listen for open rates, bounces, and click events.

---

## 18. Conclusion

The **Email Automation & Reminder System** successfully demonstrates a production-grade, educational software architecture for automated notification workflows. By prioritizing safety through its default Dry-Run Simulation mode, enforcing rigorous data validation, avoiding third-party dependency lock-in, and providing complete auditability, the project delivers a reliable, student-friendly, and enterprise-relevant software engineering solution.

---

## 19. References

1. Python Software Foundation. *email — An email and MIME handling package*. Python 3.13 Documentation, 2026.
2. Python Software Foundation. *smtplib — SMTP protocol client*. Python 3.13 Documentation, 2026.
3. Resnick, P. *Internet Message Format*. RFC 5322, Internet Engineering Task Force (IETF), 2008.
4. McKinney, Wes. *Data Structures for Statistical Computing in Python*. Proceedings of the 9th Python in Science Conference, 2010.
5. Streamlit Inc. *Streamlit Documentation — The fastest way to build and share data apps*, 2026.
