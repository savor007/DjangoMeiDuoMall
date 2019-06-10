from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework_jwt.views import obtain_jwt_token

from .models import User
from .serializers import CreateUserSerializer
from itsdangerous import TimedJSONWebSignatureSerializer as id_serializer
from django.conf import settings
from Backend_Trunk.apps.verification.serializers import ImageCodeSerializer
from .utils import get_user_by_account
import re


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



