from django.conf import settings
from django.core.management import BaseCommand

from server.bot.management.commands.utils import TelegramBotWebhook


class Command(BaseCommand):
    """Команда для установки вебхука для бота клиента."""

    help = 'Запуск телеграм бота'

    def handle(self, *args, **options):
        TelegramBotWebhook(token=settings.BOT_TOKEN, url='api/v1/webhook').run()