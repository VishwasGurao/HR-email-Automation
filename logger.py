"""
logger.py

Logging module for the
HR Email Automation System.

Responsibilities:
- Create CSV log automatically
- Store email campaign results
- Record timestamps
- Record success and failure
- Never overwrite existing logs

Author: Vishwash Gurav
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from config import (
    DATE_FORMAT,
    EMAIL_LOG_FILE,
    STATUS_FAILED,
    STATUS_SENT,
)
from utils import file_exists


class EmailLogger:
    """
    Handles email campaign logging.
    """

    HEADERS = [
        "Timestamp",
        "Recruiter",
        "Email",
        "Company",
        "Role",
        "Status",
        "Message",
    ]

    def __init__(
        self,
        log_file: Path = EMAIL_LOG_FILE,
    ) -> None:
        """
        Initialize logger.
        """

        self.log_file = log_file

        self.log_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._create_log_file()

    # ---------------------------------------------------------
    # CREATE LOG FILE
    # ---------------------------------------------------------

    def _create_log_file(self) -> None:
        """
        Create log file if it does not exist.
        """

        if file_exists(self.log_file):
            return

        with self.log_file.open(
            mode="w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(file)

            writer.writerow(self.HEADERS)

    # ---------------------------------------------------------
    # WRITE LOG ENTRY
    # ---------------------------------------------------------

    def log(
        self,
        recruiter: str,
        email: str,
        company: str,
        role: str,
        status: str,
        message: str,
    ) -> None:
        """
        Write one log entry.
        """
        with self.log_file.open(
            mode="a",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(file)

            writer.writerow(
                [
                    datetime.now().strftime(
                        DATE_FORMAT,
                    ),
                    recruiter,
                    email,
                    company,
                    role,
                    status,
                    message,
                ]
            )

    # ---------------------------------------------------------
    # SUCCESS LOG
    # ---------------------------------------------------------

    def log_success(
        self,
        recruiter: str,
        email: str,
        company: str,
        role: str,
    ) -> None:
        """
        Log successful email.
        """

        self.log(
            recruiter=recruiter,
            email=email,
            company=company,
            role=role,
            status=STATUS_SENT,
            message="Email sent successfully.",
        )

    # ---------------------------------------------------------
    # FAILURE LOG
    # ---------------------------------------------------------

    def log_failure(
        self,
        recruiter: str,
        email: str,
        company: str,
        role: str,
        error: str,
    ) -> None:
        """
        Log failed email.
        """

        self.log(
            recruiter=recruiter,
            email=email,
            company=company,
            role=role,
            status=STATUS_FAILED,
            message=error,
        )
        # ---------------------------------------------------------
# SELF TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("LOGGER MODULE")
    print("=" * 60)

    try:

        logger = EmailLogger()

        logger.log_success(
            recruiter="John Doe",
            email="john@example.com",
            company="ABC Pvt Ltd",
            role="HR Manager",
        )

        logger.log_failure(
            recruiter="Jane Smith",
            email="jane@example.com",
            company="XYZ Technologies",
            role="Talent Acquisition",
            error="SMTP Authentication Failed",
        )

        print("Logger initialized successfully.")
        print(f"Log File : {EMAIL_LOG_FILE}")

        print()
        print("LOGGER TEST PASSED")

    except Exception as error:

        print("LOGGER TEST FAILED")
        print(error)

    print("=" * 60)