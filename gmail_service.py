"""
gmail_service.py

Production-ready Gmail SMTP service for the
HR Email Automation System.

Responsibilities
----------------
- Connect to Gmail SMTP
- Authenticate using App Password
- Build plain-text EmailMessage
- Send plain-text emails
- Attach resume and other files
- Handle SMTP exceptions gracefully

Author: Vishwash Gurav
"""

from __future__ import annotations

import mimetypes
import smtplib
import ssl

from email.message import EmailMessage
from pathlib import Path

from config import (
    APP_PASSWORD,
    EMAIL_ADDRESS,
    SMTP_PORT,
    SMTP_SERVER,
)

from utils import is_valid_email


class GmailService:
    """
    Gmail SMTP service.

    This class is responsible only for
    sending emails.

    It does not know anything about
    Excel,
    Template selection,
    Logging,
    or Campaign logic.
    """

    def __init__(
        self,
        timeout: float = 10.0,
    ) -> None:

        self._timeout = timeout
        self._server: smtplib.SMTP | None = None

    # ---------------------------------------------------------
    # SMTP CONNECTION
    # ---------------------------------------------------------

    def connect(self) -> None:
        """
        Connect and authenticate
        with Gmail SMTP.
        """

        if self._server is not None:
            return

        try:

            server = smtplib.SMTP(
                SMTP_SERVER,
                SMTP_PORT,
                timeout=self._timeout,
            )

            server.ehlo()

            context = ssl.create_default_context()

            server.starttls(
                context=context,
            )

            server.ehlo()

            server.login(
                EMAIL_ADDRESS,
                APP_PASSWORD,
            )

            self._server = server

        except smtplib.SMTPAuthenticationError as error:

            raise RuntimeError(
                "SMTP authentication failed."
            ) from error

        except smtplib.SMTPException as error:

            raise RuntimeError(
                f"SMTP connection failed: {error}"
            ) from error

        except OSError as error:

            raise RuntimeError(
                f"Network error: {error}"
            ) from error

    # ---------------------------------------------------------
    # DISCONNECT
    # ---------------------------------------------------------

    def disconnect(self) -> None:
        """
        Disconnect from Gmail SMTP.
        """

        if self._server is None:
            return

        try:

            self._server.quit()

        except smtplib.SMTPServerDisconnected:
            pass

        finally:

            self._server = None

    # ---------------------------------------------------------
    # BUILD EMAIL
    # ---------------------------------------------------------

    def _build_message(
        self,
        recipient: str,
        subject: str,
        body: str,
    ) -> EmailMessage:
        """
        Create a plain-text email message.
        """

        message = EmailMessage()

        message["From"] = EMAIL_ADDRESS
        message["To"] = recipient
        message["Subject"] = subject

        message.set_content(body)

        return message

    # ---------------------------------------------------------
    # ATTACH FILE
    # ---------------------------------------------------------

    def _attach_file(
        self,
        message: EmailMessage,
        file_path: Path,
    ) -> None:
        """
        Attach a file to the email.
        """

        if not file_path.is_file():

            raise FileNotFoundError(
                f"Attachment not found:\n{file_path}"
            )

        content_type, _ = mimetypes.guess_type(
            str(file_path)
        )

        if content_type is None:

            maintype = "application"
            subtype = "octet-stream"

        else:

            maintype, subtype = content_type.split(
                "/",
                1,
            )

        with file_path.open("rb") as attachment:

            message.add_attachment(
                attachment.read(),
                maintype=maintype,
                subtype=subtype,
                filename=file_path.name,
            )

    # ---------------------------------------------------------
    # SEND EMAIL
    # ---------------------------------------------------------

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        attachments: list[Path] | None = None,
    ) -> None:
        """
        Send a plain-text email with optional attachments.
        """

        if not is_valid_email(recipient):
            raise ValueError(
                f"Invalid email address: {recipient}"
            )

        if self._server is None:
            self.connect()

        message = self._build_message(
            recipient=recipient,
            subject=subject,
            body=body,
        )

        if attachments:

            for file_path in attachments:

                if not isinstance(file_path, Path):

                    raise TypeError(
                        "Attachments must be pathlib.Path objects."
                    )

                self._attach_file(
                    message,
                    file_path,
                )

        try:

            if self._server is None:
                raise RuntimeError(
                    "SMTP server is not connected."
                )

            self._server.send_message(message)

        except smtplib.SMTPRecipientsRefused as error:

            raise RuntimeError(
                f"Recipient refused: {error}"
            ) from error

        except smtplib.SMTPException as error:

            raise RuntimeError(
                f"SMTP Error: {error}"
            ) from error

        except OSError as error:

            raise RuntimeError(
                f"Network Error: {error}"
            ) from error

    # ---------------------------------------------------------
    # CONTEXT MANAGER
    # ---------------------------------------------------------

    def __enter__(self) -> "GmailService":

        self.connect()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        self.disconnect()


# ---------------------------------------------------------
# SELF TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("GMAIL SERVICE")
    print("=" * 60)

    try:

        with GmailService():
            pass

        print("Connection Successful")

    except Exception as error:

        print("Connection Failed")
        print(error)

    print("=" * 60)