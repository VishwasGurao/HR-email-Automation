"""
config.py

Central configuration module for the HR Email Automation System.

Responsibilities:
- Load environment variables
- Define project directories
- Define file locations
- Store SMTP configuration
- Store application constants

Author: Vishwas Gurav
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

# ==========================================================
# Directories
# ==========================================================

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
RESUME_DIR = PROJECT_ROOT / "resume"
TEMPLATE_DIR = PROJECT_ROOT / "templates"
LOG_DIR = PROJECT_ROOT / "logs"

# ==========================================================
# Files
# ==========================================================

HR_CONTACTS_FILE = DATA_DIR / "sample_hr_contacts.xlsx"

CLEAN_CONTACTS_FILE = OUTPUT_DIR / "cleaned_hr_contacts.xlsx"

EMAIL_TEMPLATE_FILE = TEMPLATE_DIR / "email_template.html"

EMAIL_PLAIN_TEXT_FILE = TEMPLATE_DIR / "email_template.txt"

FOLLOWUP_TEMPLATE_FILE = TEMPLATE_DIR / "followup_template.html"

EMAIL_LOG_FILE = LOG_DIR / "email_log.csv"

# ==========================================================
# Resume Map
# Index-synchronized with subjects.py and bodies.py.
# Template N  →  Subject N  →  Body N  →  RESUME_MAP[N]
# ==========================================================

RESUME_MAP: dict[int, Path] = {
    1:  RESUME_DIR / "Vishwash_Gurav_Data_Analyst_Resume.pdf",
    2:  RESUME_DIR / "Vishwash_Gurav_Business_Analytics_Resume.pdf",
    3:  RESUME_DIR / "Vishwash_Gurav_Data_Business_Analyst_Resume.pdf",
    4:  RESUME_DIR / "Vishwash_Gurav_Business_Intelligence_Analyst_Resume.pdf",
    5:  RESUME_DIR / "Vishwash_Gurav_Data_Analytics_Reporting_Resume.pdf",
    6:  RESUME_DIR / "Vishwash_Gurav_Data_MIS_Analyst_Resume.pdf",
    7:  RESUME_DIR / "Vishwash_Gurav_Business_Intelligence_Resume.pdf",
    8:  RESUME_DIR / "Vishwash_Gurav_Data_Analytics_Resume.pdf",
    9:  RESUME_DIR / "Vishwash_Gurav_Analytics_Reporting_MIS_Resume.pdf",
    10: RESUME_DIR / "Vishwash_Gurav_Entry_Level_Analytics_Resume.pdf",
}

# ==========================================================
# Gmail Configuration
# ==========================================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_ADDRESS = os.getenv("EMAIL", "").strip()
APP_PASSWORD = os.getenv("APP_PASSWORD", "").strip()

# ==========================================================
# Email Campaign Configuration
# ==========================================================

EMAIL_SUBJECT = (
    "Data Analyst | Vishwas Gurav | "
    "SQL • Power BI • Python | Resume Attached"
)

DAILY_EMAIL_LIMIT = 50

MIN_DELAY_SECONDS = 30
MAX_DELAY_SECONDS = 45

# ==========================================================
# Status Values
# ==========================================================

STATUS_PENDING = "Pending"
STATUS_SENT = "Sent"
STATUS_FAILED = "Failed"

FOLLOWUP_DEFAULT = "No"

# ==========================================================
# Date Format
# ==========================================================

DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

# ==========================================================
# Validation
# ==========================================================


def validate_environment() -> None:
    """
    Validate required environment variables.
    """

    if not EMAIL_ADDRESS:
        raise ValueError(
            "EMAIL is missing in .env file."
        )

    if not APP_PASSWORD:
        raise ValueError(
            "APP_PASSWORD is missing in .env file."
        )


# ==========================================================
# Self Test
# ==========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("CONFIGURATION")
    print("=" * 50)

    print(f"Project Root      : {PROJECT_ROOT}")
    print(f"Data Folder       : {DATA_DIR}")
    print(f"Output Folder     : {OUTPUT_DIR}")
    print(f"Resume Folder     : {RESUME_DIR}")
    print(f"Template Folder   : {TEMPLATE_DIR}")
    print(f"Log Folder        : {LOG_DIR}")

    print()

    print(f"Contacts File     : {HR_CONTACTS_FILE}")
    print(f"Email Template    : {EMAIL_TEMPLATE_FILE}")
    print(f"Followup Template : {FOLLOWUP_TEMPLATE_FILE}")
    print(f"Log File          : {EMAIL_LOG_FILE}")

    print()

    print("Resume Map")
    print("-" * 50)
    for idx, path in RESUME_MAP.items():
        print(f"  Template {idx:>2}  :  {path.name}")

    print()

    print(f"SMTP Server       : {SMTP_SERVER}")
    print(f"SMTP Port         : {SMTP_PORT}")

    print()

    try:
        validate_environment()
        print("Environment Status : OK")
    except ValueError as error:
        print(f"Environment Status : {error}")

    print("=" * 50)

# ==========================================================
# Applicant Information
# ==========================================================

FULL_NAME = "Vishwash Gurav"

DEFAULT_JOB_TITLE = "Data Analyst"

MOBILE_NUMBER = "+91 7676733325"

PORTFOLIO_URL = "https://vishwasgurao.in"

LINKEDIN_URL = "https://linkedin.com/in/vishwas-gurav"

# ==========================================================
# Assets
# ==========================================================

ASSETS_DIR = PROJECT_ROOT / "assets"

SIGNATURE_FILE = ASSETS_DIR / "signature.png"

APP_NAME = "HR Email Automation"

VERSION = "1.0.0"

AUTHOR = "Vishwash Gurav"