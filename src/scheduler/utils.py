from datetime import datetime

from dateutil.relativedelta import relativedelta

from src.reminders.schemes import EventRepeatInterval


def calculate_next_occurrence(current_date_time: datetime, repeat_interval: EventRepeatInterval):
    match repeat_interval:
        case EventRepeatInterval.DAILY:
            return current_date_time + relativedelta(days=1)
        case EventRepeatInterval.WEEKLY:
            return current_date_time + relativedelta(weeks=1)
        case EventRepeatInterval.MONTHLY:
            return current_date_time + relativedelta(months=1)
        case EventRepeatInterval.SIXMONTH:
            return current_date_time + relativedelta(months=6)
        case EventRepeatInterval.YEARLY:
            return current_date_time + relativedelta(years=1)
