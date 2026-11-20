"""
Streamlit Web Dashboard for Email Automation & Reminder System
Provides visual KPI metrics, contact exploration, live email previews,
one-click dry-run execution, and report downloads.
"""

import sys
from pathlib import Path

# Ensure src modules are resolvable
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import streamlit as st
except ImportError:
    print("\n[INFO] Streamlit is not currently installed in this Python environment.")
    print("To launch this interactive web dashboard, run:")
    print("  pip install streamlit")
    print("  streamlit run dashboard.py\n")
    sys.exit(0)

from src.contacts import load_contacts_csv
from src.scheduler import load_reminders_csv, process_due_reminders_once
from src.templates import load_template_file, render_template
from src.email_sender import email_service

# Page Configuration
st.set_page_config(
    page_title="Email Automation & Reminder Dashboard",
    page_icon="📬",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title { font-size: 28px; font-weight: 800; color: #4F46E5; margin-bottom: 2px; }
    .subtitle { font-size: 14px; color: #64748B; margin-bottom: 20px; }
    .mode-box-dry { background-color: #FEF3C7; border-left: 5px solid #F59E0B; padding: 12px 16px; border-radius: 6px; font-size: 13px; color: #92400E; margin-bottom: 20px; }
    .mode-box-real { background-color: #D1FAE5; border-left: 5px solid #10B981; padding: 12px 16px; border-radius: 6px; font-size: 13px; color: #065F46; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# Title & Description
st.markdown('<div class="main-title">📬 Email Automation & Reminder System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Autonomous Reminder Dispatcher • Template Engine • Audit Reports</div>', unsafe_allow_html=True)

# Mode Notification
if email_service.is_dry_run():
    st.markdown('<div class="mode-box-dry">🛡️ <strong>DEFAULT ACTIVE: DRY-RUN SIMULATION MODE</strong>. No actual emails will be sent to external mailboxes. All actions are simulated and recorded safely.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="mode-box-real">⚡ <strong>REAL SMTP MODE ACTIVE</strong>. External emails are configured to be sent via your SMTP credentials.</div>', unsafe_allow_html=True)

# Load Data
contacts, invalid, contacts_summary = load_contacts_csv()
reminders = load_reminders_csv()

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)

total_contacts = len(contacts)
pending_count = sum(1 for r in reminders if r.get("status", "").upper() == "PENDING")
simulated_count = sum(1 for r in reminders if r.get("status", "").upper() == "SIMULATED")
sent_count = sum(1 for r in reminders if r.get("status", "").upper() == "SENT")

col1.metric("Total Valid Contacts", total_contacts, f"{contacts_summary['invalid_count']} invalid")
col2.metric("Pending Reminders", pending_count)
col3.metric("Simulated Deliveries", simulated_count)
col4.metric("Real Sent Deliveries", sent_count)

st.divider()

# Navigation Tabs
tab_overview, tab_contacts, tab_reminders, tab_preview, tab_process, tab_reports = st.tabs([
    "📊 Overview", "👥 Contacts", "⏰ Reminders", "✉️ Live Preview", "🚀 Process Reminders", "📑 Reports"
])

with tab_overview:
    st.subheader("System Architecture & Data Flow")
    st.markdown("""
    This Python automation engine operates on a local CSV data pipeline:
    1. **Contacts Source**: `data/contacts.csv` holds verified recipient information with email validation and deduplication.
    2. **Reminders Queue**: `data/reminders.csv` stores scheduled tasks with target timestamps and delivery statuses.
    3. **Template Engine**: `templates/reminder_template.txt` provides dynamic placeholder replacement.
    4. **Safety Controller**: Dry-run mode is active by default to prevent accidental live email dispatches.
    5. **Audit Logs**: Generates `outputs/email_report.csv` and `outputs/execution_summary.txt`.
    """)

with tab_contacts:
    st.subheader("Contact Directory")
    st.dataframe(contacts, use_container_width=True)
    if invalid:
        st.warning(f"Detected {len(invalid)} rejected invalid record(s) in CSV:")
        st.json(invalid)

with tab_reminders:
    st.subheader("Managed Reminders Queue")
    st.dataframe(reminders, use_container_width=True)

with tab_preview:
    st.subheader("Personalized Email Preview")
    if contacts and reminders:
        selected_rem = st.selectbox("Select Reminder to Preview", [f"{r['reminder_id']}: {r['subject']}" for r in reminders])
        rem_id = selected_rem.split(":")[0]
        rem = next(r for r in reminders if r['reminder_id'] == rem_id)
        cid = rem.get("contact_id")
        contact = next((c for c in contacts if c["contact_id"] == cid), contacts[0])

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

        template_text = load_template_file()
        rendered_email = render_template(template_text, context)

        st.text_area("Rendered Personalized Message", rendered_email, height=300)
    else:
        st.info("Contacts or reminders are empty.")

with tab_process:
    st.subheader("Execute Scheduled Reminders")
    st.write("Click below to evaluate and dispatch all currently due reminders.")
    
    if st.button("🚀 Trigger Due Reminders Cycle Now", type="primary"):
        with st.spinner("Processing due reminders..."):
            records, summary = process_due_reminders_once()
            if records:
                st.success(f"Successfully processed {len(records)} due reminder(s)!")
                st.dataframe(records)
            else:
                st.info("No reminders were currently due for dispatch.")

with tab_reports:
    st.subheader("Execution & Audit Reports")
    csv_file = PROJECT_ROOT / "outputs" / "email_report.csv"
    txt_file = PROJECT_ROOT / "outputs" / "execution_summary.txt"

    if csv_file.exists():
        with open(csv_file, "r", encoding="utf-8") as f:
            csv_data = f.read()
        st.download_button("📥 Download email_report.csv", csv_data, file_name="email_report.csv", mime="text/csv")
        st.text("Latest CSV Report Preview:")
        st.code(csv_data[:1000], language="csv")
    else:
        st.info("Run a processing cycle to generate outputs/email_report.csv")

    if txt_file.exists():
        with open(txt_file, "r", encoding="utf-8") as f:
            txt_data = f.read()
        st.download_button("📥 Download execution_summary.txt", txt_data, file_name="execution_summary.txt", mime="text/plain")
