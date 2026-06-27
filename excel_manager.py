"""
excel_manager.py

Excel Manager for HR Email Automation System.

Responsibilities
----------------
- Load HR contacts workbook
- Validate required columns
- Read contacts
- Prepare cleaned workbook
- Provide reusable Excel operations

Author: Vishwas Gurav
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from config import (
    CLEAN_CONTACTS_FILE,
    HR_CONTACTS_FILE,
    STATUS_PENDING,
)
from utils import (
    clean_text,
    file_exists,
    is_valid_email,
)


class ExcelManager:
    """
    Handles all Excel related operations.
    """

    REQUIRED_COLUMNS = [
        "Name",
        "Email",
        "Title",
        "Company",
    ]

    OUTPUT_COLUMNS = [
        "HR Name",
        "Email",
        "Company",
        "Designation",
        "Status",
        "Sent Date",
        "Follow-up",
        "Notes",
    ]

    def __init__(
        self,
        input_file: Path = HR_CONTACTS_FILE,
        output_file: Path = CLEAN_CONTACTS_FILE,
    ) -> None:

        self.input_file = input_file
        self.output_file = output_file

        self.contacts: pd.DataFrame = pd.DataFrame()

    def load_contacts(self) -> pd.DataFrame:
        """
        Load HR contacts Excel.

        Returns
        -------
        pandas.DataFrame
        """

        if not file_exists(self.input_file):
            raise FileNotFoundError(
                f"Input Excel not found:\n{self.input_file}"
            )

        self.contacts = pd.read_excel(
            self.input_file,
            engine="openpyxl",
        )

        self._validate_columns()

        return self.contacts

    def _validate_columns(self) -> None:
        """
        Validate required columns.
        """

        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in self.contacts.columns
        ]

        if missing:

            raise ValueError(
                f"Missing columns: {', '.join(missing)}"
            )

    def clean_contacts(self) -> pd.DataFrame:
        """
        Clean HR contact data.

        Returns
        -------
        pandas.DataFrame
        """

        df = self.contacts.copy()

        df["Name"] = df["Name"].apply(clean_text)

        df["Email"] = (
            df["Email"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        df["Company"] = df["Company"].apply(clean_text)

        df["Title"] = df["Title"].apply(clean_text)

        df = df[
            df["Email"].apply(is_valid_email)
        ]

        df = df.drop_duplicates(
            subset="Email",
            keep="first",
        )

        cleaned = pd.DataFrame()

        cleaned["HR Name"] = df["Name"]

        cleaned["Email"] = df["Email"]

        cleaned["Company"] = df["Company"]

        cleaned["Designation"] = df["Title"]

        cleaned["Status"] = STATUS_PENDING

        cleaned["Sent Date"] = ""

        cleaned["Follow-up"] = "No"

        cleaned["Notes"] = ""

        self.contacts = cleaned

        return cleaned
    
    def save_cleaned_contacts(self) -> None:
        """
        Save cleaned contacts to output Excel.
        """

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.contacts.to_excel(
            self.output_file,
            index=False,
            engine="openpyxl",
        )

    def load_cleaned_contacts(self) -> pd.DataFrame:
        """
        Load cleaned contacts workbook.

        Returns
        -------
        pandas.DataFrame
        """

        if not file_exists(self.output_file):
            raise FileNotFoundError(
                f"Cleaned contacts file not found:\n{self.output_file}"
            )

        self.contacts = pd.read_excel(
            self.output_file,
            engine="openpyxl",
        )

        return self.contacts

    def get_pending_contacts(self) -> list[dict[str, Any]]:
        """
        Return all pending contacts.

        Returns
        -------
        list[dict]
        """

        if self.contacts.empty:
            self.load_cleaned_contacts()

        pending = self.contacts[
            self.contacts["Status"] == STATUS_PENDING
        ]

        return pending.to_dict(
            orient="records"
        )

    def total_contacts(self) -> int:
        """
        Return total contacts.
        """

        return len(self.contacts)

    def total_pending(self) -> int:
        """
        Return pending contacts count.
        """

        if self.contacts.empty:
            return 0

        return len(
            self.contacts[
                self.contacts["Status"] == STATUS_PENDING
            ]
        )

    def total_sent(self) -> int:
        """
        Return sent contacts count.
        """

        if self.contacts.empty:
            return 0

        return len(
            self.contacts[
                self.contacts["Status"] == "Sent"
            ]
        )

    def total_failed(self) -> int:
        """
        Return failed contacts count.
        """

        if self.contacts.empty:
            return 0

        return len(
            self.contacts[
                self.contacts["Status"] == "Failed"
            ]
        )
    def update_contact_status(
        self,
        email: str,
        status: str,
        sent_date: str = "",
        follow_up: str = "No",
        notes: str = "",
    ) -> None:
        """
        Update a contact's status.

        Args:
            email:
                Recipient email.

            status:
                Pending / Sent / Failed

            sent_date:
                Date and time of sending.

            follow_up:
                Follow-up status.

            notes:
                Error or remarks.
        """

        if self.contacts.empty:
            self.load_cleaned_contacts()

        mask = self.contacts["Email"].str.lower() == email.strip().lower()

        if mask.any():

            self.contacts.loc[mask, "Status"] = status
            self.contacts.loc[mask, "Sent Date"] = sent_date
            self.contacts.loc[mask, "Follow-up"] = follow_up
            self.contacts.loc[mask, "Notes"] = notes

    def save(self) -> None:
        """
        Save current dataframe.
        """

        self.contacts.to_excel(
            self.output_file,
            index=False,
            engine="openpyxl",
        )


if __name__ == "__main__":

    print("=" * 60)
    print("EXCEL MANAGER SELF TEST")
    print("=" * 60)

    try:

        manager = ExcelManager()

        print("Loading HR contacts...")
        manager.load_contacts()

        print("Cleaning contacts...")
        manager.clean_contacts()

        print("Saving cleaned workbook...")
        manager.save_cleaned_contacts()

        print()
        print("Statistics")
        print("-" * 60)

        print(f"Total Contacts : {manager.total_contacts()}")
        print(f"Pending         : {manager.total_pending()}")
        print(f"Sent            : {manager.total_sent()}")
        print(f"Failed          : {manager.total_failed()}")

        print()

        pending = manager.get_pending_contacts()

        print(f"Pending Records Loaded : {len(pending)}")

        if pending:

            print()

            print("First Contact")
            print("-" * 60)

            first = pending[0]

            for key, value in first.items():
                print(f"{key:<15}: {value}")

        print()

        print("=" * 60)
        print("EXCEL MANAGER TEST PASSED")
        print("=" * 60)

    except Exception as error:

        print()

        print("=" * 60)
        print("EXCEL MANAGER TEST FAILED")
        print("=" * 60)

        print(error)