from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

main_keyboard = ReplyKeyboardMarkup(
    [["Финансы"], ["Напоминания"]],
    resize_keyboard=True,
    input_field_placeholder="Выбери категорию:",
)


async def start(update: Update, contex: ContextTypes.DEFAULT_TYPE):
    answer = f"Привет, {update.effective_user.first_name}\nЯ бот-помощник, выбери действие."
    await update.message.reply_text(answer, reply_markup=main_keyboard)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено", reply_markup=main_keyboard)
    return ConversationHandler.END
