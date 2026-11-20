# 📸 Visual Artifacts & Screenshot Capture Guide

This guide details the exact visual evidence required for project demonstration, academic submission, and GitHub portfolio presentation.

---

## 🖼️ Included Architecture & Workflow Diagrams (SVGs)

The following diagrams have been generated in `images/`:
1. `architecture_diagram.svg` — High-level system architecture, CSV data pipeline, scheduler ticker, and dual-mode dispatch engine.
2. `data_flow_diagram.svg` — Step-by-step data transformation from CSV contacts & reminders to rendered EmailMessage and audit logs.
3. `terminal_preview_mockup.svg` — Visual layout of the interactive CLI main menu and dry-run execution output.

---

## 📷 Exact Manual Screenshot Checklist (Windows Snipping Tool)

Use **Windows Key + Shift + S** to capture the following 11 project evidence screenshots. Save each file in `Python_Email_Automation_Reminder_System/images/` using the exact filename specified below:

| # | Screenshot Filename | View / Command to Capture | Description / What to Show |
|---|---|---|---|
| **1** | `01_project_structure.png` | VS Code Explorer or Terminal `tree /F` | Full file tree of `Python_Email_Automation_Reminder_System/` showing `data/`, `src/`, `templates/`, `outputs/`, `logs/`, `docs/`, `tests/`. |
| **2** | `02_contacts_csv.png` | `data/contacts.csv` in text editor or Excel | The 6 sample contacts showing `contact_id`, `name`, `email` (`@example.com`), `department`, and `company`. |
| **3** | `03_reminders_csv.png` | `data/reminders.csv` in text editor or Excel | The 6 sample reminders showing `reminder_id`, `contact_id`, `reminder_type`, `scheduled_datetime`, and `status`. |
| **4** | `04_email_template.png` | `templates/reminder_template.txt` | The template showing `{name}`, `{company}`, `{department}`, `{subject}`, `{message}` placeholders. |
| **5** | `05_email_preview.png` | Terminal: `python main.py --preview` | Rendered personalized email output for Alice Morgan & Brian Patel. |
| **6** | `06_dry_run_terminal.png` | Terminal: `python main.py --once` | CLI execution banner, active mode `SIMULATION (Safe Dry-Run)`, and 3 processed dispatches marked `[SIMULATED]`. |
| **7** | `07_scheduler_output.png` | Terminal: `python main.py --scheduler` | Continuous scheduler loop polling every 10 seconds and graceful shutdown on Ctrl+C. |
| **8** | `08_automation_logs.png` | `logs/automation.log` | Timestamped structured log entries showing contacts loaded, dry-run simulation, and cycle completions. |
| **9** | `09_generated_csv_report.png` | `outputs/email_report.csv` | Audit CSV report with `reminder_id`, `recipient`, `scheduled_datetime`, `mode`, `status=SIMULATED`. |
| **10** | `10_streamlit_dashboard.png` | Browser: `http://localhost:8501` | Streamlit web dashboard showing KPI metric cards, tabs, and dry-run notice banner. |
| **11** | `11_test_results.png` | Terminal: `python -m unittest discover ...` | Terminal test runner showing `Ran 9 tests ... OK`. |

---

## 💡 Tips for Clean Portfolio Screenshots
- Use Windows Terminal with a clean dark theme.
- Ensure terminal width is at least 100 columns for clean table alignment.
- Keep the Streamlit browser window at 1920x1080 resolution.
