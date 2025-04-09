import logging

from pytz import timezone
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
)

from src.configs import settings
from src.expense.handlers.expense import (
    register_expense_handler,
)
from src.expense.handlers.statistics import (
    register_statistic_handler,
)
from src.handlers import start
from src.reminders.handlers import register_reminder_handler
from src.reminders.utils import check_events

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.bot.token).build()
    default_scheduler_config = application.job_queue.scheduler_configuration.copy()
    default_scheduler_config["timezone"] = timezone("Europe/Moscow")
    application.job_queue.scheduler.configure(**default_scheduler_config)
    register_reminder_handler(application)
    register_expense_handler(application)
    register_statistic_handler(application)
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    application.job_queue.run_repeating(callback=check_events, interval=30, first=1)
    application.run_polling()
