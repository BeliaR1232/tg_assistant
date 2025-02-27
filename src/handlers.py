from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from src.database import db_helper
from src.expense.service import get_or_create_user_by_tg_id

main_keyboard = ReplyKeyboardMarkup(
    [["Добавить расход"], ["Удалить расход"], ["Статистика"]],
    resize_keyboard=True,
    input_field_placeholder="Выбери действие:",
)

session = db_helper.session_factory()


async def start(update: Update, contex: ContextTypes.DEFAULT_TYPE):
    await get_or_create_user_by_tg_id(session, update)
    answer = f"Привет, {update.effective_user.first_name}\nЯ бот-помощник, выбери действие."
    await update.message.reply_text(answer, reply_markup=main_keyboard)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено", reply_markup=main_keyboard)
    return ConversationHandler.END
