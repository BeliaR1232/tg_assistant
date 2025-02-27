import pytz
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from src.database import db_helper
from src.expense.service import get_statistics_by_months_count, get_top_expense
from src.handlers import main_keyboard

MONTH_STAT, THREE_MONTHS_STAT, TOP_EXPENSE = range(3)

session = db_helper.session_factory()


expense_template = "Трата {expense_id}:\n\tКатегория: {expense_category}\n\tОписание: {expense_desc}\n\tСумма: {expense_amount}\n\tДата и время: {expense_dt}\n\n"


async def get_statistic_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(text="Последние 10 трат", callback_data=str(TOP_EXPENSE))],
        [InlineKeyboardButton(text="Статистика за текущий месяц", callback_data=str(MONTH_STAT))],
        [InlineKeyboardButton(text="Статистика за три месяца", callback_data=str(THREE_MONTHS_STAT))],
    ]
    keyboards = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Веберите вид отчёта:", reply_markup=keyboards)


async def get_month_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_telegram_id = update.effective_user.id
    statistics = await get_statistics_by_months_count(session, user_telegram_id)
    answer = "Статистика по категориям\n\n"
    resume = 0
    for stat in statistics:
        resume += stat.amount
        answer += f"{stat.category_name.capitalize()}: {stat.amount}\n"
    answer += f"\nИтого: {resume}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer, reply_markup=main_keyboard)


async def get_top_expense_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_telegram_id = update.effective_user.id
    statistics = await get_top_expense(session, user_telegram_id)
    answer = "Последние 10 трат:\n\n"
    for stat in statistics:
        answer += expense_template.format(
            expense_id=stat.id,
            expense_category=stat.category_name,
            expense_desc=stat.description if stat.description else "",
            expense_amount=stat.amount,
            expense_dt=stat.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S"),
        )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer, reply_markup=main_keyboard)


async def get_three_months_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_telegram_id = update.effective_user.id
    statistics = await get_statistics_by_months_count(session, user_telegram_id, 3)
    answer = "Статистика по категориям\n\n"
    resume = 0
    for stat in statistics:
        resume += stat.amount
        answer += f"{stat.category_name.capitalize()}: {stat.amount}\n"
    answer += f"\nИтого: {resume}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer, reply_markup=main_keyboard)
