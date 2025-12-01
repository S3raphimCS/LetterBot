import logging

from django.conf import settings
from telebot import TeleBot, logger

from server.bot.handlers.admin import (
    admin,
    admin_with_callback,
    broadcast_video_note_callback,
    start_fast_mailing,
)
from server.bot.handlers.start import start
from server.bot.utils.callbacks import Callback


logger = logger
logger.setLevel(logging.DEBUG)

bot = TeleBot(
    settings.BOT_TOKEN,
    parse_mode='HTML',
)

MESSAGE_HANDLERS_MAP = {
    start: {
        'commands': ['start'],
    },
    admin: {
        'commands': ['admin'],
    },
}

PRE_CHECKOUT_HANDLERS_MAP = {

}

CALLBACK_HANDLERS_MAP = {
    start_fast_mailing: {
        "func": lambda callback: callback.data == Callback.FAST_MAILING.value,
    },
    admin_with_callback: {
        "func": lambda callback: callback.data == Callback.ADMIN.value,
    },
    broadcast_video_note_callback: {
        "func": lambda callback: callback.data == Callback.BROADCAST.value
    }

}


def register_handlers():
    """Функция регистрации обработчиков бота."""
    for func, params in MESSAGE_HANDLERS_MAP.items():
        bot.register_message_handler(
            func,
            **params,
            pass_bot=True,
        )

    for func, params in CALLBACK_HANDLERS_MAP.items():
        bot.register_callback_query_handler(
            func,
            **params,
            pass_bot=True,
        )

    for func, params in PRE_CHECKOUT_HANDLERS_MAP.items():
        bot.register_pre_checkout_query_handler(
            func,
            **params,
            pass_bot=True,
        )


register_handlers()
