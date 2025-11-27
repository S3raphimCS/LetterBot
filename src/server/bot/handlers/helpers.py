from server.bot.utils import buttons
from server.bot.utils.callbacks import Callback


def get_start_data() -> dict:
    """Получение кнопок после регистрации клиента."""
    callback_data = {

    }
    return callback_data


def get_return_menu_data() -> dict:
    callback_data = {
        buttons.RETURN_MENU: Callback.RETURN_MENU.value,
    }
    return callback_data
