from rest_framework import serializers
from .utils import OAuth
import logging
from django_redis import get_redis_connection
from user.models import User
from .models import OAuthQQUser

logger=logging.getLogger('django')


class BandOpenIDSerializer(serializers.ModelSerializer):
    access_token= serializers.CharField(label="操作凭证，包含openid", write_only=True)
    mobile=serializers.RegexField(label='手机号',regex=r'^1[3-9]\d{9}$', write_only= True)
    password=serializers.CharField(label='password', max_length=20, min_length=8, write_only= True)
    sms_code=serializers.CharField(label='短信验证码', write_only= True)

    class Meta:
        model=OAuthQQUser
        fields=['user','openid', 'password', 'sms_code','mobile', 'access_token']
        """
        单独生命的属性，如 access—token，mobile，password，必须放到fields列表中
        """
        extra_kwargs = {
            'user': {'read_only': True, 'allow_null':True},
            'openid': {'read_only': True, 'allow_null':True}
            }




    def validate(self, attrs):
        access_token=attrs.get('access_token')
        try:
            openid=OAuth.release_openid_token(access_token)
        except Exception as error:
            logger.error(str(error))
            raise serializers.ValidationError("invalid token for openid")
        else:
            if not openid:
                raise serializers.ValidationError("invalid token for openid")

            mobile=attrs.get('mobile')
            sms_code=attrs.get('sms_code')
            redis_handler=get_redis_connection('verify_codes')
            verify_sms_code=redis_handler.get('sms_verification_code_for_'+mobile)
            if verify_sms_code.decode().lower()!=sms_code.lower():
                raise serializers.ValidationError("短信验证码错误")

            try:
                user=User.objects.get(mobile=mobile)
            except Exception as error:
                logger.info('this mobile user have not registered yet.')
                user=User()
                user.mobile=mobile
                user.set_password(attrs.get('password'))
                user.username=mobile
                user.save()
                attrs={"user":user,"openid":openid}
                return attrs
            else:
                attrs = {"user": user, "openid": openid}
                return attrs


