import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)

from src.configs import settings
from src.expense.handlers import register_expense_handler
from src.expense_statistics.handlers import register_statistic_handler
from src.handlers import start
from src.reminders.handlers import register_reminder_handler

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.bot.token).build()
    register_reminder_handler(application)
    register_expense_handler(application)
    register_statistic_handler(application)
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    application.run_polling()
