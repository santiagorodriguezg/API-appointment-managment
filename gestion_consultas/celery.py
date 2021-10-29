import os

from decouple import config
from celery import Celery
from celery.schedules import crontab

settings = 'local' if config('DJANGO_ENV', default='dev') == 'dev' else 'production'

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'gestion_consultas.settings.{settings}')

app = Celery('gestion_consultas')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    # Scheduler Name
    'delete_token_blacklist_daily_at_midnight': {
        # Task Name
        'task': 'apps.chats.tasks.delete_token_blacklist',
        # Schedule
        'schedule': crontab(minute=0, hour=0),
    },
}
