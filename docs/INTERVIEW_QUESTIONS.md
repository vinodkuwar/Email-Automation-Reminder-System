# 🎯 Viva & Interview Preparation Guide: Email Automation & Reminder System

This guide contains **30 carefully structured interview questions and answers** across three levels: Basic Fundamentals, Project Technical Implementation, and Real-World Scenarios. It is designed to prepare students and junior engineers for technical interviews and project defense evaluations.

---

## 📌 Part 1: Basic Fundamentals (10 Questions)

### Q1: What is the purpose of the `csv` module in Python, and how does `csv.DictReader` differ from `csv.reader`?
**Answer:** The standard library `csv` module provides parsing and writing capabilities for Comma-Separated Value files. While `csv.reader` returns each row as a raw list of strings indexed by integer column position (`row[0]`, `row[1]`), `csv.DictReader` maps each row's values to a dictionary keyed by the column headers in the first line (`row['email']`, `row['name']`). This improves code readability and prevents index-out-of-range errors when column orders change.

### Q2: Why is the `datetime` module essential for scheduling reminders?
**Answer:** The `datetime` module provides classes for manipulating dates and times. In a reminder system, it allows comparing string timestamps by parsing them into `datetime` objects (`datetime.strptime()`) and evaluating whether `scheduled_time <= datetime.now()` to determine if a reminder is currently due for dispatch.

### Q3: How do you validate an email address in Python using regular expressions?
**Answer:** Email addresses are validated by compiling a regular expression pattern using Python's `re` module (e.g., `re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")`). Testing a string with `bool(pattern.match(email.strip()))` confirms whether the email adheres to standard RFC formatting (local-part, `@` symbol, and valid domain).

### Q4: What is an environment variable, and why is the `.env` file never committed to GitHub?
**Answer:** Environment variables are key-value pairs managed outside the source code by the operating system or runtime. A `.env` file holds sensitive configuration parameters like SMTP passwords and API tokens. Committing `.env` to GitHub exposes credentials publicly, which can lead to account hijacking, spam blacklisting, and security breaches. Instead, a sanitized `.env.example` is committed with empty placeholders.

### Q5: What is the difference between Python's standard `logging` module and simple `print()` statements?
**Answer:** `print()` sends unformatted strings directly to standard output without metadata. Python's `logging` module provides severity levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`), automatic timestamps, module identifiers, and multi-destination routing (e.g., writing simultaneously to the console and a persistent disk file like `logs/automation.log`).

### Q6: What is a "dry-run" mode and why is it important in automation systems?
**Answer:** Dry-run (or simulation) mode allows an automation program to execute its complete business logic, validations, formatting, and scheduling without triggering destructive or real-world external side-effects (such as connecting to an external SMTP server or emailing real recipients). It ensures safe verification, testing, and debugging.

### Q7: How does string formatting with `.format_map()` work in template rendering?
**Answer:** In Python, string formatting with `.format_map(mapping)` substitutes `{key}` placeholders in a template with values from a provided dictionary. When combined with a custom dictionary class that defines `__missing__(self, key)`, missing placeholders can be handled safely without crashing the program with a `KeyError`.

### Q8: What does `if __name__ == "__main__":` do in Python scripts?
**Answer:** It checks whether the Python file is being executed directly as the top-level script (in which case `__name__` equals `"__main__"`), or imported as a module into another script. It allows a file to serve both as an importable library and a standalone executable program.

### Q9: What is the role of `try-except` blocks in robust file operations?
**Answer:** File operations can fail due to missing files (`FileNotFoundError`), permission restrictions (`PermissionError`), or OS-level locking. Wrapping file reads and writes in `try-except` blocks allows the program to catch expected exceptions, log informative error messages, and execute fallback procedures rather than abruptly crashing.

### Q10: What is the purpose of `requirements.txt` in a Python project?
**Answer:** `requirements.txt` lists the external packages and libraries required to run a Python application (such as `pandas`, `schedule`, `python-dotenv`, and `streamlit`). It enables other developers and deployment pipelines to reproduce the exact environment using `pip install -r requirements.txt`.

---

## 💻 Part 2: Project-Related Technical Questions (10 Questions)

### Q11: How does this project prevent the same reminder from being sent repeatedly?
**Answer:** When reminders are loaded from `data/reminders.csv`, each record contains a `status` field. The scheduler only processes reminders whose status is strictly `PENDING`. As soon as a due reminder is dispatched (or simulated), its status is updated in-memory to `SIMULATED` or `SENT` and atomically written back to `data/reminders.csv`. On subsequent polling cycles, the scheduler skips all non-pending records.

