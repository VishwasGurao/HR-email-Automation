"""
utils.py

Common utility functions used throughout the
HR Email Automation System.

Responsibilities:
- Validate email addresses
- Generate current timestamp
- Generate random delay
- Check file existence
- Clean text

Author: Vishwas Gurav
"""

from __future__ import annotations

import random
import re
from datetime import datetime
from pathlib import Path

from config import (
    DATE_FORMAT,
    MAX_DELAY_SECONDS,
    MIN_DELAY_SECONDS,
)

# ==========================================================
# Email Validation Pattern
# ==========================================================

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


# ==========================================================
# Email Validation
# ==========================================================

def is_valid_email(email: str) -> bool:
    """
    Validate an email address.

    Args:
        email: Email address.

    Returns:
        True if valid, otherwise False.
    """

    if not email:
        return False

    return bool(EMAIL_PATTERN.fullmatch(email.strip()))


# ==========================================================
# Current Timestamp
# ==========================================================

def get_current_timestamp() -> str:
    """
    Return current date and time.

    Returns:
        Formatted timestamp.
    """

    return datetime.now().strftime(DATE_FORMAT)


# ==========================================================
# Random Delay
# ==========================================================

def get_random_delay() -> int:
    """
    Generate a random delay.

    Returns:
        Delay in seconds.
    """

    return random.randint(
        MIN_DELAY_SECONDS,
        MAX_DELAY_SECONDS,
    )


# ==========================================================
# File Exists
# ==========================================================

def file_exists(file_path: Path) -> bool:
    """
    Check whether a file exists.

    Args:
        file_path: Path object.

    Returns:
        True if file exists.
    """

    return file_path.exists() and file_path.is_file()


# ==========================================================
# Clean Text
# ==========================================================

def clean_text(text: str | None) -> str:
    """
    Remove extra spaces.

    Args:
        text: Input text.

    Returns:
        Clean text.
    """

    if text is None:
        return ""

    return " ".join(text.strip().split())


# ==========================================================
# Self Test
# ==========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("UTILS MODULE")
    print("=" * 50)

    print(f"Valid Email      : {is_valid_email('abc@gmail.com')}")
    print(f"Invalid Email    : {is_valid_email('abc@gmail')}")
    print(f"Timestamp        : {get_current_timestamp()}")
    print(f"Random Delay     : {get_random_delay()} sec")
    print(f"File Exists      : {file_exists(Path('config.py'))}")
    print(f"Clean Text       : '{clean_text('   Hello    Vishwas   ')}'")

    print("=" * 50)
    print("UTILS TEST PASSED")
    print("=" * 50)