"""
contact_loader.py

Loads recruiter contacts from Excel.

Responsibilities:
- Read contacts.xlsx
- Validate required columns
- Clean contact data
- Remove duplicate emails
- Extract first names
- Return validated contact list

Author: Vishwash Gurav
"""

from __future__ import annotations

import re

import pandas as pd  # type: ignore[reportMissingModuleSource]

from config import HR_CONTACTS_FILE
from utils import clean_text, file_exists


COLUMN_MAPPING: dict[str, str] = {
    "full_name": "Name",
    "email": "Email",
    "role": "Title",
    "company": "Company",
}

REQUIRED_COLUMNS = list(COLUMN_MAPPING.values())


class ContactLoader:
    """
    Loads and validates recruiter contacts from an Excel file.
    """

    REQUIRED_COLUMNS = REQUIRED_COLUMNS

    EMAIL_PATTERN = re.compile(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    def __init__(self) -> None:
        self.contacts_file = HR_CONTACTS_FILE

    def load_contacts(self) -> list[dict]:
        """
        Load recruiter contacts from Excel.

        Returns:
            list[dict]: Validated recruiter records.
        """

        if not file_exists(self.contacts_file):
            raise FileNotFoundError(
                f"Contacts file not found:\n{self.contacts_file}"
            )

        dataframe = self._read_contacts()
        self._validate_columns(dataframe)

        contacts: list[dict] = []
        seen_emails: set[str] = set()

        for _, row in dataframe.iterrows():
            contact = self._normalize_row(row)

            if not self._is_valid_contact(contact, seen_emails):
                continue

            seen_emails.add(contact["email"])
            contacts.append(contact)

        return contacts

    def _read_contacts(self) -> pd.DataFrame:
        """
        Read the Excel contacts file into a DataFrame.

        Raises:
            RuntimeError: If the file cannot be loaded.
        """
        try:
            return pd.read_excel(self.contacts_file)
        except Exception as exc:
            raise RuntimeError(
                f"Unable to read contacts file.\n{exc}"
            ) from exc

    def _normalize_row(self, row: pd.Series) -> dict[str, str]:
        """
        Normalize a row using the shared column mapping.
        """
        normalized: dict[str, str] = {}

        for field_key, column_name in COLUMN_MAPPING.items():
            raw_value = row.get(column_name, "")
            normalized[field_key] = clean_text(raw_value)

        normalized["email"] = normalized["email"].lower()
        normalized["first_name"] = self._extract_first_name(
            normalized["full_name"]
        )

        return normalized

    def _is_valid_contact(
        self,
        contact: dict[str, str],
        seen_emails: set[str],
    ) -> bool:
        """
        Validate normalized contact data.
        """
        if not contact["full_name"]:
            return False

        if not contact["email"]:
            return False

        if not self._is_valid_email(contact["email"]):
            return False

        if contact["email"] in seen_emails:
            return False

        return True

    def _validate_columns(self, dataframe: pd.DataFrame) -> None:
        """
        Ensure all required columns exist.
        """
        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in dataframe.columns
        ]

        if missing:
            raise ValueError(
                "Missing required columns:\n"
                + "\n".join(missing)
            )

    def _extract_first_name(self, full_name: str) -> str:
        """
        Extract first name from full name.
        """
        parts = full_name.split()

        if not parts:
            return "Recruiter"

        return parts[0]

    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email format.
        """
        return bool(self.EMAIL_PATTERN.fullmatch(email))


if __name__ == "__main__":
    loader = ContactLoader()
    contacts = loader.load_contacts()

    print("=" * 60)
    print(f"Successfully loaded {len(contacts)} contact(s)")
    print("=" * 60)

    for index, contact in enumerate(contacts[:5], start=1):
        print(f"{index}. {contact}")

    if len(contacts) > 5:
        print(f"\n... and {len(contacts) - 5} more contact(s).")