### Q12: Why did you use `email.message.EmailMessage` instead of the legacy `email.mime` modules?
**Answer:** Python 3.6+ introduced `email.message.EmailMessage` as the modern replacement for legacy `MIMEMultipart` and `MIMEText` classes. It provides a cleaner, dictionary-like interface for setting headers (`msg['To']`, `msg['Subject']`), handles character encodings (UTF-8) automatically, and simplifies body assignment with `msg.set_content()`.

### Q13: How does your implementation handle optional third-party packages like Pandas?
**Answer:** The project implements graceful degradation. When loading CSVs in `src/contacts.py` and `src/scheduler.py`, the code uses a `try: import pandas as pd ... except ImportError:` pattern. If Pandas is installed, it leverages high-speed DataFrames; if Pandas is not present, it automatically falls back to Python's built-in `csv.DictReader`. This guarantees the application runs out of the box with zero external dependencies.

### Q14: Explain the difference between `process_due_reminders_once()` and `run_continuous_scheduler()`.
**Answer:** `process_due_reminders_once()` executes an immediate, single pass: it checks currently pending reminders against the current timestamp, dispatches any that are due, updates their status, writes reports, and terminates. `run_continuous_scheduler()` enters an ongoing polling loop (every 10 seconds) that runs indefinitely until stopped with Ctrl+C (`KeyboardInterrupt`), simulating a persistent production daemon.

### Q15: How does the email service authenticate with Gmail in Real SMTP mode?
**Answer:** In Real SMTP mode, `src/email_sender.py` creates an instance of `smtplib.SMTP(host, port)`. It issues `server.ehlo()`, initiates Transport Layer Security via `server.starttls()`, re-issues `server.ehlo()`, and invokes `server.login(username, app_password)`. It requires a 16-character Google App Password rather than a standard account password because Google disables standard password authentication under 2-Step Verification.

### Q16: How does the system detect duplicate contacts?
**Answer:** During CSV ingestion in `src/contacts.py`, the system maintains two hash sets: `seen_emails` and `seen_ids`. As each row is processed, the contact's email (normalized to lowercase) and contact ID are checked against these sets. If either exists, the record is flagged as a duplicate, logged, and appended to `invalid_records` rather than being ingested into the active directory.

### Q17: What columns are included in `outputs/email_report.csv` and why?
**Answer:** The report includes: `reminder_id`, `contact_id`, `recipient`, `subject`, `scheduled_datetime`, `execution_datetime`, `mode` (`dry_run` vs `real`), `status` (`SIMULATED`, `SENT`, `FAILED`), and `error_message`. These columns provide an immutable audit trail necessary for compliance, delivery debugging, and SLA verification.

### Q18: What mechanism handles graceful shutdown when a user presses Ctrl+C during continuous scheduling?
**Answer:** In `src/scheduler.py`, the polling loop `while True:` is wrapped in a `try...except KeyboardInterrupt:` block. When the user presses Ctrl+C, Python raises a `KeyboardInterrupt` exception. The exception is caught cleanly, writes a shutdown notification to `logs/automation.log`, prints a user-friendly termination message, and exits without unhandled tracebacks.

### Q19: Why does the system write UTF-8 encoded files with `utf-8-sig` compatibility?
**Answer:** On Windows systems, tools like Microsoft Excel and PowerShell often write CSV files with a Byte Order Mark (`\ufeff`) header. If read with standard `utf-8`, the first column name becomes `\ufeffcontact_id` instead of `contact_id`. Reading with `utf-8-sig` automatically strips the BOM header, ensuring seamless cross-platform compatibility between Windows, macOS, and Linux.

### Q20: How does the Streamlit dashboard interact with the core Python backend?
**Answer:** `dashboard.py` acts as a presentation layer that directly imports backend service functions (`load_contacts_csv`, `load_reminders_csv`, `process_due_reminders_once`, and `email_service`). It does not duplicate business logic; instead, it renders interactive UI controls (metrics, dataframes, dropdowns, and download buttons) on top of the shared CSV data layer.

---

## 🛡️ Part 3: Scenario-Based Engineering Questions (10 Questions)

### Q21: Suppose a contact CSV has 100,000 rows. How would you optimize the current implementation?
**Answer:** For massive CSVs, loading the entire dataset into Python memory can lead to excessive RAM consumption. I would optimize this by:
1. Processing the file in chunks using `pandas.read_csv(chunksize=5000)` or Python generator iterators.
2. Migrating contact storage from flat CSV files to an indexed SQLite or PostgreSQL database.
3. Indexing the `email` and `contact_id` columns with unique B-tree indexes to make duplicate lookups $O(1)$ rather than $O(N)$.

