from rest_framework import serializers
from .models import User
import re
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings
from .utils import get_user_by_account
import logging

logger=logging.getLogger('django')

class CreateUserSerializer(serializers.ModelSerializer):
    """
    create user serializer for new user creation
    """



    password2=serializers.CharField(label='confirm password', required=True, allow_null=False, allow_blank=False, write_only=True)
    sms_code=serializers.CharField(label='sms verificaition code', required=True, allow_null=False, allow_blank=False, write_only=True)
    allow=serializers.CharField(label='agreement', required=True, allow_blank=False, allow_null=False, write_only=True)
    token=serializers.CharField(label='JWT Token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow', 'token')
        """
        单独声明出的属性必须放在fields列表中，如allow和sms-code等
        """
        extra_kwargs = {
            'id': {'read_only': True},
            'usernanme': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '用户名仅允许5到20个字符',
                    'max_length': '用户名仅允许5到20个字符',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '密码仅允许8到20个字符',
                    'max_length': '密码仅允许8到20个字符',
                }
            },

        }

    def validate_mobile(self,value):
        if not re.match(r'^1[345789]\d{9}$', value):
            raise serializers.ValidationError('wrong phone format')
        return value


    def validate_allow(self, value):
        if value!='true':
            raise serializers.ValidationError('Please check agreement')
        return value



    def validate(self, attrs):
        password=attrs.get('password')
        re_password=attrs.get('password2')
        mobile=attrs.get('mobile')
        if password!=re_password:
            raise serializers.ValidationError('Inconformity of input passwords ')
        sms_code=attrs.get('sms_code')
        redis_handler=get_redis_connection('verify_codes')
        sms_verify_code=redis_handler.get("sms_verification_code_for_"+mobile)
        if sms_verify_code==None:
            raise serializers.ValidationError('Invalid Verfication Code. Maybe it is expired')
        if sms_verify_code.decode()!=sms_code:
            raise serializers.ValidationError('sms code verificaton fail')

        return attrs


    def create(self, validated_data):
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 也可以直接调用使用user object 的方式
        user= super(CreateUserSerializer, self).create(validated_data)
        # user=User.objects.create(validated_data)


        #因为继承子abstractUser类，认证过程必须调用set——password的方法
        user.set_password(validated_data['password'])
        user.save()


        # generate token for front end
        jwt_payload_handler=api_settings.JWT_PAYLOAD_HANDLER
        jwt_encoder_handler=api_settings.JWT_ENCODE_HANDLER
        payload=jwt_payload_handler(user)
        token=jwt_encoder_handler(payload)
        user.token=token
        return user


class SMS_Code_Serializer(serializers.Serializer):
    sms_code=serializers.CharField(min_length=6, max_length=6)


    def validate_sms_code(self, attr):
        account=self.context["view"].kwargs.get("account")

        if not account:
            raise serializers.ValidationError("can not get account from view")
        user=get_user_by_account(account)
        if not user:
            raise serializers.ValidationError("can not get user from the account")
        self.user=user
        mobile=user.mobile
        redis_handler=get_redis_connection("verify_codes")
        verify_sms_code=redis_handler.get("sms_verification_code_for_"+mobile)
        if verify_sms_code is None:
            raise serializers.ValidationError("Invalid SMS code")
        if verify_sms_code.decode()!=attr:
            raise serializers.ValidationError("Unmatch sms code")
        else:
            return attr


class Change_Password_Serializer(serializers.ModelSerializer):
    password2=serializers.CharField(label='确认密码', write_only= True)
    access_token=serializers.CharField(label='access token', write_only=True)

    class Meta:
        model=User
        fields=['id','password2','password','access_token']

        extra_kwargs={
            'password':{
                "write_only":True,
                "min_length":8,
                "max_length":20,
                "error_messages":{
                    "min_length":"仅允许8到20个字符的密码",
                    "max_length": "仅允许8到20个字符的密码",

                }
            }
        }


    def validate(self, attrs):
        print(str(attrs))
        if attrs['password']!=attrs['password2']:
            logger.error("passowrd is %s, confirm-password is %s" % (attrs['password'], attrs['password2'] ))
            raise serializers.ValidationError('两次输入的密码不一致')

        if User.check_change_password_token(attrs['access_token'], self.context['view'].kwargs.get('pk',None)):
            return attrs
        else:
            raise serializers.ValidationError("密码token验证错误")



    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model='User'
        fields=['id','username','mobile','email','email_active']


