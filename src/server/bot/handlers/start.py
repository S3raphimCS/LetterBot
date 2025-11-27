from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from server.apps.users.models import BotUser
from server.bot.cache.manager import RedisCacheManager
from server.bot.handlers.helpers import get_start_data
from server.bot.utils import messages
from server.bot.utils.error_handler import ErrorHandler
from server.bot.utils.keyboards import KeyboardConstructor


@ErrorHandler.create()
def start(message: Message, bot: TeleBot):
    """Обработка команды '/start'."""
    telegram_id = message.chat.id
    RedisCacheManager.delete(key=telegram_id)
    username = message.from_user.first_name if message.from_user.first_name else message.from_user.username
    user, _ = BotUser.objects.update_or_create(telegram_id=telegram_id, defaults={'username': username})
    data = get_start_data()
    keyboard = KeyboardConstructor().create_inline_keyboard(data)
    return bot.send_message(
        chat_id=telegram_id,
        text=messages.START_BOT,
        reply_markup=keyboard,
    )


@ErrorHandler.create()
def menu(callback: CallbackQuery, bot: TeleBot):
    telegram_id = callback.message.chat.id
    RedisCacheManager.delete(key=telegram_id)
    data = get_start_data()
    keyboard = KeyboardConstructor().create_inline_keyboard(data)
    return bot.send_message(
        chat_id=telegram_id,
        text=messages.START_BOT,
        reply_markup=keyboard,
    )
