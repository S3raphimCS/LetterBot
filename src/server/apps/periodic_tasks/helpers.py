import mimetypes


def except_telegram_exception(exception, user) -> str:
    if exception.error_code == 403 and "bot was blocked by the user" in exception.description:
        user.is_active = False
        user.save(update_fields=["is_active"])
        return f"Пользователь {user.telegram_id} заблокировал бота."
    elif exception.error_code == 400 and "chat not found" in exception.description:
        user.is_active = False
        user.save(update_fields=["is_active"])
        return f"Чат {user.telegram_id} не найден. Деактивируем."
    elif exception.error_code == 403 and "user is deactivated" in exception.description:
        user.is_active = False
        user.save(update_fields=["is_active"])
        return f"Пользователь {user.telegram_id} деактивирован."
    else:
        return f"Неожиданная ошибка Telegram API для пользователя {user.telegram_id}: {exception}"


def media_is_video(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith("video"):
        return True
    else:
        return False
