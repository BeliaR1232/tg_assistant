import logging
from datetime import datetime

from src.reminders.schemes import EventScheme

logger = logging.getLogger(__name__)


def parse_date_time(date_time_str: str):
    try:
        return datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return None


def format_event_list(events: tuple[EventScheme, ...]):
    return "\n".join(
        [
            f"📅 ID:{e.id}\nОписание: {e.description}\nВремя события: {e.event_datetime}\nПовтор: {e.repeat_interval.value if e.repeat_interval else 'однократное'}\n"
            for e in events
        ]
    )
