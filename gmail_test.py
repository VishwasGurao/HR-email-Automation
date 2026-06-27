"""
gmail_test.py

Integration test for the HR Email Automation System.

Responsibilities
----------------
- Load first contact from cleaned Excel
- Build personalized plain-text email
- Attach the resume matched to the selected template
- Send one test email

Author: Vishwash Gurav
"""

from pathlib import Path

from config import (
    DEFAULT_JOB_TITLE,
    EMAIL_ADDRESS,
    EMAIL_SUBJECT,
    FULL_NAME,
    LINKEDIN_URL,
    MOBILE_NUMBER,
    PORTFOLIO_URL,
    RESUME_MAP,
)

from email_builder import EmailBuilder
from excel_manager import ExcelManager
from gmail_service import GmailService


def main() -> None:

    print("=" * 60)
    print("GMAIL TEST")
    print("=" * 60)

    manager = ExcelManager()

    manager.load_contacts()
    manager.clean_contacts()
    manager.save_cleaned_contacts()

    pending = manager.get_pending_contacts()

    if not pending:
        print("No pending contacts found.")
        return

    contact = pending[0]

    print()
    print("Recipient")
    print("-" * 60)
    print(f"Name    : {contact['HR Name']}")
    print(f"Email   : {contact['Email']}")
    print(f"Company : {contact['Company']}")

    builder = EmailBuilder()

    template_id, subject, body = builder.build_email(
        first_name=contact["HR Name"],
        company=contact["Company"],
    )

    resume = RESUME_MAP[template_id]

    print()
    print("Template Selected")
    print("-" * 60)
    print(f"Template ID : {template_id}")
    print(f"Subject     : {subject}")
    print(f"Resume      : {resume.name}")

    print()
    print("Sending Email...")
    print("-" * 60)

    with GmailService() as gmail:

        gmail.send_email(
        recipient=contact["Email"],
        subject=subject,
        body=body,
        attachments=[resume],
    )
        
    print()
    print("=" * 60)
    print("EMAIL SENT SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":

    try:
        main()

    except Exception as error:

        print()
        print("=" * 60)
        print("TEST FAILED")
        print("=" * 60)
        print(error)