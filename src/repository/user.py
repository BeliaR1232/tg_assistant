from typing import Optional

from sqlalchemy import select

from src.database import User
from src.repository.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями."""

    def __init__(self, session):
        super().__init__(session, User)

    async def get_user_by_tg_id(self, telegram_id) -> Optional[User]:
        stmt = select(self.model).where(self.model.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_user_by_tg_id(self, current_user: User) -> User:
        user = await self.get_user_by_tg_id(current_user.telegram_id)
        if not user:
            user = await self.add(current_user)
        return user
