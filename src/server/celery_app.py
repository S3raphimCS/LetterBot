import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

app = Celery('server')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.timezone = 'UTC'
app.conf.update(worker_cancel_long_running_tasks_on_connection_loss=True)
