from django.db import models
from Backend_Trunk.utils.models import BaseModel
from urllib.parse import *


# Create your models here.

class OAuthQQUser(BaseModel):
    user=models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name='用户')
    openid=models.CharField(max_length=64, verbose_name='QQ openid', db_index=True)

    class Meta:
        db_table='tb_oauth_qq'
        verbose_name='QQ登陆用户数据'
        verbose_name_plural=verbose_name