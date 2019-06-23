from celery import Celery

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE']='Backend_Trunk.settings.DevelopmentSettings'


app=Celery('meiduo')
app.config_from_object('celery_tasks.setting')

app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email', 'celery_tasks.html'])


# celery -A celery_tasks.main worker -l info