from django.db import models

from server.apps.mailing.enums import SendingStatus


class BaseLog(models.Model):
    """Абстрактная модель лога рассылки."""

    user_id = models.CharField(verbose_name="ID пользователя", max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(verbose_name="Дата и время создания лога", auto_now_add=True)
    sending_status = models.CharField(verbose_name="Статус отправки", choices=SendingStatus.choices, default=None,
                                      null=True)
    error = models.TextField(verbose_name="Ошибка", null=True, blank=True)

    class Meta:
        abstract = True
        verbose_name = "Абстрактная модель объявления"

    def __str__(self):
        return f"{self.sending_status} {self.user_id}"
