from Backend_Trunk.libs.yuntongxun import sms
from Backend_Trunk.utils.constants import *
# from CeleryTask.main import celery_worker
from celery_tasks.main import app
import logging

logger = logging.getLogger('django')

@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    SMS_Sender = sms.CCP()
    sms_result = -1
    sms_result = SMS_Sender.send_template_sms(mobile, [sms_code, SMS_CODE_EXPIRY / 60], 1)
    if sms_result != 0:
        logger.error('sms code sending failure')
    else:
        logger.info('sms code sent success')