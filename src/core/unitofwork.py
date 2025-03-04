from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import db_helper
from src.repository.category import CategoryRepository
from src.repository.expense import ExpenseRepository
from src.repository.user import UserRepository


class UnitOfWork:
    """Unit of Work для управления сессией и транзакциями."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.expense = ExpenseRepository(session)
        self.user = UserRepository(session)
        self.category = CategoryRepository(session)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


@asynccontextmanager
async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    """Создаёт UoW и управляет жизненным циклом сессии."""
    async with db_helper.session_factory() as session:
        yield UnitOfWork(session)
