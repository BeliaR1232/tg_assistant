from datetime import datetime
from typing import Sequence

from sqlalchemy.future import select

from src.database.models import Event, User
from src.repository.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self, session):
        super().__init__(session, Event)

    async def get_events_by_datetime(self, start_datetime: datetime, end_datetime: datetime) -> Sequence[Event]:
        query = select(Event).where(Event.event_datetime.between(start_datetime, end_datetime))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_by_user_tg(self, user_tg_id: int) -> Sequence[Event]:
        """Получение списка событий для юзера по telegram_id."""
        query = select(Event).join(User).where(User.telegram_id == user_tg_id)
        result = await self.session.execute(query)
        return result.scalars().all()
