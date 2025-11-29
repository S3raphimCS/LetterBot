from django.core.validators import FileExtensionValidator
from django.db import models

from server.apps.users.models import BotUser
from server.apps.mailing.base.models import BaseLog
from server.apps.mailing.validators import validate_file_size, validate_url


class Mailing(models.Model):
    """Модель рассылки"""

    title = models.CharField(verbose_name="Заголовок", max_length=255, null=True, blank=True)
    text = models.TextField(verbose_name="Сообщение рассылки", max_length=4096, null=True, blank=True)
    # image = models.ImageField(verbose_name="Изображение рассылки", upload_to="mailings/", blank=True, null=True)
    time_start = models.DateTimeField(verbose_name="Дата и время начала рассылки", blank=True, null=True)
    is_instant = models.BooleanField(verbose_name="Немедленная рассылка", default=False)
    # recipient_type = models.CharField(verbose_name="Тип получателей", max_length=255, choices=RecipientType.choices)
    ready_to_send = models.BooleanField(verbose_name="Готова к отправке", default=False)
    is_processed = models.BooleanField(verbose_name="В обработке", default=False)
    button_text = models.CharField(verbose_name="Текст кнопки", max_length=255, null=True, blank=True)
    button_link = models.CharField(verbose_name="Ссылка кнопки", max_length=255, null=True, blank=True, validators=[validate_url])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"


class MailingMedia(models.Model):
    """Модель фото шага сценария."""

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name="Рассылка", related_name="media_files")
    media = models.FileField(
        verbose_name="Фото",
        upload_to="mailing_photos/",
        validators=[
            validate_file_size,
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi', 'hevc']
            )
        ]
    )

    class Meta:
        verbose_name = "Медиа-файл рассылки"
        verbose_name_plural = "Медиа-файлы рассылки"


class MailingLog(BaseLog):
    """Модель лога попытки рассылки"""

    mail = models.ForeignKey(Mailing, verbose_name="Рассылка", on_delete=models.CASCADE, related_name="logs")

    class Meta:
        verbose_name = "Лог рассылки"
        verbose_name_plural = "Логи рассылки"


class Scenario(models.Model):
    """Модель составного сценария отправки пользователю сообщений."""

    title = models.CharField("Название сценария", max_length=255)
    trigger_delay_hours = models.PositiveIntegerField("Запуск через (часов)")
    is_active = models.BooleanField("Активен", default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Сценарий"
        verbose_name_plural = "Сценарии"


class ScenarioStep(models.Model):
    """Модель шага сценария."""

    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, verbose_name="Сценарий", related_name="steps")
    text = models.TextField(verbose_name="Текст", max_length=4096, null=True, blank=True)
    button_text = models.CharField("Текст кнопки", max_length=255, null=True, blank=True)
    button_url = models.URLField(verbose_name="Ссылка кнопки", null=True, blank=True, validators=[validate_url])
    delay_seconds = models.PositiveIntegerField("Задержка (секунд)", null=True, blank=True)

    def __str__(self):
        return self.scenario.title

    class Meta:
        verbose_name = "Шаг сценария"
        verbose_name_plural = "Шаги сценария"


class ScenarioStepMedia(models.Model):
    """Модель медиа-файла шага сценария."""

    scenario = models.ForeignKey(ScenarioStep, on_delete=models.CASCADE, verbose_name="Шаг сценария", related_name="media_files")
    media = models.FileField(
        verbose_name="Фото",
        upload_to="scenario_photos/",
        validators=[
            validate_file_size,
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi', 'hevc']
            )
        ]
    )

    class Meta:
        verbose_name = "Медиа-файл шага сценария"
        verbose_name_plural = "Медиа-файлы шага сценария"


class ScenarioMailingLog(BaseLog):
    """Модель лога попытки рассылки сообщения сценария"""

    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, verbose_name="Сценарий", related_name="logs")

    class Meta:
        verbose_name = "Лог рассылки"
        verbose_name_plural = "Логи рассылок"


class UserScenarioMailing(models.Model):
    """Модель отправленных пользователям сценариев."""

    user = models.ForeignKey(BotUser, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="scenarios")
    scenario = models.ForeignKey(ScenarioStep, on_delete=models.CASCADE, verbose_name="Шаг сценария", related_name="users")

    class Meta:
        verbose_name = "Пользователь рассылки"
        verbose_name_plural = "Пользователи рассылки"
