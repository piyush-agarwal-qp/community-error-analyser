"""Shared utilities — week range calculation and project root."""

from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent

load_dotenv(ROOT / ".env")


def get_week_range() -> tuple[str, str]:
    """Return (last_friday, last_thursday) as ISO date strings for the most recent completed week."""
    today = date.today()
    days_back = (today.weekday() - 3) % 7 or 7
    last_thursday = today - timedelta(days=days_back)
    last_friday = last_thursday - timedelta(days=6)
    return str(last_friday), str(last_thursday)
