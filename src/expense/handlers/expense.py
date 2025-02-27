import pytz
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from src.database import db_helper
from src.expense.exceptions import BadExpense
from src.expense.handlers.statistics import expense_template
from src.expense.schemes import ExpenseCreateScheme
from src.expense.service import (
    add_expense,
    delete_expense,
    get_all_category,
    get_top_expense,
)
from src.handlers import main_keyboard

AMOUNT, CATEGORY, DESCRIPTION, DELETE = range(4)

session = db_helper.session_factory()


async def delete_expense_start(update: Update, contex: ContextTypes.DEFAULT_TYPE):
    user_telegram_id = update.effective_user.id
    expenses = await get_top_expense(session, user_telegram_id)
    answer = "Последние 10 трат.:\n\n"
    for expense in expenses:
        answer += expense_template.format(
            expense_id=expense.id,
            expense_category=expense.category_name,
            expense_desc=expense.description if expense.description else "",
            expense_amount=expense.amount,
            expense_dt=expense.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S"),
        )
    await update.message.reply_text(answer, reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text("Введите id траты, которую хотите удалить.")
    return DELETE


async def delete_expense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expense_id = update.message.text
    if not expense_id.isdigit():
        await update.message.reply_text("Пожалуйста, введите корректный id траты.")
        return DELETE
    await delete_expense(session, expense_id)
    await update.message.reply_text(f"Расход {expense_id} успешно удалён.", reply_markup=main_keyboard)
    return ConversationHandler.END


async def add_expense_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите сумму расхода:", reply_markup=ReplyKeyboardRemove())
    return AMOUNT


async def process_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = update.message.text.replace(",", ".")
        amount = abs(float(amount))
        context.user_data["amount"] = amount
        categories = await get_all_category(session)

        category_keybord = [[category.name] for category in categories]
        await update.message.reply_text(
            "Введите категорию расхода:",
            reply_markup=ReplyKeyboardMarkup(
                category_keybord,
                resize_keyboard=True,
            ),
        )
        return CATEGORY
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректную сумму")
        return AMOUNT


async def process_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text
    context.user_data["category"] = category
    skip_mark = ReplyKeyboardMarkup(
        [["Пропустить"]],
        resize_keyboard=True,
        input_field_placeholder="Начните вводить описание...",
    )
    await update.message.reply_text("Введите описание (или пропустите):", reply_markup=skip_mark)
    return DESCRIPTION


async def process_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text if update.message.text != "Пропустить" else None
    user_data = context.user_data
    expense = ExpenseCreateScheme(
        amount=user_data["amount"],
        category_name=user_data["category"],
        description=description,
    )

    expense = await add_expense(session, expense, update)
    answer = f"Добавленны траты 🛒:\nСумма: {expense.amount}\nКатегория: {expense.category_name}"
    await update.message.reply_text(answer, reply_markup=main_keyboard)
    return ConversationHandler.END


async def add_expense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_expense = context.args
    try:
        expense = await add_expense(session, raw_expense, update)
    except BadExpense:
        answer = "Неверный формат сообщения!\nПример правильного сообщения: '100 кафе' или 'кафе 100'."
    else:
        answer = f"Добавленны траты 🛒:\nСумма: {expense.amount}\nКатегория: {expense.category_name}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
