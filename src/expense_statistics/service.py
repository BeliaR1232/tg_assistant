from src.core.unitofwork import get_uow
from src.expense.schemes import (
    ExpenseStatisticScheme,
    ExpenseTopScheme,
)


async def get_statistics_by_months_count(user_telegram_id: int, months_count: int = 0) -> list[ExpenseStatisticScheme]:
    """Получает статистику расходов пользователя за указанное количество месяцев."""
    async with get_uow() as uow:
        expenses = await uow.expense.get_statistics_by_months_count(user_telegram_id, months_count)
    return sorted(
        (ExpenseStatisticScheme.model_validate(exp) for exp in expenses),
        key=lambda x: x.amount,
        reverse=True,
    )


async def get_top_expense(user_telegram_id: int, count: int = 10) -> list[ExpenseTopScheme]:
    """Возвращает топ-N самых крупных расходов пользователя."""
    async with get_uow() as uow:
        expenses = await uow.expense.get_top_expenses(user_telegram_id, count)
    return [ExpenseTopScheme.model_validate(stat) for stat in expenses]
