from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from src.database import db_helper
from src.expense.service import get_statistics_by_months_count
from src.handlers import main_keyboard

MONTH_STAT, THREE_MONTHS_STAT = range(2)

session = db_helper.session_factory()


async def get_statistic_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
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
