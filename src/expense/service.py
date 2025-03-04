from telegram import Update

from src.core.unitofwork import get_uow
from src.database import Expense, User
from src.expense.schemes import (
    CategoryScheme,
    ExpenseCreateScheme,
    ExpenseScheme,
    ExpenseStatisticScheme,
    ExpenseTopScheme,
)


async def add_expense(
    new_expense: ExpenseCreateScheme,
    update_tg: Update,
) -> ExpenseScheme:
    async with get_uow() as uow:
        category = await uow.category.get_category_by_alias(new_expense.category_name)
        current_user = User(
            telegram_id=update_tg.effective_user.id,
            chat_id=update_tg.effective_chat.id,
            name=update_tg.effective_user.first_name,
            lastname=update_tg.effective_user.last_name,
        )
        user = await uow.user.get_or_create_user_by_tg_id(current_user)
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
    async with get_uow() as uow:
        categories = await uow.category.get_all()
    return [CategoryScheme.model_validate(category) for category in categories]


async def get_statistics_by_months_count(
    user_telegram_id: int,
    months_count: int = 0,
) -> list[ExpenseStatisticScheme]:
    async with get_uow() as uow:
        expenses = await uow.expense.get_statistics_by_months_count(user_telegram_id, months_count)
    return sorted(
        [ExpenseStatisticScheme.model_validate(exp) for exp in expenses], key=lambda x: x.amount, reverse=True
    )


async def get_top_expense(
    user_telegram_id: int,
    count: int = 10,
) -> list[ExpenseTopScheme]:
    async with get_uow() as uow:
        expenses = await uow.expense.get_top_expenses(user_telegram_id, count)
    return [ExpenseTopScheme.model_validate(stat) for stat in expenses]


async def delete_expense(
    expense_id: int,
):
    async with get_uow() as uow:
        await uow.expense.delete(int(expense_id))
        await uow.commit()