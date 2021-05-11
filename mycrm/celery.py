import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycrm.settings')
mycrm = Celery('mycrm')
mycrm.config_from_object('django.conf:settings', namespace='CELERY')
mycrm.autodiscover_tasks()

mycrm.conf.beat_schedule = {
    'daily_event': {
        'task': 'mainapp.tasks.daily_event',
        'schedule': crontab(minute=0, hour=0)
    }
}
