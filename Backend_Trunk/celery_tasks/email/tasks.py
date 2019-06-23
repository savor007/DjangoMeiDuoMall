from Backend_Trunk.utils.constants import *
# from CeleryTask.main import celery_worker
from celery_tasks.main import app
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger('django')

@app.task(name='send_verify_email')
def send_verify_email(receiver_email, username, callback_url):
    """

    :param receiver_email:
    :param callback_url:
    :return: None
    """
    subject="美多商城邮箱验证邮件"
    recipient_list=[receiver_email]
    html_message='<p>尊敬的用户%s您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (username, receiver_email, callback_url, callback_url)

    send_mail(subject=subject, message="", from_email= settings.EMAIL_FROM,recipient_list=recipient_list, html_message=html_message )
    return None