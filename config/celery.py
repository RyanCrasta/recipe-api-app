from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.conf.enable_utc = False
app.conf.update(timezone = 'Asia/Kolkata')

app.config_from_object(settings, namespace='CELERY')

#celery beat settings
app.conf.beat_schedule= {
    'send-mail-everyday-at-8': {
        'task': 'send_mail_app.tasks.send_mail_function',
        'schedule': crontab(hour=19, minute=13)
    }
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
