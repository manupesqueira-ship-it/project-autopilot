from __future__ import annotations

import argparse
import os
import urllib.parse
import urllib.request
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv

from project_loader import load_project

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@dataclass
class TelegramResult:
    sent: bool
    reason: str


def _credentials(project_id: str) -> tuple[str | None, str | None]:
    prefix = project_id.upper().replace("-", "_")
    token = os.environ.get(f"{prefix}_TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get(f"{prefix}_TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")
    return token, chat_id


def send_alert(project_id: str, kind: str, message: str, enabled: bool = True) -> TelegramResult:
    if not enabled:
        return TelegramResult(False, "telegram disabled")

    token, chat_id = _credentials(project_id)
    if not token or not chat_id:
        return TelegramResult(False, "missing Telegram credentials")

    text = f"Project Autopilot alert [{project_id}]: {kind}\n\n{message}"
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    request = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if 200 <= response.status < 300:
                return TelegramResult(True, "sent")
            return TelegramResult(False, f"telegram returned HTTP {response.status}")
    except Exception as exc:  # pragma: no cover - network dependent
        return TelegramResult(False, str(exc))


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Autopilot Telegram alerts.")
    parser.add_argument("--project", default="mira", help="Project id from project_autopilot/config/projects.")
    parser.add_argument("--test", action="store_true", help="Send an explicit test alert.")
    args = parser.parse_args()

    project = load_project(args.project)
    if not args.test:
        parser.print_help()
        return 0

    result = send_alert(
        project.project_id,
        "test",
        f"Telegram alert test for {project.project_name}.",
        enabled=project.telegram_enabled,
    )
    print(result.reason)
    return 0 if result.sent else 2


if __name__ == "__main__":
    raise SystemExit(main())

