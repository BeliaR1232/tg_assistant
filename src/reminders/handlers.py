import logging
from enum import Enum

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.handlers import cancel, main_keyboard
from src.reminders import services as event_service
from src.reminders.schemes import EventCreateScheme, EventRepeatInterval
from src.reminders.utils import format_event_list

logger = logging.getLogger(__name__)


class EventDialogStates(Enum):
    SELECT_ACTION = "select_action"
    ADD_DESCRIPTION = "add_description"
    ADD_EVENT_DATETIME = "add_event_datetime"
    ADD_REPEAT_INTERVAL = "add_repeat_interval"
    ADD_MESSAGE_COUNT = "add_message_count"
    CONFIRM_EVENT = "confirm_event"
    EDIT_EVENT = "edit_event"
    DELETE_EVENT = "delete_event"
    LIST_EVENTS = "list_events"
    EDIT_NAME = "edit_name"
    EDIT_EVENT_DATETIME = "edit_event_datetime"
    EDIT_REPEAT_INTERVAL = "edit_repeat_interval"
    CONFIRM_EDIT = " confirm_edit"


async def add_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите описание события:", reply_markup=ReplyKeyboardRemove())
    return EventDialogStates.ADD_DESCRIPTION


async def add_event_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text
    await update.message.reply_text("Введите дату и время напоминания (формат YYYY-MM-DD HH:MM):")
    return EventDialogStates.ADD_EVENT_DATETIME


async def add_event_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_time_str = update.message.text
    if not event_service.validate_date_time(date_time_str):
        await update.message.reply_text(
            "Неверный формат даты или времени! Пожалуйста, повторите ввод (формат YYYY-MM-DD HH:MM):"
        )
        return EventDialogStates.ADD_EVENT_DATETIME

    context.user_data["event_datetime"] = date_time_str
    repeat_interval_keyboard = [[interval.value] for interval in list(EventRepeatInterval)]
    repeat_interval_keyboard.extend([["Пропустить"]])
    await update.message.reply_text(
        "Введите интервал повторения:",
        reply_markup=ReplyKeyboardMarkup(repeat_interval_keyboard, resize_keyboard=True),
    )
    return EventDialogStates.ADD_REPEAT_INTERVAL


async def add_event_repeat_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repeat_interval = update.message.text.lower() if update.message.text != "Пропустить" else None
    context.user_data["repeat_interval"] = repeat_interval
    await update.message.reply_text(
        "Введите количество сообщений(число больше 0) для напоминания(по умолчанию будет 3 напоминания.):",
        reply_markup=ReplyKeyboardRemove(),
    )
    return EventDialogStates.ADD_MESSAGE_COUNT


async def add_event_message_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_count: str = update.message.text or "3"
    if not message_count.isdigit():
        await update.message.reply_text("Некорректное количество напоминаний, введите число больше 0:")
        return EventDialogStates.ADD_MESSAGE_COUNT
    context.user_data["message_count"] = int(message_count)
    await confirm_event(update, context)
    return EventDialogStates.CONFIRM_EVENT


