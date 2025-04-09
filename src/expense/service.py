from src.core.unitofwork import get_uow
from src.database import Expense
from src.database.models import User
from src.expense.schemes import (
    CategoryScheme,
    ExpenseCreateScheme,
    ExpenseScheme,
    ExpenseStatisticScheme,
    ExpenseTopScheme,
)


async def add_expense(
    new_expense: ExpenseCreateScheme,
    user_telegram_id: str,
    chat_id: str,
    firstname: str,
    lastname: str | None,
) -> ExpenseScheme:
    """Добавляет новый расход в базу данных."""
    async with get_uow() as uow:
        category = await uow.category.get_category_by_alias(new_expense.category_name)
        user = User(
            telegram_id=user_telegram_id,
            chat_id=chat_id,
            name=firstname,
            lastname=lastname,
        )
        user = await uow.user.get_or_create_user_by_tg_id(user)
        await uow.commit()
        expense_db = Expense(
            amount=new_expense.amount,
            description=new_expense.description,
            category_id=category.id,
            user_id=user.id,
        )
        expense = await uow.expense.add(expense_db)
        await uow.commit()

    return ExpenseScheme(
        id=expense.id,
        category_name=category.name,
        amount=expense.amount,
        user_id=user.id,
        category_id=category.id,
    )


async def get_all_category() -> list[CategoryScheme]:
    """Получает список всех категорий."""
    async with get_uow() as uow:
        categories = await uow.category.get_all()
    return [CategoryScheme.model_validate(category) for category in categories]


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


async def delete_expense(expense_id: int):
    """Удаляет расход по ID."""
    async with get_uow() as uow:
        await uow.expense.delete(expense_id)
        await uow.commit()
