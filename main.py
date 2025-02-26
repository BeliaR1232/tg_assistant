import logging

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.configs import settings
from src.expense.handlers.expense import (
    AMOUNT,
    CATEGORY,
    DESCRIPTION,
    add_expense_start,
    process_amount,
    process_category,
    process_description,
)
from src.expense.handlers.statistics import (
    MONTH_STAT,
    THREE_MONTHS_STAT,
    TOP_EXPENSE,
    get_month_stat,
    get_statistic_start,
    get_top_expense_stat,
)
from src.handlers import cancel, start

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.bot.token).build()

    start_handler = CommandHandler("start", start)
    stat_handler = MessageHandler(filters.Regex("^Статистика$"), get_statistic_start)
    expense_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Добавить расход$"), add_expense_start)],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_amount)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_category)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    month_stat = CallbackQueryHandler(get_month_stat, pattern="^" + str(MONTH_STAT) + "$")
    three_month_stat = CallbackQueryHandler(get_month_stat, pattern="^" + str(THREE_MONTHS_STAT) + "$")
    top_stat = CallbackQueryHandler(get_top_expense_stat, pattern="^" + str(TOP_EXPENSE) + "$")
    application.add_handler(start_handler)
    application.add_handler(stat_handler)
    application.add_handler(three_month_stat)
    application.add_handler(month_stat)
    application.add_handler(top_stat)
    application.add_handler(expense_handler)

    application.run_polling()
