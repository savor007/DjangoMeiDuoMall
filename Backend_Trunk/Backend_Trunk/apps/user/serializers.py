from rest_framework import serializers
from .models import User, Address
import re
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings
from .utils import get_user_by_account
import logging
from celery_tasks.email.tasks import send_verify_email
from area.models import Area

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
        model=User
        fields=['id','username','mobile','email','email_active']


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','email']
        extra_kwargs={
            'email':{
                'required':True
            },
            'username': {
                'read_only': True
            },

        }


    def update(self, instance: User, validated_data):
        instance.email=validated_data.get('email')
        instance.save()

        callbackurl= instance.generate_email_url()
        send_verify_email.delay(validated_data.get('email'),instance.username,callbackurl)

        return instance


class EmailVericationSerializer(serializers.ModelSerializer):
    token=serializers.CharField(label='确认邮件', write_only= True)
    class Meta:
        model=User
        fields=['id','email', 'email_active', 'token']
    """
    fields中列出了要序列化器验证的字段， 如果设置了write only，就会从传入的数据，query_params中取
    """

    def validate(self, attrs):
        token= attrs.get('token')
        if not token:
            raise serializers.ValidationError('Invalid Token for email activation')
        user=User.Check_UserID_Email_token(token)
        if user:
            attrs['user']=user
            return attrs
        else:
            raise serializers.ValidationError('Invalid Token for email activation')


class AddressSerializer_List(serializers.ModelSerializer):
    province=serializers.StringRelatedField(read_only=True)
    city=serializers.StringRelatedField(read_only=True)
    district=serializers.StringRelatedField(read_only=True)
    """
    在area中已经定义了__str__方法，直接返回name
    """

    class Meta:
        model= Address
        exclude=['user', 'is_deleted', 'create_time', 'update_time']


class AddressSerializer_Create(serializers.ModelSerializer):

    # this.form_address.receiver = '';
    # this.form_address.province_id = '';
    # this.form_address.city_id = '';
    # this.form_address.district_id = '';
    # this.form_address.place = '';
    # this.form_address.mobile = '';
    # this.form_address.tel = '';
    # this.form_address.email = '';
    province_id=serializers.IntegerField(min_value=0, write_only=True, allow_null=False)
    district_id = serializers.IntegerField(min_value=0, write_only=True, allow_null=False)
    city_id = serializers.IntegerField(min_value=0, write_only=True, allow_null=False)

    class Meta:
        model= Address
        exclude = ['user', 'is_deleted', 'create_time', 'update_time']
        extra_kwargs = {
            'province': {
                'read_only': True
            },
            'city': {
                'read_only': True
            },
            'district': {
                'read_only': True
            },
        }


    def create(self, validated_data):
        user=self.context['request'].user
        new_address=Address()
        new_address.user=user
        new_address.is_deleted=False
        new_address.receiver=validated_data.get('receiver')
        new_address.tel=validated_data.get('tel')
        new_address.place=validated_data.get('place')
        new_address.title=validated_data.get('title')
        new_address.province=Area.objects.get(id=validated_data.get('province_id'))
        new_address.city=Area.objects.get(id=validated_data.get('city_id'))
        new_address.district=Area.objects.get(id=validated_data.get('district_id'))

        new_address.mobile=validated_data.get('mobile')
        new_address.email=validated_data.get('email')
        try:
            new_address.save()
        except Exception as error:
            logger.error("Error in new user address saving")
            raise serializers.ValidationError("Error in new user address saving")
        validated_data['new_address']=new_address
        return new_address


class AddressSerializer_Update(serializers.ModelSerializer):
    class Meta:
        model= Address
        fields=[]


class AddressTitleSerialzer(serializers.ModelSerializer):
    """
    前端发送请求，修改地址名称， 如家的地址，公司地址等，请求方式是put
    """
    class Meta:
        model=Address
        fields=['title']