async def confirm_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        description = context.user_data.get("description")
        date_time = context.user_data.get("event_datetime")
        repeat_interval = context.user_data.get("repeat_interval")
        message_count = context.user_data.get("message_count")

        message = f"Событие:\n🗓️ Описание: {description}\n⏰ Дата/время: {date_time}\n🔄 Интервал: {repeat_interval or 'Однократное'}\n🔢 Количество сообщений: {message_count}"
        await update.message.reply_text(
            f"{message}\nПодтвердите добавление события (да/нет):", reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(f"Ошибка при подтверждении события: {e}")
        await update.message.reply_text(
            "Произошла ошибка при подтверждении события. Попробуйте снова. ❌",
            reply_markup=main_keyboard,
        )
        return ConversationHandler.END


async def confirm_event_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        confirmation = update.message.text.lower()
        if confirmation != "да":
            await update.message.reply_text("Добавление события отменено. ❌")
            return ConversationHandler.END
        event = EventCreateScheme(
            description=context.user_data.get("description"),
            event_datetime=context.user_data.get("event_datetime"),
            repeat_interval=context.user_data.get("repeat_interval"),
            message_count=context.user_data.get("message_count"),
        )

        result_event = await event_service.add_event_by_tg(
            event,
            update.effective_user.id,
            update.effective_chat.id,
            update.effective_user.first_name,
            update.effective_user.last_name,
        )
        if result_event:
            await update.message.reply_text(
                f"Событие успешно добавлено! ✅\n📅 {result_event.description}\n⏰ {result_event.event_datetime}",
                reply_markup=main_keyboard,
            )
        else:
            await update.message.reply_text("Произошла ошибка при добавлении события. Попробуйте снова. ❌")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка при добавлении события: {e}")
        await update.message.reply_text(
            "Произошла ошибка при добавлении события. Попробуйте снова. ❌",
            reply_markup=main_keyboard,
        )
        return ConversationHandler.END


async def get_list_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        events = await event_service.get_all_events(update.effective_user.id)
        if events:
            message = format_event_list(events)
        else:
            message = "У вас нет запланированных событий. 📋"
        await update.message.reply_text(
            text=message,
            reply_markup=main_keyboard,
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка при получении списка событий: {e}")
        await update.message.reply_text("Произошла ошибка при получении списка событий. Попробуйте позже. ❌")
        return ConversationHandler.END


async def delete_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        events = await event_service.get_all_events(update.effective_user.id)
        if events:
            message = format_event_list(events)
        else:
            message = "У вас нет запланированных событий. 📋"
            await update.message.reply_text(message, reply_markup=main_keyboard)
            return ConversationHandler.END
        await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text("Введите id событие для удаления:")
        return EventDialogStates.DELETE_EVENT
    except Exception as e:
        logger.error(f"Ошибка при старте удаления события: {e}")
        await update.message.reply_text("Произошла ошибка при удалении события. Попробуйте позже. ❌")
        return ConversationHandler.END


async def delete_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        event_id = update.message.text
        if not event_id or not event_id.isdigit():
            await update.message.reply_text("Пожалуйста, введите корректный ID напоминания.")
            return EventDialogStates.DELETE_EVENT
        await event_service.delete_event(int(event_id), update.effective_user.id)
        await update.message.reply_text(f"Событие с ID={event_id} успешно удалено. ✅")
    except Exception as e:
        logger.error(f"Ошибка при удалении события: {e}")
        await update.message.reply_text("Произошла ошибка при удалении события. Попробуйте позже. ❌")
    return ConversationHandler.END


async def edit_event_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        events = await event_service.get_all_events(update.effective_user.id)
        if events:
            message = format_event_list(events)
        else:
            message = "У вас нет запланированных событий. 📋"
            await update.message.reply_text(message, reply_markup=main_keyboard)
            return ConversationHandler.END
        await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text("Введите id события для редактирования:")
        return EventDialogStates.EDIT_EVENT
    except Exception as e:
        logger.error(f"Ошибка при старте редактирования события: {e}")
        await update.message.reply_text("Произошла ошибка при редактировании события. Попробуйте позже. ❌")
        return ConversationHandler.END


async def choice_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        event_id = update.message.text
        if not event_id or not event_id.isdigit():
            await update.message.reply_text("Пожалуйста, введите корректный ID напоминания.")
            return EventDialogStates.EDIT_EVENT

        context.user_data["event_id"] = event_id
        await update.message.reply_text("Введите новое описание события:")
        return EventDialogStates.EDIT_NAME
    except Exception as e:
        logger.error(f"Ошибка при выборе события для редактирования: {e}")
        await update.message.reply_text("Произошла ошибка при выборе события для редактирования. Попробуйте позже. ❌")
        return ConversationHandler.END


async def edit_event_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["edit_description"] = update.message.text
    await update.message.reply_text("Введите новую дату и время события (формат YYYY-MM-DD HH:MM):")
    return EventDialogStates.EDIT_EVENT_DATETIME


async def edit_event_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_time_str = update.message.text
    if not event_service.validate_date_time(date_time_str):
        await update.message.reply_text(
            "Неверный формат даты или времени! Пожалуйста, повторите ввод (формат YYYY-MM-DD HH:MM):"
        )
        return EventDialogStates.EDIT_EVENT_DATETIME

    context.user_data["edit_datetime"] = date_time_str
    repeat_interval_keyboard = [[interval.value] for interval in list(EventRepeatInterval)]
    repeat_interval_keyboard.extend([["Пропустить"]])
    await update.message.reply_text(
        "Введите интервал повторения:",
        reply_markup=ReplyKeyboardMarkup(repeat_interval_keyboard, resize_keyboard=True),
    )
    return EventDialogStates.EDIT_REPEAT_INTERVAL


async def edit_event_repeat_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repeat_interval = update.message.text.lower()
    context.user_data["edit_repeat_interval"] = repeat_interval if repeat_interval != "пропустить" else None
    await confirm_edit(update, context)
    return EventDialogStates.CONFIRM_EDIT


async def confirm_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        description = context.user_data.get("edit_description")
        event_datetime = context.user_data.get("edit_datetime")
        repeat_interval = context.user_data.get("edit_repeat_interval")

        message = f"Событие:\n📅 Название: {description}\n⏰ Дата/время: {event_datetime}\n🔄 Интервал: {repeat_interval or 'Однократное'}"
        await update.message.reply_text(f"{message}\nПодтвердите изменение события (да/нет):")
    except Exception as e:
        logger.error(f"Ошибка при подтверждении редактирования события: {e}")
        await update.message.reply_text(
            "Произошла ошибка при подтверждении редактирования события. Попробуйте снова. ❌",
            reply_markup=main_keyboard,
        )
        return ConversationHandler.END


async def confirm_edit_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        confirmation = update.message.text.lower()
        if confirmation != "да":
            await update.message.reply_text("Редактирование события отменено. ❌", reply_markup=main_keyboard)
            return ConversationHandler.END

        description = context.user_data.get("edit_description")
        event_datetime = context.user_data.get("edit_datetime")
        repeat_interval = context.user_data.get("edit_repeat_interval")
        event_id = int(context.user_data.get("event_id"))

        result = await event_service.update_event(event_id, description, event_datetime, repeat_interval)
        if result:
            await update.message.reply_text(
                f"Событие с ID={event_id} успешно обновлено! ✅", reply_markup=main_keyboard
            )
        else:
            await update.message.reply_text(f"Событие с ID={event_id} не обновлено. ❌", reply_markup=main_keyboard)
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка при обновлении события: {e}")
        await update.message.reply_text("Произошла ошибка при обновлении события. Попробуйте снова. ❌")
        return ConversationHandler.END


async def start_reminders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    finance_keyboard = ReplyKeyboardMarkup(
        [["Добавить напоминание"], ["Посмотреть напоминания"], ["Удалить напоминание"], ["Редактировать напоминание"]],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие:",
    )
    await update.message.reply_text("Выбери действие:", reply_markup=finance_keyboard)


def register_reminder_handler(application: Application):
    start_handler = MessageHandler(filters.Regex("^Напоминания$"), start_reminders_handler)

    add_event_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Добавить напоминание$"), add_event_start)],
        states={
            EventDialogStates.ADD_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_event_description)],
            EventDialogStates.ADD_MESSAGE_COUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_event_message_count)
            ],
            EventDialogStates.ADD_EVENT_DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_event_datetime)],
            EventDialogStates.ADD_REPEAT_INTERVAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_event_repeat_interval)
            ],
            EventDialogStates.CONFIRM_EVENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_event_submission)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    edit_event_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Редактировать напоминание$"), edit_event_start)],
        states={
            EventDialogStates.EDIT_EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choice_event)],
            EventDialogStates.EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_event_description)],
            EventDialogStates.EDIT_EVENT_DATETIME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_event_datetime)
            ],
            EventDialogStates.EDIT_REPEAT_INTERVAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_event_repeat_interval)
            ],
            EventDialogStates.CONFIRM_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_edit_submission)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    delete_event_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Удалить напоминание$"), delete_event_start)],
        states={
            EventDialogStates.DELETE_EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_event)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    list_events_handler = MessageHandler(filters.Regex("^Посмотреть напоминания$"), get_list_events)
    application.add_handler(start_handler)
    application.add_handler(add_event_handler)
    application.add_handler(edit_event_handler)
    application.add_handler(delete_event_handler)
    application.add_handler(list_events_handler)
