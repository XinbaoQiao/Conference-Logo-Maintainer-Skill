#!/usr/bin/env python3
"""Send scheduled logo-maintenance review notification by SMTP."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage


REQUIRED_ENV = ("NOTIFY_EMAIL", "SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD")


def configured() -> bool:
    missing = [name for name in REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        print("Email notification skipped; missing env: " + ", ".join(missing))
        return False
    return True


def main() -> int:
    if not configured():
        return 0

    to_addr = os.environ["NOTIFY_EMAIL"]
    from_addr = os.environ.get("SMTP_FROM") or os.environ["SMTP_USERNAME"]
    host = os.environ["SMTP_HOST"]
    port = int(os.environ.get("SMTP_PORT") or "587")
    branch = os.environ.get("UPDATE_BRANCH") or "scheduled-logo-maintenance"
    scope = os.environ.get("MAINTENANCE_SCOPE") or "monthly-focus"
    repo = os.environ.get("GITHUB_REPOSITORY") or "CS-Conference-Logo-Maintainer"
    run_url = os.environ.get("RUN_URL") or ""
    branch_url = os.environ.get("BRANCH_URL") or ""

    message = EmailMessage()
    message["Subject"] = f"[CS Conference Logo Maintainer] Review {scope} logo update"
    message["From"] = from_addr
    message["To"] = to_addr
    message.set_content(
        "\n".join(
            [
                "The scheduled conference-logo update has been pushed for review.",
                "",
                f"Repository: {repo}",
                f"Staging branch: {branch}",
                f"Scope: {scope}",
                f"Branch URL: {branch_url}",
                f"Workflow run: {run_url}",
                "",
                "Please review the changed logo assets and reports before the 10th.",
                "If no manual action is taken, the scheduled workflow will merge the staging branch into main on the 10th and delete the staging branch.",
            ]
        )
    )

    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(message)
    print(f"Email notification sent to {to_addr}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
