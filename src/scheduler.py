import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dateutil.relativedelta import relativedelta
from pytz import timezone
from telegram import Bot

from src.configs import settings
from src.core.unitofwork import get_uow
from src.reminders.schemes import EventRepeatInterval

sched = AsyncIOScheduler(timezone=timezone("Europe/Moscow"))

logger = logging.getLogger(__name__)

bot = Bot(token=settings.bot.token)


def calculate_next_occurrence(current_date_time: datetime, repeat_interval: EventRepeatInterval):
    match repeat_interval:
        case EventRepeatInterval.DAILY:
            return current_date_time + relativedelta(days=1)
        case EventRepeatInterval.WEEKLY:
            return current_date_time + relativedelta(weeks=1)
        case EventRepeatInterval.MONTHLY:
            return current_date_time + relativedelta(months=1)
        case EventRepeatInterval.YEARLY:
            return current_date_time + relativedelta(years=1)


async def send_reminder(user_tg_id: int, description: str):
    await bot.send_message(user_tg_id, text=f"Напоминание: {description}")


async def check_events():
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
                    sched.add_job(
                        send_reminder,
                        "date",
                        kwargs={
                            "user_tg_id": user.telegram_id,
                            "description": event.description,
                        },
                        run_date=time_to_send,
                    )
                if event.repeat_interval is None:
                    await uow.event.delete(event.id)
                else:
                    next_occurrence = calculate_next_occurrence(event.event_datetime, event.repeat_interval)
                    await uow.event.update(event.id, {"event_datetime": next_occurrence})

            await uow.commit()
    except Exception as e:
        logger.error(f"Ошибка при проверке событий: {e}")


async def test():
    print("test")
    asyncio.sleep(2)
    print("test sleep")


async def main():
    try:
        sched.add_job(test, trigger="interval", seconds=30)
        sched.start()
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except Exception as e:
        logger.error(e)
