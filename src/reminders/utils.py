import logging
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from telegram.ext import ContextTypes

from src.core.unitofwork import get_uow
from src.reminders.schemes import EventRepeatInterval, EventScheme

logger = logging.getLogger(__name__)


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


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(job.user_id, text=f"Напоминание: {job.data}")


async def check_events(context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info("Получение напоминаний.")
        now = datetime.now()
        period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        async with get_uow() as uow:
            events = await uow.event.get_events_by_datetime(period_start, period_end)
            logger.info(f"Полученно {len(events)} напоминаний.")
            for event in events:
                user = await uow.user.get_by_id(event.user_id)
                for count in range(event.message_count):
                    time_to_send = event.event_datetime + timedelta(minutes=count + 1)
                    context.job_queue.run_once(
                        send_reminder,
                        time_to_send,
                        user_id=user.telegram_id,
                        name=f"{event.id}_{count}",
                        data=event.description,
                    )
                if event.repeat_interval is None:
                    await uow.event.delete(event.id)
                else:
                    next_occurrence = calculate_next_occurrence(event.event_datetime, event.repeat_interval)
                    await uow.event.update(event.id, {"event_datetime": next_occurrence})

            await uow.commit()
    except Exception as e:
        logger.error(f"Ошибка при проверке событий: {e}")


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
