# HR Email Automation

A Python automation system for sending personalized job application emails via Gmail. The system manages contact loading, email template selection, resume attachment, campaign progress tracking, and per-run logging through a modular, single-entry-point architecture.

---

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Architecture](#architecture)
- [Module Reference](#module-reference)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Resume Setup](#resume-setup)
- [Contact Dataset](#contact-dataset)
- [Usage](#usage)
- [Email Templates](#email-templates)
- [Logging](#logging)
- [Excluded Files](#excluded-files)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

The system reads recruiter contacts from an Excel workbook, selects a randomized email template (subject, body, and matching resume attachment), sends the email via Gmail SMTP with rate limiting and random inter-send delays, and writes the result to a CSV log. Contacts that have already been sent an email are skipped on subsequent runs.

Key characteristics:

- Single entry point: `run.py`
- Template, subject, body, and resume are index-synchronized — selecting template N resolves subject N, body N, and `RESUME_MAP[N]` in unison
- Daily send limit enforced via `DAILY_EMAIL_LIMIT`
- Random inter-send delay between `MIN_DELAY_SECONDS` and `MAX_DELAY_SECONDS`
- Campaign state tracked in-memory against the email log; no database required

---

## Repository Structure

```
HR-email-Automation/
├── assets/
│   └── signature.png           # Email signature image
├── data/
│   └── sample_hr_contacts.xlsx   # Sample HR contact dataset
├── resume/                     # Resume PDF files (excluded from version control)
├── templates/
│   ├── email_template.html     # Primary HTML email template
│   ├── email_template.txt      # Plain-text fallback template
│   └── followup_template.html  # Follow-up email template
├── .gitignore
├── README.md
├── campaign_tracker.py         # Tracks sent/failed/remaining contacts
├── clean_contacts.py           # Contact cleaning utility
├── config.py                   # Central configuration module
├── contact_loader.py           # Loads contacts from Excel
├── email_builder.py            # Builds personalized email content
├── excel_manager.py            # Excel read/write operations
├── gmail_service.py            # Gmail SMTP service
├── gmail_test.py               # Gmail connectivity test
├── logger.py                   # CSV email log writer
├── requirements.txt            # Python dependencies
├── run.py                      # Entry point
├── send_emails.py              # Campaign orchestration
└── utils.py                    # Utility functions (delay, helpers)
```

The following directories and files are generated at runtime and are excluded from version control:

- `output/` — cleaned contact exports (`cleaned_hr_contacts.xlsx`)
- `logs/` — per-run CSV logs (`email_log.csv`)
- `resume/` — resume PDF files
- `.env` — environment credentials

---

## Architecture

```
run.py
  └── EmailCampaign (send_emails.py)
        ├── ContactLoader       (contact_loader.py)   → reads data/sample_hr_contacts.xlsx
        ├── CampaignTracker     (campaign_tracker.py)  → checks sent/failed state
        ├── EmailBuilder        (email_builder.py)     → selects template ID; builds subject + body
        ├── GmailService        (gmail_service.py)     → SMTP send with attachment
        ├── EmailLogger         (logger.py)            → writes logs/email_log.csv
        └── config.py           → RESUME_MAP[template_id] resolves the resume path
```

Template synchronization: `EmailBuilder.build_email()` returns `(template_id, subject, body)`. The same `template_id` is used to look up `RESUME_MAP[template_id]` in `send_emails.py`, keeping subject, body, and resume attachment in sync.

---

## Module Reference

| Module | Responsibility |
|---|---|
| `config.py` | Loads `.env`, defines all directory paths, file paths, SMTP settings, `RESUME_MAP`, campaign constants, and applicant metadata |
| `run.py` | Entry point; instantiates `EmailCampaign` and calls `campaign.run()` |
| `send_emails.py` | Orchestrates the full campaign loop: load contacts, skip sent, build email, send, log, delay |
| `contact_loader.py` | Reads `data/samplet_hr_contacts.xlsx` and returns a list of contact dictionaries |
| `clean_contacts.py` | Contact cleaning utility |
| `email_builder.py` | Selects a random template ID (1–10); constructs the personalized subject and HTML body |
| `gmail_service.py` | Opens an SMTP connection to Gmail and sends multipart emails with PDF attachments |
| `gmail_test.py` | Standalone connectivity test for Gmail credentials |
| `campaign_tracker.py` | Reads `logs/email_log.csv` to build the set of already-sent addresses; reports campaign status |
| `excel_manager.py` | Handles Excel file operations via `openpyxl` |
| `logger.py` | Appends success and failure records to `logs/email_log.csv` |
| `utils.py` | Provides `get_random_delay()` and other shared helpers |

---

## Prerequisites

- Python 3.9 or later
- A Gmail account with an App Password enabled (standard Gmail passwords are not accepted)
- App Passwords require 2-Step Verification to be active on the Google account

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/VishwasGurao/HR-email-Automation.git
cd HR-email-Automation
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Create the environment file**

```bash
cp .env.example .env   # if an example file is provided, otherwise create manually
```

`.env` contents:

```
EMAIL=your_gmail_address@gmail.com
APP_PASSWORD=your_gmail_app_password
```

To generate a Gmail App Password: Google Account → Security → 2-Step Verification → App Passwords.

**5. Verify the configuration**

```bash
python config.py
```

This prints all resolved paths and validates that `EMAIL` and `APP_PASSWORD` are present.

**6. Test Gmail connectivity**

```bash
python gmail_test.py
```

---

## Configuration

All configuration is centralized in `config.py`. The table below documents every variable.

### Directories

| Variable | Default Path | Description |
|---|---|---|
| `PROJECT_ROOT` | Repository root | Resolved from `__file__` |
| `DATA_DIR` | `<root>/data` | Source contact workbooks |
| `OUTPUT_DIR` | `<root>/output` | Cleaned contact exports (generated at runtime) |
| `RESUME_DIR` | `<root>/resume` | Resume PDF files (excluded from version control) |
| `TEMPLATE_DIR` | `<root>/templates` | HTML and plain-text email templates |
| `LOG_DIR` | `<root>/logs` | CSV email logs (generated at runtime) |
| `ASSETS_DIR` | `<root>/assets` | Static assets (signature image) |

### Files

| Variable | Path | Description |
|---|---|---|
| `HR_CONTACTS_FILE` | `data/samplet_hr_contacts.xlsx` | Source contact dataset |
| `CLEAN_CONTACTS_FILE` | `output/cleaned_hr_contacts.xlsx` | Output of the cleaning step |
| `EMAIL_TEMPLATE_FILE` | `templates/email_template.html` | Primary HTML template |
| `EMAIL_PLAIN_TEXT_FILE` | `templates/email_template.txt` | Plain-text fallback |
| `FOLLOWUP_TEMPLATE_FILE` | `templates/followup_template.html` | Follow-up template |
| `EMAIL_LOG_FILE` | `logs/email_log.csv` | Campaign log |
| `SIGNATURE_FILE` | `assets/signature.png` | Signature image |

### SMTP

| Variable | Value | Description |
|---|---|---|
| `SMTP_SERVER` | `smtp.gmail.com` | Gmail SMTP host |
| `SMTP_PORT` | `587` | TLS port |
| `EMAIL_ADDRESS` | From `.env` | Sender address |
| `APP_PASSWORD` | From `.env` | Gmail App Password |

### Campaign

| Variable | Default | Description |
|---|---|---|
| `DAILY_EMAIL_LIMIT` | `50` | Maximum emails per run |
| `MIN_DELAY_SECONDS` | `30` | Minimum inter-send delay |
| `MAX_DELAY_SECONDS` | `45` | Maximum inter-send delay |
| `DATE_FORMAT` | `%d-%m-%Y %H:%M:%S` | Timestamp format used in logs |

### Status Values

| Variable | Value |
|---|---|
| `STATUS_PENDING` | `"Pending"` |
| `STATUS_SENT` | `"Sent"` |
| `STATUS_FAILED` | `"Failed"` |
| `FOLLOWUP_DEFAULT` | `"No"` |

### Applicant Metadata

| Variable | Description |
|---|---|
| `FULL_NAME` | Applicant full name |
| `DEFAULT_JOB_TITLE` | Default role title used in email content |
| `MOBILE_NUMBER` | Contact number included in emails |
| `PORTFOLIO_URL` | Portfolio URL included in emails |
| `LINKEDIN_URL` | LinkedIn URL included in emails |

---

## Resume Setup

Resume PDF files are intentionally excluded from version control for privacy reasons. The `resume/` directory and all `.pdf` files are listed in `.gitignore`.

To use the system:

1. Create the `resume/` directory in the project root if it does not exist.
2. Place your resume PDF files inside `resume/`.
3. Update `RESUME_MAP` in `config.py` to match your filenames.

`RESUME_MAP` currently defines 10 entries (indices 1–10), each mapping a template ID to a resume path:

```python
RESUME_MAP: dict[int, Path] = {
    1: RESUME_DIR / "Your_Name_Role_A_Resume.pdf",
    2: RESUME_DIR / "Your_Name_Role_B_Resume.pdf",
    # ... continue for all template IDs in use
}
```

Every key in `RESUME_MAP` must correspond to a valid template ID that `EmailBuilder` can select. If a file is missing at send time, the campaign will log a failure for that contact and continue.

---

## Contact Dataset

The repository includes `data/samplet_hr_contacts.xlsx` as a sample dataset for development and testing purposes. This file contains synthetic or anonymized contact records and is not the original production contact workbook.

The workbook is expected to contain at minimum the following columns, which `ContactLoader` reads:

- `full_name` — recruiter or contact name
- `email` — recipient email address
- `company` — company name
- `role` — target role or department

To use your own contact data, replace `data/samplet_hr_contacts.xlsx` with a workbook that matches this schema, or update `HR_CONTACTS_FILE` in `config.py` to point to a different file.

---

## Usage

**Run the campaign**

```bash
python run.py
```

The entry point instantiates `EmailCampaign` and calls `campaign.run()`. On startup, the campaign prints a status report showing total contacts, already sent, failed, and remaining. It then processes each pending contact in order, printing per-email progress and a summary on completion.

To cancel a run in progress, press `Ctrl+C`. The campaign handles `KeyboardInterrupt` gracefully; contacts sent before cancellation are logged and will be skipped on the next run.

**Run the contact cleaning utility**

```bash
python clean_contacts.py
```

Output is written to `output/cleaned_hr_contacts.xlsx`.

**Verify Gmail connectivity**

```bash
python gmail_test.py
```

**Inspect configuration**

```bash
python config.py
```

---

## Email Templates

Ten template variants are defined. `EmailBuilder.build_email()` selects one at random per contact. The template ID returned by `build_email()` is used in `send_emails.py` to look up both the email subject and the resume attachment from `RESUME_MAP`, ensuring all three components are consistently synchronized.

HTML templates reside in `templates/`. A plain-text fallback (`email_template.txt`) is also available for clients that do not render HTML. A follow-up template (`followup_template.html`) is present for future use.

---

## Logging

Every send attempt is recorded in `logs/email_log.csv`. The log directory is created at runtime if it does not exist. The log is not reset between runs; `CampaignTracker` reads it at startup to determine which email addresses have already been contacted.

Log columns include recruiter name, email address, company, role, send status (`Sent` / `Failed`), error message (on failure), and timestamp.

---

## Excluded Files

The following are excluded from version control via `.gitignore` and must be created locally:

| Path | Reason |
|---|---|
| `.env` | Contains credentials |
| `resume/` | Resume PDFs excluded for privacy |
| `output/` | Generated at runtime |
| `logs/` | Generated at runtime |
| `.venv/`, `venv/` | Virtual environment |
| `__pycache__/` | Python bytecode |
| `token.json`, `credentials.json`, `client_secret*.json` | OAuth tokens and secrets |

---

## Roadmap

The following improvements are under consideration:

- Scheduled execution via cron or a task scheduler to enforce daily send limits automatically
- Configurable template weights to control selection frequency per resume variant
- Duplicate detection based on company domain in addition to email address
- CSV export of per-campaign summary statistics

---

## License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.
