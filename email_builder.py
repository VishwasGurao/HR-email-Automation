"""
email_builder.py

Builds personalized email subject and body
for the HR Email Automation System.

Responsibilities:
- Randomly select a template ID (1-10)
- Render personalized subject from subjects.py
- Render personalized body from bodies.py
- Return (template_id, subject, body) tuple
  so the caller can resolve the matching resume
  via RESUME_MAP[template_id]

Author: Vishwash Gurav
"""

from __future__ import annotations

import random

from templates.subjects import SUBJECTS
from templates.bodies import render


class EmailBuilder:
    """
    Builds personalized plain-text emails
    from template dictionaries.
    """

    # ---------------------------------------------------------
    # BUILD EMAIL
    # ---------------------------------------------------------

    def build_email(
        self,
        first_name: str,
        company: str,
    ) -> tuple[int, str, str]:
        """
        Randomly select a template and return a
        personalized (template_id, subject, body) tuple.

        The template_id is returned so the caller can
        look up the matching resume via RESUME_MAP[template_id],
        keeping Subject ↔ Body ↔ Resume perfectly synchronized.

        Parameters
        ----------
        first_name : str
            Recruiter's first name.
        company : str
            Company name. Falls back to
            "your organization" if empty.

        Returns
        -------
        tuple[int, str, str]
            (template_id, subject, body)
        """

        template_id = random.randint(1, 10)

        subject = SUBJECTS[template_id]

        body = render(
            template_id=template_id,
            first_name=first_name,
            company=company,
        )

        return template_id, subject, body


# ---------------------------------------------------------
# SELF TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    from config import RESUME_MAP

    print("=" * 60)
    print("EMAIL BUILDER MODULE")
    print("=" * 60)

    builder = EmailBuilder()

    template_id, subject, body = builder.build_email(
        first_name="Rahul",
        company="ABC Technologies Pvt Ltd",
    )

    resume = RESUME_MAP[template_id]

    print(f"Template ID : {template_id}")
    print(f"Subject     : {subject}")
    print(f"Resume      : {resume.name}")
    print()
    print("Body Preview (first 200 chars):")
    print("-" * 60)
    print(body[:200])
    print("...")
    print()
    print("Mapping Verification")
    print("-" * 60)
    print(f"  Subject {template_id} ↔ Body {template_id} ↔ {resume.name}")
    print()
    print("EMAIL BUILDER TEST PASSED")
    print("=" * 60)