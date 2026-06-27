# HR Email Automation

A Python automation system for sending personalized job application emails to HR recruiter contacts via Gmail SMTP. The system reads contact data from an Excel workbook, generates role-targeted email content from a pool of ten template variants, attaches the corresponding resume PDF, delivers each message over a TLS-secured SMTP connection, and records every outcome to an append-only CSV audit log. Campaign state is derived from the log at startup, enabling campaigns to be stopped and resumed without data loss or duplicate sends.

---
# Business Benefits

This project was designed to streamline large-scale job application campaigns by reducing manual effort, improving communication consistency, preventing duplicate outreach, and maintaining a complete audit trail of email delivery. The automation focuses on reliability, maintainability, and operational efficiency while preserving personalized communication with recruiters.

| Benefit              | Description                             |
| -------------------- | --------------------------------------- |
| Time Saving          | Eliminates repetitive manual emailing   |
| Consistency          | Standardized professional communication |
| Resume Accuracy      | Prevents incorrect resume attachments   |
| Campaign Tracking    | Persistent progress across sessions     |
| Duplicate Prevention | Avoids repeated outreach                |
| Auditability         | Complete delivery history               |
| Configurability      | Easy customization through config.py    |


## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Objectives](#2-objectives)
3. [Key Features](#3-key-features)
4. [System Architecture](#4-system-architecture)
5. [Execution Workflow](#5-execution-workflow)
6. [Repository Structure](#6-repository-structure)
7. [Technology Stack](#7-technology-stack)
8. [Requirements](#8-requirements)
9. [Installation](#9-installation)
10. [Gmail Configuration](#10-gmail-configuration)
11. [Configuration Reference](#11-configuration-reference)
12. [Resume Setup](#12-resume-setup)
13. [Contact Dataset](#13-contact-dataset)
14. [Email Templates and Personalization](#14-email-templates-and-personalization)
15. [Module Reference](#15-module-reference)
16. [Logging System](#16-logging-system)
17. [Campaign Tracking](#17-campaign-tracking)
18. [Error Handling](#18-error-handling)
19. [Spam Prevention](#19-spam-prevention)
20. [Customization](#20-customization)
21. [Usage](#21-usage)
22. [Expected Output](#22-expected-output)
23. [Troubleshooting](#23-troubleshooting)
24. [Roadmap](#24-roadmap)
25. [Contributing](#25-contributing)
26. [License](#26-license)
27. [Author](#27-author)

---

## 1. Problem Statement

Conducting a job search at scale requires sending a high volume of application emails to HR contacts across many organizations. Managing this manually introduces several operational problems:

- Sending duplicate emails to the same contact across separate work sessions.
- Attaching the wrong resume variant for the role being targeted.
- Losing visibility into which contacts have been reached and which remain pending.
- Sending emails in rapid succession, which increases the probability of spam classification.
- Maintaining no durable record of delivery outcomes for audit or retry purposes.

This system addresses each of these problems through persistent log-based tracking, deterministic index-synchronized resume mapping, append-only CSV logging, and configurable random inter-send delays.

---

## 2. Objectives

- Load and validate recruiter contact records from a structured Excel workbook.
- Prevent duplicate sends across independent campaign sessions using a log-derived in-memory set.
- Select from ten distinct email template variants per send to diversify message content.
- Keep the email subject, body, and attached resume PDF synchronized through a shared integer index.
- Deliver messages via Gmail SMTP over a TLS-secured connection authenticated with an App Password.
- Append one audit record per send attempt to a persistent CSV log, regardless of success or failure.
- Report pre-campaign and post-campaign statistics from the tracker on every run.
- Allow campaigns to be interrupted and resumed without data loss.

---

## 3. Key Features

| Feature | Description |
|---|---|
| Ten-variant template engine | Each send selects one of ten subject/body combinations via `random.randint(1, 10)`. Each variant targets a different analytics role angle. |
| Index-synchronized resume mapping | The integer that selects the template also resolves the resume PDF via `RESUME_MAP`, making it impossible for subject, body, and attachment to mismatch. |
| Persistent duplicate prevention | `CampaignTracker` reads the CSV log at startup and builds an in-memory set of previously sent addresses, skipping them in subsequent runs. |
| Resumable campaigns | Interrupting and restarting the process skips all already-sent contacts and resumes from the first unsent address. |
| Append-only audit log | `EmailLogger` writes one row per attempt with timestamp, recruiter name, email, company, role, status, and error detail. Existing rows are never modified. |
| Contact validation and deduplication | Email addresses are validated against a regex pattern at load time. Contacts with missing names, invalid addresses, or duplicate emails within the session are excluded silently. |
| Gmail SMTP over TLS | Connects to `smtp.gmail.com:587`, upgrades via `STARTTLS`, and authenticates with an App Password. The SMTP connection is held open for the duration of the campaign via a context manager. |
| Configurable rate limiting | Random inter-send delay and a daily volume limit constant are both configurable in `config.py`. |
| Self-testing modules | Every module includes an `if __name__ == "__main__":` block for isolated testing and diagnostics. |
| Centralized configuration | All paths, SMTP settings, campaign constants, status strings, and applicant metadata are defined in a single `config.py` module. |

---

## 4. System Architecture

The system uses a layered architecture with a single entry point, a campaign orchestration layer, a set of single-responsibility service modules, a central configuration module, and a shared utility module.

```
+----------------------------------------------------------+
|                    Entry Point                           |
|                    run.py                                |
|                    EmailCampaign.run()                   |
+------------------------+---------------------------------+
                         |
        +----------------+----------------+
        |                |                |
+-------+-------+ +------+------+ +-------+-------+
| ContactLoader | | CampaignTra | | EmailBuilder  |
|               | | cker        | |               |
| Reads Excel   | | Reads CSV   | | Selects       |
| Validates     | | log         | | template_id   |
| Deduplicates  | | Builds sent | | Returns       |
| Returns       | | set         | | (id, subj,    |
| list[dict]    | | Reports     | |  body)        |
|               | | progress    | |               |
+-------+-------+ +------+------+ +-------+-------+
        |                                 |
        |         +---------------+       |
        |         |   config.py   |       |
        |         |               |       |
        |         | RESUME_MAP    +<------+
        |         | Paths         |
        |         | SMTP settings |
        |         | Constants     |
        |         +---------------+
        |
+-------+--------------------------------------------------+
|                    GmailService                          |
|                    gmail_service.py                      |
|                                                          |
|  connect()    — EHLO, STARTTLS, login                   |
|  send_email() — builds EmailMessage, attaches PDF        |
|  disconnect() — SMTP.quit()                              |
|  Context manager (__enter__ / __exit__)                  |
+---------------------------+------------------------------+
                            |
+---------------------------+------------------------------+
|                    EmailLogger                           |
|                    logger.py                             |
|                                                          |
|  Creates logs/email_log.csv if absent                    |
|  Appends one row per success or failure event            |
+---------------------------+------------------------------+
                            |
+---------------------------+------------------------------+
|                    utils.py                              |
|                                                          |
|  is_valid_email()    clean_text()                        |
|  get_random_delay()  file_exists()                       |
|  get_current_timestamp()                                 |
+----------------------------------------------------------+
```

### Architectural Decisions

**Single configuration module.** All constants, file paths, SMTP settings, and status strings are defined in `config.py` and imported by every other module. This eliminates magic strings and ensures that changes to paths or constants require edits in only one location.

**Context manager for SMTP.** `GmailService` implements `__enter__` and `__exit__`, so the SMTP connection is opened once at the start of the campaign loop and reliably closed on exit regardless of whether an exception occurs. This avoids per-email authentication overhead.

**Index-synchronized triple.** `EmailBuilder.build_email()` returns `(template_id, subject, body)`. The caller uses `template_id` to look up `RESUME_MAP[template_id]` without a second selection call. Subject, body, and attachment are always drawn from the same variant.

**Append-only log as campaign state.** The CSV log is the authoritative source of campaign state. `CampaignTracker` derives its `sent_emails` set entirely from this log, meaning the system remains correct even if the Excel contact workbook is modified between runs.

**Failure isolation per contact.** A send failure on one contact does not terminate the campaign. The exception is caught, logged, printed, and execution continues with the next contact after the configured delay.

---

## 5. Execution Workflow

```
START
  |
  v
Load contacts from Excel (ContactLoader)
  |
  v
Read CSV log and rebuild sent-email set (CampaignTracker)
  |
  v
Print campaign analysis: total / sent / failed / remaining
  |
  v
Open SMTP connection (GmailService.__enter__)
  |
  v
+----------------------------------------------------+
| For each contact in contact list:                  |
|                                                    |
|   Normalize email to lowercase                     |
|       |                                            |
|       v                                            |
|   Is email in sent_emails set?                     |
|       |               |                            |
|      YES              NO                           |
|       |               |                            |
|   Skip            EmailBuilder.build_email()       |
|                   Returns (template_id,            |
|                             subject, body)         |
|                       |                            |
|                       v                            |
|                   Resolve resume path:             |
|                   RESUME_MAP[template_id]          |
|                       |                            |
|                       v                            |
|                   GmailService.send_email()        |
|                       |                            |
|               +-------+-------+                   |
|            SUCCESS           FAILURE               |
|               |                  |                 |
|       log_success()       log_failure()            |
|       Add to sent_emails  (error recorded)         |
|               |                  |                 |
|               +--------+---------+                 |
|                        |                           |
|                   Random delay                     |
|                   (MIN to MAX seconds)             |
+----------------------------------------------------+
  |
  v
Close SMTP connection (GmailService.__exit__)
  |
  v
Print campaign summary
  |
  v
END
```

---

## 6. Repository Structure

```
HR-email-Automation/
├── assets/
│   └── signature.png               # Email signature image (path defined in config.py)
├── data/
│   └── test_hr_contacts.xlsx       # Sample contact dataset (see Section 13)
├── resume/                         # Resume PDF files — excluded from version control
├── templates/
│   ├── email_template.html         # HTML reference template
│   ├── email_template.txt          # Plain-text reference template
│   └── followup_template.html      # Follow-up reference template
├── .gitignore
├── README.md
├── campaign_tracker.py             # Log-based campaign state and progress reporting
├── clean_contacts.py               # Contact cleaning utility (currently empty)
├── config.py                       # Central configuration module
├── contact_loader.py               # Excel contact loading, validation, deduplication
├── email_builder.py                # Template selection and email personalization
├── excel_manager.py                # Excel read/clean/write operations
├── gmail_service.py                # Gmail SMTP connection and message delivery
├── gmail_test.py                   # Standalone SMTP connectivity test
├── logger.py                       # Append-only CSV event logger
├── requirements.txt                # Pinned Python dependencies
├── run.py                          # Primary entry point
├── send_emails.py                  # Campaign orchestrator (EmailCampaign class)
└── utils.py                        # Shared utility functions
```

The following paths are generated at runtime and are excluded from version control:

| Path | Generated by | Reason excluded |
|---|---|---|
| `logs/email_log.csv` | `EmailLogger` | Runtime output |
| `output/cleaned_hr_contacts.xlsx` | `ExcelManager` | Runtime output |
| `resume/` | User-provided | Privacy |
| `.env` | User-created | Contains credentials |

---

## 7. Technology Stack

| Component | Technology | Version | Notes |
|---|---|---|---|
| Runtime | Python | 3.10+ | `from __future__ import annotations` used throughout |
| Email transport | `smtplib` | stdlib | SMTP connection and message delivery |
| TLS negotiation | `ssl` | stdlib | `ssl.create_default_context()` for STARTTLS |
| Message construction | `email.message.EmailMessage` | stdlib | MIME message building and attachment handling |
| Excel read/write | pandas | 3.0.3 | DataFrame-based contact parsing |
| Excel file engine | openpyxl | 3.1.5 | Engine for `pd.read_excel` and `to_excel` |
| Environment variables | python-dotenv | 1.2.2 | Loads `.env` at startup |
| File paths | `pathlib.Path` | stdlib | Cross-platform path construction |
| Randomization | `random` | stdlib | Template selection and inter-send delay |
| Audit logging | `csv` | stdlib | Append-only row writing |
| Input validation | `re` | stdlib | Email format verification |
| Numeric support | numpy | 2.5.0 | Transitive dependency of pandas |
| Date parsing | python-dateutil | 2.9.0.post0 | Transitive dependency of pandas |
| Timezone data | tzdata | 2026.2 | Runtime timezone database |

---

## 8. Requirements

| Requirement | Specification |
|---|---|
| Python version | 3.10 or higher |
| Operating system | Windows, macOS, or Linux |
| Network access | Outbound TCP to `smtp.gmail.com:587` |
| Gmail account | Google account with 2-Step Verification enabled |
| Gmail App Password | 16-character App Password for SMTP authentication |

---

## 9. Installation

**Step 1: Clone the repository**

```bash
git clone https://github.com/VishwasGurao/HR-email-Automation.git
cd HR-email-Automation
```

**Step 2: Verify Python version**

```bash
python --version
# Required: 3.10 or higher
```

**Step 3: Create and activate a virtual environment**

```bash
# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**Step 4: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 5: Create the environment file**

Create `.env` in the project root:

```text
EMAIL=your_gmail_address@gmail.com
APP_PASSWORD=xxxx xxxx xxxx xxxx
```

See [Section 10](#10-gmail-configuration) for instructions on generating an App Password.

**Step 6: Place resume files**

Create the `resume/` directory and copy your PDF files into it. Filenames must match the values defined in `RESUME_MAP` inside `config.py`. See [Section 12](#12-resume-setup).

**Step 7: Verify the contact workbook**

Ensure `data/sample_hr_contacts.xlsx` contains the required columns. See [Section 13](#13-contact-dataset).

**Step 8: Verify configuration**

```bash
python config.py
```

This prints all resolved paths, the resume map, and the result of environment validation.

**Step 9: Test SMTP connectivity**

```bash
python gmail_test.py
```

Opens and immediately closes an SMTP connection without sending any email.

**Step 10: Run the campaign**

```bash
python run.py
```

---

## 10. Gmail Configuration

This system authenticates using a Gmail **App Password**, not the account's primary password. App Passwords require 2-Step Verification to be active on the account.

### Enabling 2-Step Verification

1. Navigate to [myaccount.google.com](https://myaccount.google.com).
2. Select **Security** from the left panel.
3. Under **How you sign in to Google**, select **2-Step Verification** and follow the setup prompts.

### Generating an App Password

1. Navigate to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
2. Under **App name**, enter a descriptive label such as `HR Email Bot`.
3. Click **Create**.
4. Copy the 16-character password (format: `xxxx xxxx xxxx xxxx`).
5. Add this value to `.env` as `APP_PASSWORD`.

### SMTP Connection Parameters

| Parameter | Value |
|---|---|
| Server | `smtp.gmail.com` |
| Port | `587` |
| Security | STARTTLS |
| Authentication | App Password |

### Common Authentication Errors

| Error | Cause | Resolution |
|---|---|---|
| `SMTPAuthenticationError` | Incorrect App Password or 2-Step Verification not active | Regenerate the App Password after confirming 2-Step Verification is enabled |
| `534 5.7.9` | App Passwords not available | Enable 2-Step Verification first |
| `Connection refused` | Port 587 blocked by firewall | Test on a different network; check firewall rules |
| `Network error: timed out` | No route to `smtp.gmail.com:587` | Verify internet connectivity and DNS resolution |

---

## 11. Configuration Reference

All configuration is centralized in `config.py`. No other module defines constants independently.

### Directory Constants

| Constant | Resolved Path | Purpose |
|---|---|---|
| `PROJECT_ROOT` | Parent directory of `config.py` | Absolute root for all relative paths |
| `DATA_DIR` | `PROJECT_ROOT/data` | Source contact workbooks |
| `OUTPUT_DIR` | `PROJECT_ROOT/output` | Cleaned contact exports (runtime-generated) |
| `RESUME_DIR` | `PROJECT_ROOT/resume` | Resume PDF files |
| `TEMPLATE_DIR` | `PROJECT_ROOT/templates` | Email template files |
| `LOG_DIR` | `PROJECT_ROOT/logs` | Campaign audit logs (runtime-generated) |
| `ASSETS_DIR` | `PROJECT_ROOT/assets` | Static assets (signature image) |

### File Constants

| Constant | Path | Purpose |
|---|---|---|
| `HR_CONTACTS_FILE` | `data/sample_hr_contacts.xlsx` | Primary input contact workbook |
| `CLEAN_CONTACTS_FILE` | `output/cleaned_hr_contacts.xlsx` | Output of `ExcelManager.save_cleaned_contacts()` |
| `EMAIL_TEMPLATE_FILE` | `templates/email_template.html` | HTML reference template |
| `EMAIL_PLAIN_TEXT_FILE` | `templates/email_template.txt` | Plain-text reference template |
| `FOLLOWUP_TEMPLATE_FILE` | `templates/followup_template.html` | Follow-up reference template |
| `EMAIL_LOG_FILE` | `logs/email_log.csv` | Append-only campaign audit log |
| `SIGNATURE_FILE` | `assets/signature.png` | Signature image path |

### Campaign Constants

| Constant | Default | Purpose |
|---|---|---|
| `DAILY_EMAIL_LIMIT` | `50` | Maximum emails per run (not programmatically enforced in the loop; see Roadmap) |
| `MIN_DELAY_SECONDS` | `30` | Lower bound of the inter-send delay range |
| `MAX_DELAY_SECONDS` | `45` | Upper bound of the inter-send delay range |
| `DATE_FORMAT` | `%d-%m-%Y %H:%M:%S` | Timestamp format used in the audit log |

### Status Constants

| Constant | Value | Usage |
|---|---|---|
| `STATUS_PENDING` | `"Pending"` | Initial status in the cleaned workbook |
| `STATUS_SENT` | `"Sent"` | Written to log on successful delivery |
| `STATUS_FAILED` | `"Failed"` | Written to log when an exception occurs |
| `FOLLOWUP_DEFAULT` | `"No"` | Default follow-up value in the cleaned workbook |

### SMTP Constants

| Constant | Value |
|---|---|
| `SMTP_SERVER` | `"smtp.gmail.com"` |
| `SMTP_PORT` | `587` |
| `EMAIL_ADDRESS` | Loaded from `EMAIL` in `.env` |
| `APP_PASSWORD` | Loaded from `APP_PASSWORD` in `.env` |

### Applicant Constants

| Constant | Description |
|---|---|
| `FULL_NAME` | Applicant full name used in email content |
| `DEFAULT_JOB_TITLE` | Default role title |
| `MOBILE_NUMBER` | Contact number referenced in templates |
| `PORTFOLIO_URL` | Portfolio URL referenced in templates |
| `LINKEDIN_URL` | LinkedIn URL referenced in templates |

### Environment Variables

The `.env` file must be placed in the project root. Both variables are required; `config.validate_environment()` raises `ValueError` if either is absent or empty.

| Variable | Description | Example |
|---|---|---|
| `EMAIL` | Gmail address used as the SMTP sender | `yourname@gmail.com` |
| `APP_PASSWORD` | 16-character Gmail App Password | `abcd efgh ijkl mnop` |

The `.env` file is listed in `.gitignore` and must never be committed to version control. Credentials must not be hardcoded in source files.

---

## 12. Resume Setup

Resume PDF files are intentionally excluded from version control. The `resume/` directory and all `.pdf` files are listed in `.gitignore`.

**Why resume mapping matters.** Each of the ten email template variants is designed for a different analytics role angle. Sending an email about Business Intelligence while attaching a Data Analyst resume creates an inconsistency that reduces credibility. The index-synchronized design in `RESUME_MAP` prevents this by tying the resume path to the same integer that selected the template.

### Setup Steps

1. Create the `resume/` directory in the project root if it does not exist.
2. Place your PDF files inside `resume/`.
3. Update `RESUME_MAP` in `config.py` to match your filenames:

```python
RESUME_MAP: dict[int, Path] = {
    1: RESUME_DIR / "Your_Name_Role_A_Resume.pdf",
    2: RESUME_DIR / "Your_Name_Role_B_Resume.pdf",
    # ... one entry per template ID
}
```

Every key in `RESUME_MAP` must correspond to a valid template ID (1 through 10 by default). If a PDF file is missing at send time, `GmailService._attach_file()` raises `FileNotFoundError`, which causes that contact's send to be logged as a failure; the campaign continues with the next contact.

---

## 13. Contact Dataset

The repository includes `data/sample_hr_contacts.xlsx` as a sample dataset for development and testing. This file contains synthetic or anonymized records and is not a production contact workbook.

### Required Column Schema

`ContactLoader` expects the following four column headers, case-sensitive:

| Workbook Column | Internal Field Key | Description |
|---|---|---|
| `Name` | `full_name` | Recruiter full name |
| `Email` | `email` | Recipient email address |
| `Title` | `role` | HR role or designation |
| `Company` | `company` | Company name |

If any column is absent, `ContactLoader._validate_columns()` raises `ValueError` listing the missing names.

### Normalization Applied at Load Time

- All text fields are passed through `clean_text()`, which strips leading/trailing whitespace and collapses internal whitespace sequences.
- The `email` field is lowercased.
- `first_name` is extracted from `full_name` by taking the first whitespace-delimited token. Defaults to `"Recruiter"` if the name is empty after cleaning.
- Contacts with an empty `full_name`, an empty or invalid `email`, or a duplicate `email` within the session are excluded silently.

### Using a Different Contact File

Update `HR_CONTACTS_FILE` in `config.py`:

```python
HR_CONTACTS_FILE = DATA_DIR / "my_contacts.xlsx"
```

The workbook columns must still be `Name`, `Email`, `Title`, and `Company`.

---

## 14. Email Templates and Personalization

### Template Selection

`EmailBuilder.build_email()` calls `random.randint(1, 10)` to select a `template_id` for each contact. The same integer is used to retrieve:

- The subject line from `templates/subjects.py`: `SUBJECTS[template_id]`
- The rendered body from `templates/bodies.py`: `render(template_id, first_name, company)`

The method returns `(template_id, subject, body)`. The `template_id` is returned explicitly so the orchestrator can resolve `RESUME_MAP[template_id]` without making a second independent selection.

### Personalization Parameters

| Parameter | Source | Usage |
|---|---|---|
| `first_name` | Extracted from `contact["full_name"]` by `ContactLoader` | Salutation line |
| `company` | From `contact["company"]` after `clean_text()` | Body copy |

If `company` is empty after cleaning, the `render()` function defaults to `"your organization"`.

### Template Structure

`templates/subjects.py` defines `SUBJECTS` as a `dict[int, str]`. `templates/bodies.py` defines a `render(template_id, first_name, company)` function. Each of the ten variants addresses a different role angle—Data Analyst, Business Analytics, MIS, Business Intelligence, Reporting, and others—so recipients at the same organization receive meaningfully distinct messages.

### Adding a New Template Variant

1. Add a new integer key to `SUBJECTS` in `templates/subjects.py`.
2. Add a corresponding branch in `render()` in `templates/bodies.py`.
3. Add a new entry to `RESUME_MAP` in `config.py`.
4. Place the corresponding PDF in the `resume/` directory.
5. Update the upper bound in `EmailBuilder.build_email()`: change `random.randint(1, 10)` to `random.randint(1, N)`.

---

## 15. Module Reference

### `config.py`

**Purpose:** Single source of truth for all configuration values.

**Responsibilities:** Calls `load_dotenv()`; derives all directory and file paths from `PROJECT_ROOT` using `pathlib.Path`; defines `RESUME_MAP`; exposes SMTP settings, campaign constants, status strings, date format, and applicant metadata; provides `validate_environment()` which raises `ValueError` if `EMAIL` or `APP_PASSWORD` are absent.

**Dependencies:** `os`, `pathlib`, `python-dotenv`

---

### `run.py`

**Purpose:** Primary entry point.

**Responsibilities:** Prints the campaign header; instantiates `EmailCampaign` and calls `run()`; handles `KeyboardInterrupt` with a graceful cancellation message; catches and prints any unhandled exception.

---

### `send_emails.py`

**Purpose:** Campaign orchestration.

**Responsibilities:** In `EmailCampaign.__init__()`, instantiates all service objects. In `EmailCampaign.run()`:

1. Calls `ContactLoader.load_contacts()` to retrieve `list[dict]`.
2. Calls `CampaignTracker.campaign_status()` and prints the pre-campaign analysis.
3. Opens the SMTP connection via `with self.gmail:`.
4. For each contact: normalizes the email, checks `CampaignTracker.is_already_sent()`, calls `EmailBuilder.build_email()`, resolves `RESUME_MAP[template_id]`, calls `GmailService.send_email()`, logs the result, updates `sent_emails`, and applies a random delay.
5. Prints the post-campaign summary.

---

### `contact_loader.py`

**Purpose:** Load, validate, normalize, and deduplicate recruiter contacts from the Excel workbook.

**Inputs:** `HR_CONTACTS_FILE` from `config.py`

**Outputs:** `list[dict]` with keys `full_name`, `email`, `role`, `company`, `first_name`

**Responsibilities:** Verifies the file exists; reads into a `pandas.DataFrame`; validates required columns; normalizes each row using `_normalize_row()`; filters invalid and duplicate contacts; returns the cleaned list.

**Dependencies:** `pandas`, `re`, `config`, `utils`

---

### `email_builder.py`

**Purpose:** Select a template variant and render a personalized subject and body.

**Inputs:** `first_name: str`, `company: str`

**Outputs:** `tuple[int, str, str]` — `(template_id, subject, body)`

**Responsibilities:** Calls `random.randint(1, 10)` for `template_id`; retrieves `SUBJECTS[template_id]`; calls `render(template_id, first_name, company)`; returns the triple.

**Design note:** Returning `template_id` explicitly keeps the subject, body, and resume lookup synchronized through a single shared integer.

**Dependencies:** `templates.subjects`, `templates.bodies`, `random`

---

### `gmail_service.py`

**Purpose:** Manage the SMTP connection lifecycle and deliver emails with attachments.

**Inputs:** `recipient: str`, `subject: str`, `body: str`, `attachments: list[Path] | None`

**Outputs:** `None` on success; raises `RuntimeError` wrapping the underlying exception on failure.

**Responsibilities:**
- `connect()`: Creates `smtplib.SMTP`, calls `ehlo()`, upgrades via `starttls()` with `ssl.create_default_context()`, calls `ehlo()` again, authenticates with `EMAIL_ADDRESS` and `APP_PASSWORD`.
- `disconnect()`: Calls `SMTP.quit()`, suppressing `SMTPServerDisconnected` if already closed.
- `_build_message()`: Constructs `EmailMessage` with headers and plain-text body via `set_content()`.
- `_attach_file()`: Resolves MIME type, reads file in binary mode, calls `add_attachment()`. Raises `FileNotFoundError` if the path does not exist.
- `send_email()`: Validates recipient, builds message, attaches files, calls `SMTP.send_message()`.
- Implements `__enter__` / `__exit__` for context manager use.

**Dependencies:** `smtplib`, `ssl`, `email.message`, `mimetypes`, `pathlib`, `config`, `utils`

---

### `campaign_tracker.py`

**Purpose:** Reconstruct campaign history from the audit log and provide duplicate detection and progress statistics.

**Inputs:** `log_file: Path` (defaults to `EMAIL_LOG_FILE`)

**Responsibilities:** On `__init__()`, calls `_load_logs()` which reads the CSV log row by row, populating `sent_emails: set[str]` for `Status == "Sent"` and `failed_emails: set[str]` for `Status == "Failed"`. Key methods:

| Method | Return Type | Description |
|---|---|---|
| `is_already_sent(email)` | `bool` | O(1) set lookup; returns `True` if address is in `sent_emails` |
| `campaign_status(total)` | `dict` | Returns `total`, `sent`, `failed`, `remaining`, `completion` |
| `get_summary()` | `dict` | Returns log-level counts |
| `find_duplicate_emails(contacts)` | `list` | Returns emails appearing more than once in the contact list |
| `estimate_remaining_time(total, avg_delay)` | `float` | Remaining contacts × average delay in seconds |
| `reset()` / `reload()` | `None` | Clear and optionally repopulate in-memory state |

**Dependencies:** `csv`, `pathlib`, `config`, `utils`

---

### `logger.py`

**Purpose:** Append one row to the CSV audit log per send attempt.

**Log column order:** `Timestamp`, `Recruiter`, `Email`, `Company`, `Role`, `Status`, `Message`

**Responsibilities:** Creates `LOG_DIR` and the log file (with header row) if absent; `log_success()` writes `Status=Sent`; `log_failure()` writes `Status=Failed` with the exception string. The file is always opened in append mode; existing rows are never modified.

**Dependencies:** `csv`, `datetime`, `pathlib`, `config`, `utils`

---

### `excel_manager.py`

**Purpose:** Standalone Excel preparation and status reporting utility. Not used in the campaign loop.

**Responsibilities:** `clean_contacts()` normalizes names and companies, lowercases and strips emails, removes invalid and duplicate rows, and constructs a cleaned DataFrame with the output schema: `HR Name`, `Email`, `Company`, `Designation`, `Status`, `Sent Date`, `Follow-up`, `Notes`. Additional methods handle saving, reloading, pending contact queries, per-row status updates, and aggregate counts.

**Note:** The campaign orchestrator uses `ContactLoader` for reading contacts and `EmailLogger` as the authoritative tracking mechanism. `ExcelManager` is used independently as a data preparation step.

**Dependencies:** `pandas`, `openpyxl`, `config`, `utils`

---

### `utils.py`

**Purpose:** Shared utility functions used by all modules.

| Function | Signature | Description |
|---|---|---|
| `is_valid_email` | `(email: str) -> bool` | Returns `True` if the input matches the email regex pattern |
| `get_current_timestamp` | `() -> str` | Returns `datetime.now()` formatted using `DATE_FORMAT` |
| `get_random_delay` | `() -> int` | Returns `random.randint(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)` |
| `file_exists` | `(file_path: Path) -> bool` | Returns `True` if the path exists and is a file |
| `clean_text` | `(text: str \| None) -> str` | Strips and collapses internal whitespace; returns `""` for `None` |

**Dependencies:** `random`, `re`, `datetime`, `pathlib`, `config`

---

### `clean_contacts.py`

**Status:** Present in the repository but currently empty. Contact cleaning is performed by `ExcelManager.clean_contacts()` and by the deduplication logic in `ContactLoader.load_contacts()`.

---

### `gmail_test.py`

**Purpose:** Standalone script that tests Gmail SMTP authentication without sending any email. Opens and immediately closes an SMTP connection using the configured credentials.

---

## 16. Logging System

### Log File Location

`logs/email_log.csv`. The `logs/` directory and the file are created automatically by `EmailLogger.__init__()` on the first run.

### Log Schema

| Column | Type | Description |
|---|---|---|
| `Timestamp` | string | Date and time formatted as `dd-mm-yyyy HH:MM:SS` |
| `Recruiter` | string | Full name from the contact record |
| `Email` | string | Recipient email address |
| `Company` | string | Company name from the contact record |
| `Role` | string | HR designation from the contact record |
| `Status` | string | `Sent` or `Failed` |
| `Message` | string | `"Email sent successfully."` on success, or the exception string on failure |

### Append-Only Guarantee

`EmailLogger` opens the log file with `mode="a"` on every write. Existing rows are never read or modified. The log is a complete, immutable record of every attempt across all campaign sessions.

### Sample Log Content

```csv
Timestamp,Recruiter,Email,Company,Role,Status,Message
26-06-2026 14:31:05,Rahul Sharma,rahul@example.com,Acme Technologies,HR Manager,Sent,Email sent successfully.
26-06-2026 14:31:13,Priya Desai,priya@example.com,Nexus Solutions,Talent Acquisition,Failed,SMTP Error: [Errno 111] Connection refused
```

---

## 17. Campaign Tracking

`CampaignTracker` derives its entire state from the CSV log. The two collections it maintains are:

- `sent_emails: set[str]` — addresses for all rows with `Status == "Sent"`.
- `failed_emails: set[str]` — addresses for all rows with `Status == "Failed"`.

Both are populated at instantiation. No state is written to the Excel workbook by the campaign orchestrator.

### Pre-Campaign Output

```text
============================================================
CAMPAIGN ANALYSIS
============================================================
Dataset Size    : 50
Already Sent    : 23
Failed Earlier  : 2
Remaining       : 27
============================================================
```

### Post-Campaign Output

```text
============================================================
CAMPAIGN SUMMARY
============================================================
Dataset Size    : 50
Already Sent    : 23
Sent Today      : 12
Failed Today    : 1
Remaining       : 14
============================================================
```

### Resumability

Because `CampaignTracker` rebuilds its state from the log at every startup, a campaign interrupted by a network failure, keyboard interrupt, or system restart can be resumed by running `python run.py` again. Every address in `sent_emails` is skipped, and the campaign continues from the first address not present in that set.

---

## 18. Error Handling

| Module | Strategy |
|---|---|
| `ContactLoader` | Raises `FileNotFoundError` if the workbook is absent; raises `ValueError` on missing columns; invalid and duplicate contacts are filtered silently at row level. |
| `GmailService` | Converts `SMTPAuthenticationError`, `SMTPRecipientsRefused`, `SMTPException`, and `OSError` into `RuntimeError` with descriptive messages. `_attach_file()` raises `FileNotFoundError` if a resume path does not resolve to an existing file. |
| `EmailCampaign` | Wraps each per-contact send in `try/except Exception`. A failure on one contact is logged and the loop continues with the next. `KeyboardInterrupt` is caught at the top level of `run.py`. |
| `CampaignTracker` | Returns silently if the log file does not exist; does not raise on a missing log. |
| `EmailLogger` | Creates parent directories before writing; does not raise if the log directory is absent. |
| `ExcelManager` | Raises `FileNotFoundError` on missing input; raises `ValueError` on missing columns. |

---

## 19. Spam Prevention

### Random Inter-Send Delay

Between each email, execution pauses for a random number of seconds in the range `[MIN_DELAY_SECONDS, MAX_DELAY_SECONDS]` (default: 3–10 seconds), implemented via `utils.get_random_delay()`. The delay is applied only when additional contacts remain in the current run.

### Daily Volume Limit

`DAILY_EMAIL_LIMIT` is set to `50` in `config.py`. This constant is documented as a recommended ceiling per run. Keeping daily send volume low reduces the probability of triggering Gmail's outbound spam filters. Programmatic enforcement in the campaign loop is planned for a future release (see Roadmap).

### Template Variation

Ten distinct subject/body combinations mean recipients at the same organization, or contacts reached across multiple days, receive visibly different messages. Sending identical subject lines to many addresses in rapid succession is a significant spam classification signal; varying content across sends mitigates this risk.

### TLS Encryption

All SMTP communication occurs over a TLS-upgraded connection via `STARTTLS`. Email content and credentials are not transmitted in plaintext.

### Email Address Validation

`utils.is_valid_email()` and `ContactLoader._is_valid_email()` reject malformed addresses before any send is attempted. Delivery attempts to invalid addresses generate bounce events that negatively affect sender reputation.

---

## 20. Customization

### Adjusting the Inter-Send Delay

```python
# config.py
MIN_DELAY_SECONDS = 30
MAX_DELAY_SECONDS = 45
```

### Changing the Contact File

```python
# config.py
HR_CONTACTS_FILE = DATA_DIR / "my_contacts.xlsx"
```

The workbook must still contain columns `Name`, `Email`, `Title`, and `Company`.

### Updating Applicant Information

```python
# config.py
FULL_NAME         = "Your Name"
DEFAULT_JOB_TITLE = "Your Target Role"
MOBILE_NUMBER     = "+91 XXXXXXXXXX"
PORTFOLIO_URL     = "https://yourportfolio.com"
LINKEDIN_URL      = "https://linkedin.com/in/your-profile"
```

### Updating Resume Files

```python
# config.py
RESUME_MAP: dict[int, Path] = {
    1: RESUME_DIR / "New_Resume_Variant_1.pdf",
    # ...
}
```

Place the PDF files in `resume/` with filenames that match exactly.

---

## 21. Usage

| Command | Description |
|---|---|
| `python run.py` | Run the email campaign |
| `python gmail_test.py` | Test SMTP authentication without sending any email |
| `python config.py` | Verify path resolution and environment variable validation |
| `python contact_loader.py` | Test contact loading and print the number of valid contacts |
| `python email_builder.py` | Preview a generated subject and body for a sample contact |
| `python campaign_tracker.py` | Print campaign statistics from the audit log |
| `python logger.py` | Write two test rows to the audit log |
| `python excel_manager.py` | Run the cleaning pipeline and write `output/cleaned_hr_contacts.xlsx` |

---

## 22. Expected Output

### Campaign start

```text
============================================================
HR EMAIL AUTOMATION
============================================================

============================================================
CAMPAIGN ANALYSIS
============================================================
Dataset Size    : 50
Already Sent    : 0
Failed Earlier  : 0
Remaining       : 50
============================================================
```

### Per-contact: success

```text
[1/50] Sending to rahul.sharma@example.com
✓ Email Sent [Template 3 | Your_Name_Data_Analyst_Resume.pdf]
Next email in 7 sec...
```

### Per-contact: failure

```text
[2/50] Sending to invalid@nodomain
✗ Failed : SMTP Error: [Errno 111] Connection refused
Next email in 4 sec...
```

### Post-campaign summary

```text
============================================================
CAMPAIGN SUMMARY
============================================================
Dataset Size    : 50
Already Sent    : 0
Sent Today      : 13
Failed Today    : 1
Remaining       : 36
============================================================

============================================================
CAMPAIGN COMPLETED SUCCESSFULLY
============================================================
Dataset Size    : 50
Already Sent    : 13
Failed Earlier  : 1
Remaining       : 36
Completion      : 26.0 %
============================================================
```

---

## 23. Troubleshooting

### SMTP authentication failure

**Symptom:** `RuntimeError: SMTP authentication failed.`

**Cause:** The App Password in `.env` is incorrect or has been revoked; or 2-Step Verification is not enabled.

**Resolution:** Revoke the existing App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords), generate a new one, and update `.env`. Confirm that 2-Step Verification is active.

---

### Missing environment variable

**Symptom:** `ValueError: EMAIL is missing in .env file.` or `ValueError: APP_PASSWORD is missing in .env file.`

**Cause:** The `.env` file does not exist or the variable name is misspelled.

**Resolution:** Verify that `.env` is in the project root (the same directory as `config.py`) and that both `EMAIL` and `APP_PASSWORD` are defined with the exact variable names shown.

---

### Missing contact workbook

**Symptom:** `FileNotFoundError: Contacts file not found: .../data/sample_hr_contacts.xlsx`

**Resolution:** Place the Excel file at `data/sample_hr_contacts.xlsx` relative to the project root.

---

### Missing required column

**Symptom:** `ValueError: Missing required columns: Title`

**Cause:** The workbook does not contain one or more of the required column headers.

**Resolution:** Verify that the workbook contains columns named exactly `Name`, `Email`, `Title`, and `Company`. Column names are case-sensitive.

---

### Missing resume file

**Symptom:** `FileNotFoundError: Attachment not found: .../resume/Your_Resume.pdf`

**Cause:** The PDF file is absent from `resume/`, or the filename in `RESUME_MAP` does not match the actual file.

**Resolution:** Place the PDF files in `resume/` with filenames that exactly match the values in `RESUME_MAP` in `config.py`.

---

### No contacts returned

**Symptom:** `No contacts found.` printed immediately after campaign start.

**Cause:** All rows in the workbook were excluded by `ContactLoader` due to missing names, missing or invalid emails, or all contacts already being present in `sent_emails`.

**Resolution:** Run `python contact_loader.py` to see how many contacts load successfully. Inspect the workbook for data quality issues.

---

### Port 587 blocked

**Symptom:** `RuntimeError: Network error: [Errno 111] Connection refused` or `timed out`

**Cause:** The network or firewall blocks outbound TCP on port 587.

**Resolution:** Test from a different network (such as a mobile hotspot). If operating behind a corporate firewall, request that port 587 to `smtp.gmail.com` be opened.

---

### All contacts skipped on resume

**Symptom:** The campaign runs but shows `Sent Today: 0` and completes immediately.

**Cause:** All addresses in the contact workbook are present in `sent_emails` from a prior run. This is the expected behavior of the duplicate-prevention mechanism.

**Resolution for testing only:** Rename or delete `logs/email_log.csv`. Do not do this in a production campaign, as it will cause duplicate sends to all previously contacted addresses.

---

## 24. Roadmap

The following improvements are under consideration. None exist in the current codebase.

- Implement `clean_contacts.py` as a command-line utility wrapping `ExcelManager.clean_contacts()` for a two-step workflow: prepare contacts, then run the campaign.
- Add programmatic enforcement of `DAILY_EMAIL_LIMIT` within `EmailCampaign.run()`.
- Add MIME multipart support to `GmailService` to send HTML bodies alongside a plain-text fallback, using the existing `email_template.html` and `email_template.txt`.
- Implement the follow-up email workflow using `followup_template.html`, triggered after a configurable number of days with no response.
- Add a `--dry-run` CLI flag that executes the full pipeline but calls a stub instead of `GmailService.send_email()`.
- Add a command-line interface using `argparse` to accept `--limit`, `--dry-run`, and `--contact-file` parameters.
- Add a `pytest` unit test suite covering `ContactLoader`, `EmailBuilder`, `CampaignTracker`, `EmailLogger`, and `utils`.
- Integrate with a scheduler (cron on Linux/macOS, Task Scheduler on Windows) for fully automated daily execution.
- Add support for rotating across multiple Gmail sender accounts to distribute send volume.

---

## 25. Contributing

Contributions are accepted via pull request.

### Development Setup

1. Fork the repository and clone the fork locally.
2. Create a feature branch from `master`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

### Code Style Requirements

- Use `from __future__ import annotations` in all modules.
- Apply full type annotations to all function signatures.
- Use `pathlib.Path` for all file system paths. Do not use `os.path`.
- Keep each module responsible for a single concern.
- Handle all exceptions explicitly. Do not use bare `except:` clauses.
- Add a docstring to every public class and public method.
- Add an `if __name__ == "__main__":` self-test block to any new module.

### Submitting Changes

1. Commit with a clear, concise message describing what changed and why.
2. Push the branch to your fork and open a pull request against the `master` branch.
3. Include in the pull request description: the change, its motivation, and any configuration or migration steps required.

### Reporting Issues

Open a GitHub Issue with the Python version, operating system, complete traceback, steps to reproduce, and the contents of `config.py` with credentials redacted.

---

## 26. License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.

---

## 27. Author

**Vishwash Gurav**  
Data Analyst | Python Developer

- GitHub: [github.com/VishwasGurao](https://github.com/VishwasGurao)
- LinkedIn: [linkedin.com/in/vishwas-gurav](https://linkedin.com/in/vishwas-gurav)
- Portfolio: [vishwasgurao.in](https://vishwasgurao.in)
