import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.configs import settings
from src.expense.handlers import (
    AMOUNT,
    CATEGORY,
    DESCRIPTION,
    add_expense_start,
    process_amount,
    process_category,
    process_description,
)
from src.handlers import cancel, start

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.bot.token).build()

    start_handler = CommandHandler("start", start)
    exit_handler = CommandHandler("cancel", cancel)
    expense_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Добавить расход$"), add_expense_start)],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_amount)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_category)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(start_handler)
    application.add_handler(exit_handler)
    application.add_handler(expense_handler)

    application.run_polling()
