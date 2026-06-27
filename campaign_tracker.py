"""
campaign_tracker.py

Tracks email campaign progress for the
HR Email Automation System.

Responsibilities:
- Load previous email logs
- Detect already sent emails
- Detect failed emails
- Provide campaign statistics
- Support resume campaign

Author: Vishwash Gurav
"""

from __future__ import annotations

import csv
from pathlib import Path

from config import (
    EMAIL_LOG_FILE,
    STATUS_FAILED,
    STATUS_SENT,
)
from utils import file_exists


class CampaignTracker:
    """
    Tracks previous email campaign history.
    """

    def __init__(
        self,
        log_file: Path = EMAIL_LOG_FILE,
    ) -> None:

        self.log_file = log_file

        self.sent_emails: set[str] = set()

        self.failed_emails: set[str] = set()

        self.total_logs = 0

        self._load_logs()

    # ---------------------------------------------------------
    # LOAD LOG FILE
    # ---------------------------------------------------------

    def _load_logs(self) -> None:
        """
        Load existing email log.
        """

        if not file_exists(self.log_file):
            return

        with self.log_file.open(
            mode="r",
            newline="",
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                self.total_logs += 1

                email = row["Email"].strip().lower()

                status = row["Status"].strip()

                if status == STATUS_SENT:

                    self.sent_emails.add(email)

                elif status == STATUS_FAILED:

                    self.failed_emails.add(email)

    # ---------------------------------------------------------
    # CHECK SENT STATUS
    # ---------------------------------------------------------

    def is_already_sent(
        self,
        email: str,
    ) -> bool:
        """
        Check whether an email has already
        been sent successfully.
        """

        return (
            email.strip().lower()
            in self.sent_emails
        )

    # ---------------------------------------------------------
    # CHECK FAILED STATUS
    # ---------------------------------------------------------

    def is_failed(
        self,
        email: str,
    ) -> bool:
        """
        Check whether an email failed
        in a previous campaign.
        """

        return (
            email.strip().lower()
            in self.failed_emails
        )

    # ---------------------------------------------------------
    # SHOULD SEND?
    # ---------------------------------------------------------

    def should_send(
        self,
        email: str,
    ) -> bool:
        """
        Decide whether an email should be sent.

        Returns:
            True  -> Send
            False -> Skip
        """

        return not self.is_already_sent(email)

    # ---------------------------------------------------------
    # GET SENT EMAILS
    # ---------------------------------------------------------

    def get_sent_emails(self) -> set[str]:
        """
        Return all successfully sent emails.
        """

        return self.sent_emails.copy()

    # ---------------------------------------------------------
    # GET FAILED EMAILS
    # ---------------------------------------------------------

    def get_failed_emails(self) -> set[str]:
        """
        Return all failed emails.
        """

        return self.failed_emails.copy()

    # ---------------------------------------------------------
    # CAMPAIGN SUMMARY
    # ---------------------------------------------------------

    def get_summary(self) -> dict:
        """
        Return campaign statistics.
        """

        return {
            "total_logs": self.total_logs,
            "sent": len(self.sent_emails),
            "failed": len(self.failed_emails),
            "unique_emails": (
                len(
                    self.sent_emails.union(
                        self.failed_emails
                    )
                )
            ),
        }

    # ---------------------------------------------------------
    # PRINT SUMMARY
    # ---------------------------------------------------------

    def print_summary(self) -> None:
        """
        Print campaign statistics.
        """

        summary = self.get_summary()

        print("=" * 60)
        print("CAMPAIGN ANALYSIS")
        print("=" * 60)

        print(
            f"Total Log Records : "
            f"{summary['total_logs']}"
        )

        print(
            f"Already Sent     : "
            f"{summary['sent']}"
        )

        print(
            f"Failed           : "
            f"{summary['failed']}"
        )

        print(
            f"Unique Emails    : "
            f"{summary['unique_emails']}"
        )

        print("=" * 60)

    # ---------------------------------------------------------
    # REMAINING CONTACTS
    # ---------------------------------------------------------

    def get_remaining_contacts(
        self,
        total_contacts: int,
    ) -> int:
        """
        Calculate remaining contacts.
        """

        remaining = (
            total_contacts
            - len(self.sent_emails)
        )

        return max(0, remaining)

    # ---------------------------------------------------------
    # CAMPAIGN COMPLETION
    # ---------------------------------------------------------

    def get_completion_percentage(
        self,
        total_contacts: int,
    ) -> float:
        """
        Calculate campaign completion percentage.
        """

        if total_contacts <= 0:
            return 0.0

        return round(
            (
                len(self.sent_emails)
                / total_contacts
            )
            * 100,
            2,
        )

    # ---------------------------------------------------------
    # ESTIMATED TIME
    # ---------------------------------------------------------

    def estimate_remaining_time(
        self,
        total_contacts: int,
        average_delay: int,
    ) -> int:
        """
        Estimate remaining campaign time.

        Returns:
            Remaining seconds.
        """

        remaining = self.get_remaining_contacts(
            total_contacts,
        )

        return remaining * average_delay

    # ---------------------------------------------------------
    # LAST SENT EMAIL
    # ---------------------------------------------------------

    def get_last_sent_count(self) -> int:
        """
        Return number of successful emails.
        """

        return len(self.sent_emails)

    # ---------------------------------------------------------
    # DUPLICATE EMAIL DETECTION
    # ---------------------------------------------------------

    def find_duplicate_emails(
        self,
        contacts: list[dict],
    ) -> list[str]:
        """
        Find duplicate emails in contact list.
        """

        seen: set[str] = set()

        duplicates: list[str] = []

        for contact in contacts:

            email = (
                contact["email"]
                .strip()
                .lower()
            )

            if email in seen:

                duplicates.append(email)

            else:

                seen.add(email)

        return duplicates

    # ---------------------------------------------------------
    # CAMPAIGN STATUS
    # ---------------------------------------------------------

    def campaign_status(
        self,
        total_contacts: int,
    ) -> dict:
        """
        Return complete campaign status.
        """

        sent = len(self.sent_emails)

        failed = len(self.failed_emails)

        remaining = max(
            0,
            total_contacts - sent,
        )

        completion = (
            round(
                (sent / total_contacts) * 100,
                2,
            )
            if total_contacts > 0
            else 0.0
        )

        return {
            "total": total_contacts,
            "sent": sent,
            "failed": failed,
            "remaining": remaining,
            "completion": completion,
        }

    # ---------------------------------------------------------
    # RESET TRACKER
    # ---------------------------------------------------------

    def reset(self) -> None:
        """
        Clear all cached campaign data.
        """

        self.sent_emails.clear()

        self.failed_emails.clear()

        self.total_logs = 0

    # ---------------------------------------------------------
    # RELOAD TRACKER
    # ---------------------------------------------------------

    def reload(self) -> None:
        """
        Reload campaign log from disk.
        """

        self.sent_emails.clear()
        self.failed_emails.clear()
        self.total_logs = 0

        self._load_logs()


# ---------------------------------------------------------
# SELF TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("CAMPAIGN TRACKER")
    print("=" * 60)

    try:

        tracker = CampaignTracker()

        tracker.print_summary()

        print()

        print(
            "CAMPAIGN TRACKER TEST PASSED"
        )

    except Exception as error:

        print(
            "CAMPAIGN TRACKER TEST FAILED"
        )

        print(error)

    print("=" * 60)
