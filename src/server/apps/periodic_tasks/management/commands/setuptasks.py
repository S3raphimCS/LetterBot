from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    """Команда для создания периодических задач."""

    help = 'Создание периодических задач'

    def handle(self, *args, **options):
        """Консольный вывод."""
        self.stdout.write("Начато создание периодических задач:\n")
        start = timezone.now()
        self._setup_tasks()
        self.stdout.write(
            "Периодические задачи созданы. Время: "
            f"{(timezone.now() - start).seconds / 60:.2f} мин"
        )

    @staticmethod
    def _setup_tasks():
        """Периодические задачи."""

        every_one_min_cron, _ = CrontabSchedule.objects.get_or_create(
            minute='*/1',
            timezone=settings.TIME_ZONE,
        )

        every_five_min_cron, _ = CrontabSchedule.objects.get_or_create(
            minute='*/5',
            timezone=settings.TIME_ZONE,
        )

        every_ten_min_cron, _ = CrontabSchedule.objects.get_or_create(
            minute='*/10',
            timezone=settings.TIME_ZONE,
        )

        every_one_hour_cron, _ = CrontabSchedule.objects.get_or_create(
            minute='*/60',
            timezone=settings.TIME_ZONE,
        )

        every_twelve_hour_cron, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="*/12",
            timezone=settings.TIME_ZONE
        )

        _ = PeriodicTask.objects.update_or_create(
            name="Отправка запланированных рассылок, готовых к отправке",
            defaults={
                'crontab': every_one_min_cron,
                'task': 'server.apps.periodic_tasks.tasks.send_timed_mailing',
            }
        )

        _ = PeriodicTask.objects.update_or_create(
            name='Отправка моментальных рассылок, готовых с отправке',
            defaults={
                'crontab': every_one_min_cron,
                'task': 'server.apps.periodic_tasks.tasks.send_instant_mailing',
            }
        )

        _ = PeriodicTask.objects.update_or_create(
            name="Отправка сценариев пользователям",
            defaults={
                "crontab": every_five_min_cron,
                "task": "server.apps.periodic_tasks.tasks.check_scenario_dispatcher"
            }
        )
