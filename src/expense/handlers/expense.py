from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from src.database import db_helper
from src.expense.exceptions import BadExpense
from src.expense.schemes import ExpenseCreateScheme
from src.expense.service import add_expense, get_all_category
from src.handlers import main_keyboard

AMOUNT, CATEGORY, DESCRIPTION = range(3)

session = db_helper.session_factory()


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
