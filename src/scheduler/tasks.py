import logging
from datetime import datetime, timedelta
from typing import Any

from arq.connections import ArqRedis
from telegram import Bot

from src.core.unitofwork import get_uow
from src.scheduler.utils import calculate_next_occurrence

logger = logging.getLogger(__name__)


async def send_reminder(context: dict[str, Any], user_tg_id: int, event_id: int, message: str):
    bot: Bot = context["bot"]
    await bot.send_message(user_tg_id, text=f"Напоминание: {message}")
    logger.info(f"Напоминание id:{event_id} отправленно пользователю(telegram_id: {user_tg_id})")


async def check_events(context: dict[str, Any]):
    try:
        logger.info("Получение напоминаний.")
        now = datetime.now()
        period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        redis: ArqRedis = context["redis"]

        async with get_uow() as uow:
            events = await uow.event.get_events_by_datetime(period_start, period_end)
            logger.info(f"Полученно {len(events)} напоминаний.")
            for event in events:
                user = await uow.user.get_by_id(event.user_id)
                for count in range(event.message_count):
                    time_to_send = (
                        event.event_datetime + timedelta(hours=count, minutes=30)
                        if count != 0
                        else event.event_datetime
                    )
                    await redis.enqueue_job(
                        "send_reminder",
                        user.telegram_id,
                        event.id,
                        event.description,
                        _defer_until=time_to_send,
                    )

                    logger.info(
                        f"Напоминание id: {event.id} поставленна в очередь на отправку {time_to_send.date()} в {time_to_send.time()}."
                    )
                if event.repeat_interval is None:
                    await uow.event.delete(event.id)
                else:
                    next_occurrence = calculate_next_occurrence(event.event_datetime, event.repeat_interval)
                    await uow.event.update(event.id, {"event_datetime": next_occurrence})

            await uow.commit()

    except Exception as e:
        logger.error(f"Ошибка при проверке событий: {e}")
