from datetime import datetime
from typing import Sequence

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, select, text

from src.database import Category, Expense, User
from src.repository.base import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    """Репозиторий для работы с расходами."""

    def __init__(self, session):
        super().__init__(session, Expense)

    async def get_statistics_by_months_count(
        self,
        user_telegram_id: int,
        months_count: int = 0,
    ) -> Sequence[Expense]:
        """Получает статистику расходов за указанное количество месяцев."""
        date_range = (
            datetime.now() + relativedelta(hour=0, minute=0, second=1, months=-months_count, day=1),
            datetime.now() + relativedelta(hour=23, minute=59, second=59, day=31),
        )

        stmt = (
            select(
                func.json_build_object(
                    text("'amount', sum(expense.amount)"),
                    text("'category_name', category.name"),
                )
            )
            .select_from(Expense)
            .join(Category)
            .join(User)
            .where(User.telegram_id == user_telegram_id)
            .where(Expense.created_at.between(date_range[0], date_range[1]))
            .group_by(Category.name)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_top_expenses(self, user_telegram_id: int, count: int = 10) -> Sequence[Expense]:
        """Получает топ-N расходов пользователя."""
        stmt = (
            select(
                func.json_build_object(
                    text("'id', expense.id"),
                    text("'amount', expense.amount"),
                    text("'category_name', category.name"),
                    text("'created_at', expense.created_at"),
                    text("'description', expense.description"),
                )
            )
            .select_from(Expense)
            .join(Category, Expense.category_id == Category.id)
            .join(User, Expense.user_id == User.id)
            .where(User.telegram_id == user_telegram_id)
            .order_by(Expense.id.desc())
            .limit(count)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()