### Q22: What happens if the network disconnects in the middle of sending emails in Real SMTP mode?
**Answer:** In `src/email_sender.py`, each dispatch call is enclosed in a `try-except` block catching `smtplib.SMTPException` and general `Exception`. If network connectivity drops, the exception is caught, logged with full diagnostics, and returns a dictionary with `status="FAILED"` and the exact error description. The scheduler updates the reminder's status to `FAILED`, preventing subsequent reminders in the batch from crashing the application.

### Q23: How would you prevent SMTP rate-limiting or getting blacklisted when sending thousands of emails?
**Answer:** Sending emails too rapidly triggers SMTP provider rate limits and spam filters. To prevent this:
1. Implement rate limiting (e.g., maximum 5 emails per second using `time.sleep()`).
2. Implement batching with exponential backoff retry strategies (e.g., using Celery or Redis queues).
3. Authenticate sender domains using SPF (Sender Policy Framework), DKIM (DomainKeys Identified Mail), and DMARC DNS records.

### Q24: What if a user accidentally edits `reminder_template.txt` and introduces a typo in a placeholder like `{nme}`?
**Answer:** In `src/templates.py`, the `render_template` function uses a custom `SafeDict` class with `__missing__(key)`. When an unrecognized placeholder like `{nme}` is encountered, Python does not crash with a `KeyError`. Instead, `__missing__` safely replaces it with fallback text (`[NME_NOT_PROVIDED]`), logs a warning, and allows the remaining valid placeholders (`{subject}`, `{message}`) to populate normally.

### Q25: How would you deploy this Python reminder system to a production cloud server?
**Answer:** I would:
1. Containerize the application using a lightweight `Dockerfile` (e.g., `python:3.11-slim`).
2. Manage environment variables using Docker Secrets or cloud secret managers (AWS Secrets Manager, Google Secret Manager).
3. Run the scheduler as a systemd background service or Kubernetes CronJob.
4. Mount persistent volumes for the `data/`, `logs/`, and `outputs/` directories to retain state across container restarts.

### Q26: Why is storing plain-text passwords in source code considered a critical vulnerability, and how does your project enforce security?
**Answer:** Hardcoded credentials can be accidentally committed to public repositories, extracted via reverse engineering, or viewed in system process listings. This project enforces security by:
1. Reading credentials exclusively via `os.getenv()` from `.env`.
2. Including `.env` in `.gitignore`.
3. Never printing `SMTP_PASS` or raw credentials in logs or console output.
4. Masking sender usernames in UI previews.

### Q27: How can you verify that no real emails were sent during an evaluation session?
**Answer:** Verification can be confirmed by:
1. Checking `.env`: `EMAIL_MODE` is set to `dry_run` (the default).
2. Inspecting `outputs/email_report.csv`: every processed row has `mode="dry_run"` and `status="SIMULATED"`.
3. Reviewing `logs/automation.log`: log messages explicitly say `[SIMULATION] Generated reminder email for ... (No external SMTP server was contacted)`.
4. The absence of network traffic to port 587 or 465.

### Q28: How would you extend this system to support HTML-formatted emails with logos and styled buttons?
**Answer:** Python's `EmailMessage` class supports MIME multipart alternatives via `msg.add_alternative(html_content, subtype='html')`. I would create an `email_template.html` file with CSS styling and inline placeholders, render it using Jinja2 or string replacement, and attach both the plain-text fallback and HTML payload to the message before dispatch.

### Q29: What happens if a reminder's `scheduled_datetime` string is invalid or corrupted (e.g., "tomorrow at 3")?
**Answer:** In `src/scheduler.py`, the `parse_datetime()` function attempts to parse the string against supported ISO and timestamp formats. If parsing fails, it returns `None`. The scheduler logs a warning (`Reminder has invalid date`), skips dispatching the unparseable reminder, and continues processing remaining valid reminders without terminating the execution cycle.

### Q30: If you were presenting this project to a hiring manager, what key engineering decisions would you highlight?
**Answer:** I would highlight:
1. **Safety-First Design**: Defaulting to dry-run simulation mode to prevent unintended external dispatches.
2. **Zero-Dependency Resilience**: Writing clean fallback logic so the project runs immediately on Python standard library (`csv`, `email`, `smtplib`) while seamlessly upgrading to Pandas and Streamlit when present.
3. **Data Integrity**: Implementing duplicate detection, schema validation, and atomic CSV updates to prevent double-sending.
4. **Comprehensive Observability**: Timestamped file and console logging coupled with automated CSV audit reports and Markdown documentation.
