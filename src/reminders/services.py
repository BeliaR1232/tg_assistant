import logging

from src.core.unitofwork import get_uow
from src.database.models import Event, User
from src.reminders.schemes import EventCreateScheme, EventRepeatInterval, EventScheme
from src.reminders.utils import parse_date_time

logger = logging.getLogger(__name__)


async def add_event_by_tg(
    event: EventCreateScheme,
    user_telegram_id: str,
    chat_id: str,
    firstname: str,
    lastname: str | None,
) -> EventScheme:
    async with get_uow() as uow:
        user = User(
            telegram_id=user_telegram_id,
            chat_id=chat_id,
            name=firstname,
            lastname=lastname,
        )
        user = await uow.user.get_or_create_user_by_tg_id(user)
        await uow.commit()
        new_event = Event(
            user_id=user.id,
            description=event.description,
            event_datetime=event.event_datetime,
            repeat_interval=event.repeat_interval,
            message_count=event.message_count,
        )
        new_event = await uow.event.add(new_event)
        await uow.commit()
        return EventScheme.model_validate(new_event)


async def get_all_events(user_tg_id: int) -> tuple[EventScheme, ...]:
    try:
        async with get_uow() as uow:
            events = await uow.event.get_all_by_user_tg(user_tg_id)
            return tuple(EventScheme.model_validate(event) for event in events)
    except Exception as e:
        logger.error(f"Ошибка при получении событий: {e}")
        return tuple()


async def delete_event(event_id: int, user_tg_id: int) -> bool:
    async with get_uow() as uow:
        user = await uow.user.get_user_by_tg_id(user_tg_id)
        event = await uow.event.get_by_id(event_id)
        if user and event and event.user_id == user.id:
            await uow.session.delete(event)
            await uow.commit()
            return True
        return False


async def update_event(
    event_id: str,
    description: str,
    date_time_str: str,
    repeat_interval: EventRepeatInterval | None,
) -> EventScheme | None:
    date_time = parse_date_time(date_time_str)
    if not date_time:
        return None

    async with get_uow() as uow:
        result = await uow.event.update(
            int(event_id),
            EventCreateScheme(
                description=description,
                event_datetime=date_time_str,
                repeat_interval=repeat_interval,
            ).dict(exclude_unset=True),
        )
        await uow.commit()
        return EventScheme.model_validate(result)


def validate_date_time(date_time_str):
    return parse_date_time(date_time_str) is not None
