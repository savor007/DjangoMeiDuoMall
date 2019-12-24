from django.shortcuts import render
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework_jwt.views import obtain_jwt_token
import random

from rest_framework_jwt.views import ObtainJSONWebToken

from cart.utils import Merge_Cookie_Cart
from .models import User, Address
from .serializers import CreateUserSerializer ,Change_Password_Serializer, UserInfoSerializer, EmailSerializer, EmailVericationSerializer
from .serializers import AddressSerializer_List, AddressSerializer_Create, AddressSerializer_Update , AddressTitleSerialzer
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
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_403_FORBIDDEN
from rest_framework.decorators import action

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


class EmailView(UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    """
    调用updateAPIView时会用到update的方法，update时用会用到get_object,get_object默认使用pk
    """

    def get_serializer(self, *args, **kwargs):
        return EmailSerializer(instance= self.request.user, data=self.request.data)

    def get_object(self):
        return self.request.user


class EmailVerificationView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = EmailVericationSerializer

    def get(self, request):
        myserializer= self.get_serializer(data=request.query_params)
        myserializer.is_valid(raise_exception= True)
        user=myserializer.validated_data['user']
        user.email_active=True
        user.save()
        return Response({"message":"OK"})



class AddressViewSet(ModelViewSet):

    permissions = [IsAuthenticated]

    def get_queryset(self):
        queryset=self.request.user.addresses.filter(is_deleted=False)
        queryset2=Address.objects.filter(is_deleted=False, user_id=self.request.user.id)
        return queryset




    def get_serializer_class(self):
        if self.action=='list':
            return AddressSerializer_List
        elif self.action in ['update','create'] :
            return AddressSerializer_Create
        elif self.action=='title':
            return AddressTitleSerialzer
        else:
            None


    def list(self, request, *args, **kwargs):
        """
        重写 list 方法，发送复合前端要求的RESPONSE数据
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user=self.request.user
        myserializer=self.get_serializer(instance=self.get_queryset(),many=True)
        return Response(data={
            "user_id":user.id,
            "default_address_id":user.default_address_id,
            "limit": USER_ADDRESS_COUNTS_LIMIT,
            "addresses":myserializer.data,
        })


    def create(self,request, *args, **kwargs):
         user=self.request.user
         address_count=user.addresses.filter(is_deleted=False).count()
         if address_count>=USER_ADDRESS_COUNTS_LIMIT:
             return Response(data={
                 "message":"保存地址数据已经达到上限"
             })
         logger.info("address request data: " + str(self.request.data))
         myserializer=self.get_serializer(data=self.request.data)
         if myserializer.is_valid()==False:
            print(str(myserializer.errors))
            raise Exception("validator error")
         new_address= myserializer.save()

         formatter_serializer=AddressSerializer_List(many=False, instance=new_address)
         return Response(data= {
             "address":formatter_serializer.data
         })

    def destroy(self, request, *args, **kwargs):
        address=self.get_object()
        address.is_deleted=True
        address.save()
        return Response(data={
            "message":"OK"
        })


    @action(method=['put'], detail=True)
    def defaultaddress(self, request, *args, **kwargs):
        user=self.request.user
        address = self.get_object()
        user.default_address=address
        user.save()
        return Response(data={
            "message":"OK"
        })



    @action(method=['put'], detail=True)
    def title(self, request, *args, **kwargs):
        address=self.get_object()
        myserializer=self.get_serializer(instance= address, data= self.request.data)
        if myserializer.is_valid()==False:
            logger.error(myserializer.errors)
            raise Exception("validator error")
        myserializer.save()
        return Response(data=myserializer.data)


    def update(self,request, *args, **kwargs):
         logger.info("address request data: " + str(self.request.data))
         myserializer=self.get_serializer(instance= self.get_object(), data=self.request.data)
         if myserializer.is_valid()==False:
            print(str(myserializer.errors))
            raise Exception("validator error")
         new_address= myserializer.save()

         formatter_serializer=AddressSerializer_List(many=False, instance=new_address)
         return Response(data= {
             "address":formatter_serializer.data
         })



class ObtainJSONwebTokenwithCookies(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        response= super(ObtainJSONwebTokenwithCookies, self).post(request)

        if response.status_code == HTTP_200_OK:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.object.get('user') or request.user
                response= Merge_Cookie_Cart(user_id=user.id, request=request, response=response)
        return response










