from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models import BaseDbModel

T = TypeVar("T", bound=BaseDbModel)


class BaseRepository(Generic[T]):
    """Абстрактный репозиторий для CRUD-операций."""

    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, obj_id: int) -> Optional[T]:
        """Получает объект по ID."""
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> Sequence[T]:
        """Получает все объекты модели."""
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add(self, obj: T) -> T:
        """Добавляет новый объект."""
        self.session.add(obj)
        return obj

    async def delete(self, obj_id: int):
        """Удаляет объект по ID."""
        stmt = delete(self.model).where(self.model.id == obj_id)
        await self.session.execute(stmt)

    async def update(self, obj_id: int, update_fields: dict[str, Any]):
        stmt = update(self.model).where(self.model.id == obj_id).values(**update_fields).returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()
