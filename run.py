"""
run.py

Single entry point for the
HR Email Automation System.

Usage:
    python run.py

Author: Vishwash Gurav
"""

from __future__ import annotations

from send_emails import EmailCampaign


def main() -> None:
    """
    Launch the HR Email Automation campaign.
    """

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


if __name__ == "__main__":
    main()