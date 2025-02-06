from datetime import datetime, timezone


def datetime_utc_now() -> datetime:
    """Текущее время в UTC."""
    return datetime.now(timezone.utc)
