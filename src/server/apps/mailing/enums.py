from django.db import models


class SendingStatus(models.TextChoices):
    """Перечисление статусов отправки рассылки"""
    SUCCESS = 'success', 'Отправлено успешно'
    ERROR = 'error', 'Ошибка при отправке'
