from datetime import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import delete, func, insert, select, text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update

from src.database import Category, Expense, User
from src.expense.schemes import (
    CategoryScheme,
    ExpenseCreateScheme,
    ExpenseScheme,
    ExpenseStatisticScheme,
    ExpenseTopScheme,
    UserScheme,
)


async def add_expense(session: AsyncSession, new_expense: ExpenseCreateScheme, update_tg: Update) -> ExpenseScheme:
    category = await get_category_by_alias(session, new_expense.category_name)
    user = await get_or_create_user_by_tg_id(session, update_tg)
    expense = await add_expense_in_db(session, new_expense, category, user)
    return expense


async def get_or_create_user_by_tg_id(session: AsyncSession, update_tg: Update) -> UserScheme:
    json_build = func.json_build_object(
        text("'id', id"),
        text("'telegram_id', telegram_id"),
        text("'chat_id', chat_id"),
        text("'name', name"),
        text("'lastname', lastname"),
        text("'is_active', is_active"),
    )
    stmt = select(json_build).where(User.telegram_id == update_tg.effective_user.id)
    result = await session.execute(stmt)
    try:
        user = result.scalar_one()
    except NoResultFound:
        stmt = (
            insert(User)
            .values(
                {
                    "telegram_id": update_tg.effective_user.id,
                    "chat_id": update_tg.effective_chat.id,
                    "name": update_tg.effective_user.first_name,
                    "lastname": update_tg.effective_user.last_name,
                }
            )
            .returning(json_build)
        )
        result = await session.execute(stmt)
        await session.commit()
        user = result.scalar_one()
    return UserScheme.model_validate(user)


async def get_category_by_alias(session: AsyncSession, category_alias: str) -> CategoryScheme:
    stmt = select(
        func.json_build_object(
            text("'id', id"),
            text("'name', name"),
            text("'is_base_expense', is_base_expense"),
            text("'codename', codename"),
        ),
    ).where(Category.aliases.has_key(category_alias))
    result = await session.execute(stmt)
    try:
        category = result.scalar_one()
    except NoResultFound:
        stmt = select(
            func.json_build_object(
                text("'id', id"),
                text("'name', name"),
                text("'is_base_expense', is_base_expense"),
                text("'codename', codename"),
            ),
        ).where(Category.aliases.has_key("прочее"))
        result = await session.execute(stmt)
        category = result.scalar_one()
    return CategoryScheme.model_validate(category)


async def add_expense_in_db(
    session: AsyncSession,
    new_expense: ExpenseCreateScheme,
    category: CategoryScheme,
    user: UserScheme,
) -> ExpenseScheme:
    stmt = (
        insert(Expense)
        .values(
            {
                "amount": new_expense.amount,
                "description": new_expense.description,
                "category_id": category.id,
                "user_id": user.id,
            }
        )
        .returning(
            func.json_build_object(
                text("'id', id"),
                text("'amount', amount"),
                text("'user_id', user_id"),
                text("'category_id', category_id"),
            )
        )
    )
    result = await session.execute(stmt)
    await session.commit()
    expense = result.scalar_one()
    expense["category_name"] = category.name
    return ExpenseScheme.model_validate(expense)


async def get_all_category(session: AsyncSession) -> list[CategoryScheme]:
    stmt = select(
        func.json_build_object(
            text("'id', id"),
            text("'name', name"),
            text("'is_base_expense', is_base_expense"),
            text("'codename', codename"),
        ),
    ).select_from(Category)
    result = await session.execute(stmt)
    categories = result.scalars().all()
    return [CategoryScheme.model_validate(category) for category in categories]


async def get_statistics_by_months_count(
    session: AsyncSession,
    user_telegram_id: int,
    months_count: int = 0,
) -> list[ExpenseStatisticScheme]:
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
        .join(User, Expense.user_id == User.id)
        .join(Category, Expense.category_id == Category.id)
        .where(User.telegram_id == user_telegram_id)
        .where(Expense.created_at.between(date_range[0], date_range[1]))
        .group_by(Category.name)
    )
    result = await session.execute(stmt)
    expenses = result.scalars().all()
    expense = [ExpenseStatisticScheme.model_validate(stat) for stat in expenses]
    return list(sorted(expense, key=lambda x: x.amount, reverse=True))


async def get_top_expense(
    session: AsyncSession,
    user_telegram_id: int,
    count: int = 10,
) -> list[ExpenseTopScheme]:
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
        .join(User, Expense.user_id == User.id)
        .join(Category, Expense.category_id == Category.id)
        .where(User.telegram_id == user_telegram_id)
        .order_by(Expense.id.desc())
        .limit(count)
    )
    result = await session.execute(stmt)
    expenses = result.scalars().all()
    return [ExpenseTopScheme.model_validate(stat) for stat in expenses]


async def delete_expense(session: AsyncSession, expense_id: str):
    stmt = delete(Expense).where(Expense.id == int(expense_id))
    await session.execute(stmt)
    await session.commit()
