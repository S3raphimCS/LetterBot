from django.contrib.auth.models import AbstractUser
from django.db import models

from server.apps.users.managers import UserManager


class BaseUser(AbstractUser):
    """Модель Администратора"""

    objects = UserManager()

    username = None
    email = models.EmailField(verbose_name='Email', unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы'


class BotUser(models.Model):
    """Модель пользователя бота"""

    telegram_id = models.IntegerField(verbose_name="Telegram ID", unique=True)
    username = models.CharField(verbose_name="Username", max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name="Дата и время создания", auto_now_add=True)

    def __str__(self):
        return f"{self.telegram_id}"

    class Meta:
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"
