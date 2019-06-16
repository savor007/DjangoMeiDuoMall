from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as id_serializer, BadData
from django.conf import settings
from Backend_Trunk.utils.constants import *
import logging


logger=logging.getLogger('django')

class User(AbstractUser):
    """
    AbstractUser has a lots of necessary properties and fields
    """
    mobile=models.CharField(max_length=11, unique=True, verbose_name='phone number')
    email=models.CharField(max_length=21, unique=True,verbose_name='email',null= True)
    email_active=models.BooleanField(default=False, verbose_name='email status')

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



    @staticmethod
    def check_send_sms_code_token(token):
        myserializer=id_serializer(settings.SECRET_KEY, expires_in= SEND_SMS_TOKEN_EXPIRE)
        try:
            data=myserializer.loads(token)
        except BadData as error:
            logger.info(error)
            return None
        else:
            mobile= data.get('mobile', None)
            return mobile



    def generate_changepassword_code(self):
        myserializer = id_serializer(settings.SECRET_KEY, expires_in=SEND_SMS_TOKEN_EXPIRE)
        data = {"user_id": self.id}
        token = myserializer.dumps(data)
        """
        生成的token是二进制的需要decode
        """
        return token.decode()


    @staticmethod
    def check_change_password_token(token,user_id):
        myserializer=id_serializer(settings.SECRET_KEY, expires_in= CHANGE_PASSWORD_TOKEN_EXPIRE)
        try:
            data=myserializer.loads(token)
        except BadData as error:
            logger.error(error)
            return None
        if user_id== str(data.get("user_id", None)):
            return user_id
        else:
            return None


