from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as id_serializer, BadData
from django.conf import settings
from Backend_Trunk.utils.constants import *
import logging

from Backend_Trunk.utils.models import BaseModel

logger=logging.getLogger('django')

class User(AbstractUser):
    """
    AbstractUser has a lots of necessary properties and fields
    """
    mobile=models.CharField(max_length=11, unique=True, verbose_name='phone number')
    #email=models.CharField(max_length=21, unique=True,verbose_name='email',null= True)
    email_active=models.BooleanField(default=False, verbose_name='email status')
    default_address=models.ForeignKey('Address', related_name='users', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='default address')

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


    def generate_email_url(self):
        myserializer = id_serializer(settings.SECRET_KEY, expires_in=SEND_SMS_TOKEN_EXPIRE)
        data = {"user_id": self.id, "email": self.email}
        token = myserializer.dumps(data)
        """
        生成的token是二进制的需要decode
        """
        callbackurl="http://www.meiduo.site:8080/success_verify_email.html?token="+token.decode()
        return callbackurl

    @staticmethod
    def Check_UserID_Email_token(token):
        myserializer = id_serializer(settings.SECRET_KEY, expires_in=CHANGE_PASSWORD_TOKEN_EXPIRE)
        try:
            data = myserializer.loads(token)
        except BadData as error:
            logger.error(error)
            return None
        user_id = data.get("user_id", None)
        email = str(data.get("email", None))
        if (not user_id) or (not email):
            return None
        user= User.objects.get(id=user_id, email=email)
        if user:
            return user
        else:
            return None



class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('area.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('area.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('area.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']





