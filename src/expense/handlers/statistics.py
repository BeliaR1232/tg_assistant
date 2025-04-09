from enum import Enum

import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.expense.service import get_statistics_by_months_count, get_top_expense
from src.handlers import main_keyboard


class StatisticState(Enum):
    MONTH_STAT = "month_stat"
    THREE_MONTHS_STAT = "three_nmonths_stat"
    TOP_EXPENSE = "top_expense"


expense_template = "Трата {expense_id}:\n\tКатегория: {expense_category}\n\tОписание: {expense_desc}\n\tСумма: {expense_amount}\n\tДата и время: {expense_dt}\n\n"


async def get_statistic_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выводит кнопки с вариантами статистики."""
    buttons = [
        [InlineKeyboardButton("Последние 10 трат", callback_data=StatisticState.TOP_EXPENSE.value)],
        [InlineKeyboardButton("Статистика за текущий месяц", callback_data=StatisticState.MONTH_STAT.value)],
        [InlineKeyboardButton("Статистика за три месяца", callback_data=StatisticState.THREE_MONTHS_STAT.value)],
    ]
    keyboards = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Выберите вид отчёта:", reply_markup=keyboards)


async def _generate_statistics_answer(user_telegram_id: int, months: int = 0) -> str:
    """Формирует текст статистики по категориям."""
    statistics = await get_statistics_by_months_count(user_telegram_id, months)
    resume = sum(stat.amount for stat in statistics)
    stats_text = "\n".join(f"{stat.category_name.capitalize()}: {stat.amount}" for stat in statistics)
    return f"Статистика по категориям\n\n{stats_text}\n\nИтого: {resume}"


async def get_month_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет статистику за текущий месяц."""
    await update.callback_query.answer()
    user_telegram_id = update.effective_user.id
    answer = await _generate_statistics_answer(user_telegram_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer, reply_markup=main_keyboard)


async def get_three_months_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет статистику за три месяца."""
    await update.callback_query.answer()
    user_telegram_id = update.effective_user.id
    answer = await _generate_statistics_answer(user_telegram_id, 3)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer, reply_markup=main_keyboard)


async def get_top_expense_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выводит топ-10 трат пользователя."""
    await update.callback_query.answer()
    user_telegram_id = update.effective_user.id
    statistics = await get_top_expense(user_telegram_id)

    answer = "Последние 10 трат:\n\n" + "\n".join(
        expense_template.format(
            expense_id=stat.id,
            expense_category=stat.category_name,
            expense_desc=stat.description or "",
            expense_amount=stat.amount,
            expense_dt=stat.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S"),
        )
        for stat in statistics
    )

    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer, reply_markup=main_keyboard)


def register_statistic_handler(application: Application):
    month_stat_handler = CallbackQueryHandler(get_month_stat, pattern="^" + StatisticState.MONTH_STAT.value + "$")
    three_month_stat_handler = CallbackQueryHandler(
        get_three_months_stat, pattern="^" + StatisticState.THREE_MONTHS_STAT.value + "$"
    )
    top_stat_handler = CallbackQueryHandler(get_top_expense_stat, pattern="^" + StatisticState.TOP_EXPENSE.value + "$")
    stat_handler = MessageHandler(filters.Regex("^Статистика$"), get_statistic_start)
    application.add_handler(stat_handler)
    application.add_handler(three_month_stat_handler)
    application.add_handler(month_stat_handler)
    application.add_handler(top_stat_handler)
