from mycrm.celery import mycrm # type: ignore
from .models import Application

@mycrm.task
def daily_event():
    Application.update_in_works()
