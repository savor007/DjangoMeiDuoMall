from celery import Celery


app=Celery('meiduo')
app.config_from_object('celery_tasks.setting')

app.autodiscover_tasks(['celery_tasks.sms'])


# celery -A celery_tasks.main worker -l info