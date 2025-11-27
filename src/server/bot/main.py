import logging

from django.conf import settings
from telebot import TeleBot, logger

from server.bot.handlers.payments import payment_callback
from server.bot.handlers.points import point_callbacks
from server.bot.handlers.quests import quests_callback
from server.bot.handlers.socials import socials_callback
from server.bot.handlers.start import menu, start
from server.bot.handlers.tasks import (
    task_callbacks,
    task_prompt_callback,
    task_quiz_callback,
)
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
    }
}

PRE_CHECKOUT_HANDLERS_MAP = {

}

CALLBACK_HANDLERS_MAP = {
    socials_callback: {
        "func": lambda callback: callback.data == Callback.SOCIALS.value
    },
    menu: {
        "func": lambda callback: callback.data == Callback.RETURN_MENU.value
    },
    quests_callback: {
        "func": lambda callback: callback.data == Callback.QUESTS.value
    },
    point_callbacks: {
        "func": lambda callback: callback.data.startswith(Callback.QUEST_START.value) or
                                 callback.data.startswith(Callback.POINT_DECLINE_1.value) or  # noqa
                                 callback.data.startswith(Callback.POINT_DECLINE_2.value) or  # noqa
                                 callback.data.startswith(Callback.POINT_DECLINE_3.value) or  # noqa
                                 callback.data.startswith(Callback.POINT_GPT.value)  # noqa
    },
    task_callbacks: {
        "func": lambda callback: callback.data.startswith(Callback.TASK_START.value) or
                                 callback.data.startswith(Callback.TASK_COMPLETE.value)  # noqa
    },
    task_quiz_callback: {
        "func": lambda callback: callback.data.startswith(Callback.QUIZ.value)
    },
    task_prompt_callback: {
        "func": lambda callback: callback.data.startswith(Callback.PROMPT.value)
    },
    payment_callback: {
        "func": lambda callback: callback.data.startswith(Callback.PAY_QUEST.value)
    },
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
