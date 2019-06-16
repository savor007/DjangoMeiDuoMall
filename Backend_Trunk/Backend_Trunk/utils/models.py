from django.db import models


class BaseModel(models.Model):
    create_time=models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time=models.DateTimeField(auto_now= True, verbose_name='更新时间')

    class Meta:
        abstract= True    # 说明是抽象类，只用来继承，不会生成数据表
