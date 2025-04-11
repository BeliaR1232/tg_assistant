from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class EventRepeatInterval(Enum):
    DAILY = "ежедневно"
    WEEKLY = "еженедельно"
    MONTHLY = "ежемесячно"
    SIXMONTH = "раз в полгода"
    YEARLY = "ежегодно"


class EventCreateScheme(BaseModel):
    description: str
    event_datetime: datetime
    repeat_interval: EventRepeatInterval | None
    message_count: int | None = None


class EventScheme(BaseModel):
    id: int
    user_id: int
    description: str
    event_datetime: datetime
    repeat_interval: EventRepeatInterval | None

    class Config:
        from_attributes = True
