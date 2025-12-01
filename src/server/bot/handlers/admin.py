from django.conf import settings
from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from server.bot.cache.manager import RedisCacheManager
from server.bot.handlers.helpers import get_admin_menu_data
from server.bot.utils import messages
from server.bot.utils.error_handler import ErrorHandler
from server.bot.utils.keyboards import KeyboardConstructor


@ErrorHandler.create()
def admin_with_callback(callback: CallbackQuery, bot: TeleBot):
    """Обработка callback'а admin"""
    telegram_id = callback.message.chat.id
    RedisCacheManager.set(key=telegram_id, file_id=None)

    if telegram_id not in settings.ADMIN_IDS:
        return bot.send_message(
            chat_id=telegram_id,
            text=messages.NO_ADMIN_RIGHTS,
        )

    data = get_admin_menu_data()
    keyboard = KeyboardConstructor().create_inline_keyboard(data)
    return bot.send_message(
        chat_id=telegram_id,
        text=messages.ADMIN_PANEL,
        reply_markup=keyboard,
    )


@ErrorHandler.create()
def admin(message: Message, bot: TeleBot):
    """Обработка команды '/admin'."""
    telegram_id = message.chat.id
    RedisCacheManager.set(key=telegram_id, file_id=None)

    if telegram_id not in settings.ADMIN_IDS:
        return bot.send_message(
            chat_id=telegram_id,
            text=messages.NO_ADMIN_RIGHTS,
        )

    data = get_admin_menu_data()
    keyboard = KeyboardConstructor().create_inline_keyboard(data)
    return bot.send_message(
        chat_id=telegram_id,
        text=messages.ADMIN_PANEL,
        reply_markup=keyboard,
    )


@ErrorHandler.create()
def start_fast_mailing(callback: CallbackQuery, bot: TeleBot):
    telegram_id = callback.message.chat.id
    bot.send_message(
        chat_id=telegram_id,
        text=messages.SEND_VIDEO_NOTE
    )
    bot.register_next_step_handler_by_chat_id(telegram_id, handle_video_note, bot)


@ErrorHandler.create()
def handle_video_note(message: Message, bot: TeleBot):
    telegram_id = message.chat.id
    if message.text == "/admin":
        pass

    if not message.video_note:
        bot.send_message(
            chat_id=telegram_id,
            text=messages.SENT_NOT_VIDEO_NOTE
        )
        bot.register_next_step_handler_by_chat_id(telegram_id, handle_video_note, bot)

    file_id = message.video_note.file_id
    RedisCacheManager.set(key=telegram_id, file_id=file_id)

    keyboard = KeyboardConstructor(one_time_keyboard=True).create_inline_keyboard(
        {
            "✉️ Отправить": "broadcast",
            "❌ Отменить": "admin"
        }
    )

    bot.send_message(
        chat_id=telegram_id,
        text=messages.AFTER_VIDEO_NOTE_QUESTION,
        reply_markup=keyboard,
    )


@ErrorHandler.create()
def broadcast_video_note_callback(callback: CallbackQuery, bot: TeleBot):
    from server.apps.periodic_tasks.tasks import broadcast_video_note
    bot.edit_message_reply_markup(
        callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )
    telegram_id = callback.message.chat.id
    cache = RedisCacheManager.get(key=telegram_id)
    file_id = cache.get("file_id", None)
    if not file_id:
        return bot.send_message(
            chat_id=telegram_id,
            text=messages.NO_FILE_ID
        )

    broadcast_video_note.delay(file_id, telegram_id)

    bot.send_message(
        chat_id=telegram_id,
        text=messages.BROADCAST_START
    )
