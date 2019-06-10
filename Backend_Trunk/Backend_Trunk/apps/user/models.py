from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as id_serializer
from django.conf import settings
from Backend_Trunk.utils.constants import *


class User(AbstractUser):
    """
    AbstractUser has a lots of necessary properties and fields
    """
    mobile=models.CharField(max_length=11, unique=True, verbose_name='phone number')

    class Meta:
        db_table='tb_user'
        verbose_name='User'
        verbose_name_plural=verbose_name

# Create your models here.
    def __str__(self):
        return "user id is %s, username is %s." % (str(self.id), str(self.username))


    def generate_send_sms_code(self):
        myserializer=id_serializer(settings.SECRET_KEY, expires_in=SEND_SMS_TOKEN_EXPIRE)
        data={"mobile":self.mobile}
        token=myserializer.dumps(data)
        """
        生成的token是二进制的需要decode
        """
        return token.decode()