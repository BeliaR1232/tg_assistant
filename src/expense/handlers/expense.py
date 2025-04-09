from enum import Enum

import pytz
from sqlalchemy.exc import SQLAlchemyError
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.expense.handlers.statistics import expense_template
from src.expense.schemes import ExpenseCreateScheme
from src.expense.service import (
    add_expense,
    delete_expense,
    get_all_category,
    get_top_expense,
)
from src.handlers import cancel, main_keyboard


class ExpenseState(Enum):
    AMOUNT = "amount"
    CATEGORY = "category"
    DESCRIPTION = "description"
    DELETE = "delete"


async def delete_expense_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Начало процесса удаления расходов."""
    user_telegram_id = update.effective_user.id
    expenses = await get_top_expense(user_telegram_id)

    if not expenses:
        await update.message.reply_text("У вас пока нет расходов.")
        return ConversationHandler.END

    answer = "Последние 10 трат:\n\n" + "\n".join(
        expense_template.format(
            expense_id=expense.id,
            expense_category=expense.category_name,
            expense_desc=expense.description or "",
            expense_amount=expense.amount,
            expense_dt=expense.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S"),
        )
        for expense in expenses
    )

    await update.message.reply_text(answer, reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text("Введите ID траты, которую хотите удалить.")
    return ExpenseState.DELETE


async def delete_expense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик удаления расхода."""
    expense_id = update.message.text
    if not expense_id or not expense_id.isdigit():
        await update.message.reply_text("Пожалуйста, введите корректный ID траты.")
        return ExpenseState.DELETE

    try:
        await delete_expense(int(expense_id))
        await update.message.reply_text(f"Расход {expense_id} успешно удалён.", reply_markup=main_keyboard)
    except SQLAlchemyError:
        await update.message.reply_text("Ошибка удаления расхода. Попробуйте снова.")
        return ExpenseState.DELETE

    return ConversationHandler.END


async def add_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запрашивает сумму расхода."""
    await update.message.reply_text("Введите сумму расхода:", reply_markup=ReplyKeyboardRemove())
    return ExpenseState.AMOUNT


async def process_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает введённую сумму расхода."""
    try:
        amount = abs(float(update.message.text.replace(",", ".")))
        context.user_data["amount"] = amount

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректную сумму.")
        return ExpenseState.AMOUNT

    categories = await get_all_category()

    category_keyboard = [[category.name] for category in categories]
    await update.message.reply_text(
        "Введите категорию расхода:",
        reply_markup=ReplyKeyboardMarkup(category_keyboard, resize_keyboard=True),
    )
    return ExpenseState.CATEGORY


async def process_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает введённую категорию."""
    context.user_data["category"] = update.message.text
    await update.message.reply_text(
        "Введите описание (или пропустите):",
        reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True),
    )
    return ExpenseState.DESCRIPTION


async def process_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает описание и сохраняет расход в базе данных."""
    description = update.message.text if update.message.text != "Пропустить" else None
    user_data = context.user_data

    expense = ExpenseCreateScheme(
        amount=user_data["amount"],
        category_name=user_data["category"],
        description=description,
    )

    try:
        expense = await add_expense(
            expense,
            update.effective_user.id,
            update.effective_message.id,
            update.effective_user.first_name,
            update.effective_user.last_name,
        )
        await update.message.reply_text(
            f"Добавлены траты 🛒:\nСумма: {expense.amount}\nКатегория: {expense.category_name}",
            reply_markup=main_keyboard,
        )
    except SQLAlchemyError:
        await update.message.reply_text("Ошибка добавления расхода. Попробуйте снова.")
        return ExpenseState.AMOUNT

    return ConversationHandler.END


async def get_finance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выводит кнопки с вариантами статистики."""
    finance_keyboard = ReplyKeyboardMarkup(
        [["Статистика"], ["Добавить расход"], ["Удалить расход"]],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие:",
    )
    await update.message.reply_text("Выберите вид отчёта:", reply_markup=finance_keyboard)


def register_expense_handler(application: Application):
    finance_handler = MessageHandler(filters.Regex("^Финансы$"), get_finance_start)

    add_expense_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Добавить расход$"), add_expense_start)],
        states={
            ExpenseState.AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_amount)],
            ExpenseState.CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_category)],
            ExpenseState.DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    delete_expense_handler_main = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Удалить расход$"), delete_expense_start)],
        states={
            ExpenseState.DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_expense_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(finance_handler)
    application.add_handler(add_expense_handler)
    application.add_handler(delete_expense_handler_main)
