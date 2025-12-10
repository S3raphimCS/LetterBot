from server.bot.utils import buttons
from server.bot.utils.callbacks import Callback


def get_start_data() -> dict:
    """Получение кнопок после регистрации клиента."""
    callback_data = {

    }
    return callback_data


def get_admin_menu_data() -> dict:
    """Получение кнопок админ-панели."""
    callback_data = {
        buttons.FAST_MAILING: Callback.FAST_MAILING.value,
        buttons.VOICE_MAILING: Callback.VOICE_MAILING.value,
    }
    return callback_data
