from django.shortcuts import render
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework_jwt.views import obtain_jwt_token
import random
from .models import User
from .serializers import CreateUserSerializer ,Change_Password_Serializer, UserInfoSerializer
from itsdangerous import TimedJSONWebSignatureSerializer as id_serializer
from django.conf import settings
from Backend_Trunk.apps.verification.serializers import ImageCodeSerializer
from .serializers import SMS_Code_Serializer
from .utils import get_user_by_account
from rest_framework import mixins
import re
import logging
from django_redis import get_redis_connection
from Backend_Trunk.utils.constants import *
from celery_tasks.sms.tasks import send_sms_code
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_403_FORBIDDEN

logger=logging.getLogger('django')


# Create your view functions here.


class UserAccount_UserName(APIView):
    def get(self, request, username):
        user_count=User.objects.filter(username=username).count()
        return Response(data={"username":username, "count":user_count}, status=200)



class UserAccount_Mobile(APIView):
    def get(self, request, mobile):
        user_count = User.objects.filter(mobile= mobile).count()
        return Response(data={"mobile": mobile, "count": user_count}, status=200)



class UserData(CreateAPIView):
    queryset = User.objects.all()     #没有必要，因为只是涉及到创建，不涉及查询
    serializer_class = CreateUserSerializer




"""
找回密码操作，找回密码没有使用默认的JW，因为默认的JWT生成token时会把密码数据放在token里，
而找回密码只需要使用usename或者userid,
ITSDangouse中的TimedJSONWebSignatureSerializer更灵活
"""

"""
accounts/(?P<account>\w{5,20})/sms/token/?image_code_id=xx&text=xxx
"""
class SMSCodeTokenView(GenericAPIView):
    serializer_class = ImageCodeSerializer
    queryset = User.objects.all()

    def get(self, request, account):
        print(request.query_params)
        myserializer=self.get_serializer(data=request.query_params)
        myserializer.is_valid(raise_exception=True)
        user=get_user_by_account(account)
        if not user:
            return Response({'message':'the input user %s does not exist' % account}, status=HTTP_404_NOT_FOUND )
        token= user.generate_send_sms_code()
        mobile=re.sub(r'(\d{3})\d{4}(\d{4})',r'\1****\2',user.mobile)

        return Response(data={"mobile": mobile, "access_token": token}, status=HTTP_200_OK)


"""
/sms_codes/?access_token=XXXXXXXX
"""
class SMS_Verifcation_ByToken(APIView):
    def get(self, request):
        access_token= request.query_params.get("access_token")
        if not access_token:
            return Response(data={"message":"invalid mobile number or no mobile found"}, status=HTTP_400_BAD_REQUEST)

        mobile=User.check_send_sms_code_token(access_token)
        if not mobile:
            return Response(data={"message":"invalid mobile number or no mobile found"}, status=HTTP_400_BAD_REQUEST)

        redis_handle = get_redis_connection('verify_codes')
        send_flag=redis_handle.get("send_flag_"+mobile)
        if send_flag:
            return Response({"message":"too frequent for sms request"}, status=HTTP_429_TOO_MANY_REQUESTS)
        # SMS_Sender=sms.CCP()
        # sms_result=-1
        # sms_result= SMS_Sender.send_template_sms(mobile, [sms_code, SMS_CODE_EXPIRY/60] ,1)
        # if sms_result!=0:
        #     return Response(status=HTTP_500_INTERNAL_SERVER_ERROR, data='can not send sms code!')

        sms_code = "%06d" % random.randint(0, 999999)
        logger.info("sms verfication code is " + sms_code)
        print(mobile)
        send_sms_code.delay(mobile, sms_code)
        """

        save sms code into redis
        """

        redis_pipeline = redis_handle.pipeline()
        redis_pipeline.multi()
        redis_pipeline.setex("send_flag_" + mobile, MOBILE_REQUEST_EXPRIRY, 1)
        redis_pipeline.setex("sms_verification_code_for_" + mobile, SMS_CODE_EXPIRY, sms_code)

        redis_pipeline.execute()

        return Response(status=HTTP_200_OK, data={"message": "OK"})



"""
generate token for final modify the password
url is "accounts/(?P<account>\w{5,20})/password/token/?sms_code=xxxxxx"
"""

class Password_Token(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = SMS_Code_Serializer

    def get(self, request, account):
        received_sms_code= request.query_params.get("sms_code",None)
        if not received_sms_code:
            return Response(data={"message":"invalid SMS code"},status=HTTP_400_BAD_REQUEST)
        sms_code_serializer=self.get_serializer(data={"sms_code":received_sms_code})
        sms_code_serializer.is_valid(raise_exception=True)
        user=sms_code_serializer.user
        access_token=user.generate_changepassword_code()
        return Response({"user_id":user.id, "access_token":access_token})



"""
设置密码
POST users/(?P<pk>\d+)/password/$
从post中取token
"""
class PasswordVIEW(mixins.UpdateModelMixin, GenericAPIView):  #没有使用UplateAPIview因为它支持put patch，不支持post
    queryset = User.objects.all()
    serializer_class = Change_Password_Serializer

    def post(self, request,pk):
         return self.update(request,pk)




class UserInfoView(RetrieveAPIView):
    # queryset = User.objects.all()
    serializer_class = UserInfoSerializer
    permission_classes = [IsAuthenticated]
    """
    通过JWT认证通过后，会把user信息放到request user里
    """

    def get_object(self):
        """
        使用get——object本身会判断访问权限
        :return:
        """
        return self.request.user