"""
send_emails.py

Runs the complete HR Email Automation Campaign.

Responsibilities:
- Load recruiter contacts
- Generate personalized emails
- Attach the resume matched to the selected template
- Send emails
- Log results
- Apply random delay

Author: Vishwash Gurav
"""

from __future__ import annotations

from pathlib import Path
import time


from contact_loader import ContactLoader
from campaign_tracker import CampaignTracker
from email_builder import EmailBuilder
from gmail_service import GmailService
from logger import EmailLogger
from config import (
    EMAIL_ADDRESS,
    EMAIL_SUBJECT,
    FULL_NAME,
    LINKEDIN_URL,
    MOBILE_NUMBER,
    PORTFOLIO_URL,
    RESUME_MAP,
)

from utils import get_random_delay


class EmailCampaign:
    """
    Runs the HR email campaign.
    """

    def __init__(self) -> None:

        self.contacts = ContactLoader()

        self.builder = EmailBuilder()

        self.gmail = GmailService()

        self.logger = EmailLogger()

        self.tracker = CampaignTracker()

        self.subject = EMAIL_SUBJECT

    # ---------------------------------------------------------
    # RUN CAMPAIGN 
    # ---------------------------------------------------------

    def run(self) -> None:
        """
        Run the complete HR email campaign.

        For every contact, a random template ID (1-10) is
        selected. The matching Subject, Body, and Resume are
        all resolved from that same ID, keeping the three
        perfectly synchronized.
        """

        contacts = self.contacts.load_contacts()

        if not contacts:

            print("No contacts found.")
            return

        total_contacts = len(contacts)

        status = self.tracker.campaign_status(
            total_contacts
        )

        print("=" * 60)
        print("CAMPAIGN ANALYSIS")
        print("=" * 60)
        print(f"Dataset Size   : {status['total']}")
        print(f"Already Sent   : {status['sent']}")
        print(f"Failed Earlier : {status['failed']}")
        print(f"Remaining      : {status['remaining']}")
        print("=" * 60)
        print()

        sent_today = 0
        failed_today = 0
        skipped = 0

        progress = len(
            self.tracker.sent_emails
        )

        with self.gmail:

            for contact in contacts:

                email = (
                    contact["email"]
                    .strip()
                    .lower()
                )

                # -----------------------------------------
                # Skip already sent emails
                # -----------------------------------------

                if self.tracker.is_already_sent(email):

                    skipped += 1
                    continue

                progress += 1

                print(
                    f"[{progress}/{total_contacts}] "
                    f"Sending to {email}"
                )

                try:

                    # template_id keeps Subject ↔ Body ↔ Resume
                    # in sync — all three share the same index.
                    template_id, subject, body = (
                        self.builder.build_email(
                            first_name=contact["full_name"],
                            company=contact["company"],
                        )
                    )

                    resume = RESUME_MAP[template_id]

                    self.gmail.send_email(
                    recipient=email,
                    subject=subject,
                    body=body,
                    attachments=[resume],
)

                    self.logger.log_success(
                        recruiter=contact["full_name"],
                        email=email,
                        company=contact["company"],
                        role=contact["role"],
                    )

                    # Update tracker immediately

                    self.tracker.sent_emails.add(email)

                    sent_today += 1

                    print(
                        f"✓ Email Sent  "
                        f"[Template {template_id} | "
                        f"{resume.name}]"
                    )

                except Exception as error:

                    failed_today += 1

                    self.logger.log_failure(
                        recruiter=contact["full_name"],
                        email=email,
                        company=contact["company"],
                        role=contact["role"],
                        error=str(error),
                    )

                    print(f"✗ Failed : {error}")

                remaining = (
                    total_contacts
                    - progress
                )

                if remaining > 0:

                    delay = get_random_delay()

                    print(
                        f"Next email in {delay} sec..."
                    )

                    time.sleep(delay)

        print()

        print("=" * 60)
        print("CAMPAIGN SUMMARY")
        print("=" * 60)
        print(f"Dataset Size : {total_contacts}")
        print(f"Already Sent : {skipped}")
        print(f"Sent Today   : {sent_today}")
        print(f"Failed Today : {failed_today}")
        print(f"Remaining    : {total_contacts - progress}")
        print("=" * 60)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("HR EMAIL AUTOMATION")
    print("=" * 60)

    try:

        campaign = EmailCampaign()

        campaign.run()

        print()
        print("=" * 60)
        print("CAMPAIGN COMPLETED SUCCESSFULLY")
        print("=" * 60)

        contacts = campaign.contacts.load_contacts()
        status = campaign.tracker.campaign_status(
            len(contacts)
        )

        print("=" * 60)
        print("CAMPAIGN ANALYSIS")
        print("=" * 60)
        print(f"Dataset Size     : {status['total']}")
        print(f"Already Sent     : {status['sent']}")
        print(f"Failed Earlier   : {status['failed']}")
        print(f"Remaining        : {status['remaining']}")
        print(f"Completion       : {status['completion']} %")
        print("=" * 60)
        print()

    except KeyboardInterrupt:

        print()
        print("=" * 60)
        print("Campaign cancelled by user.")
        print("=" * 60)

    except Exception as error:

        print()
        print("=" * 60)
        print("CAMPAIGN FAILED")
        print("=" * 60)
        print(error)
        print("=" * 60)