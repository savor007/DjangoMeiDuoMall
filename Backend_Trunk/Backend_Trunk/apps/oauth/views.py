from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from django.http.response import HttpResponse
import logging
from .models import OAuthQQUser
from rest_framework_jwt.settings import api_settings
from .serializers import BandOpenIDSerializer


from .utils import OAuth
# Create your views here.
logger=logging.getLogger('django')

class QQAuthURLView(APIView):
    def get(self, request):
        state=request.query_params.get('state')
        oauth=OAuth(stat=state)
        auth_url=oauth.get_auth_url()
        return Response(data={"auth_url":auth_url}, status=HTTP_200_OK)


class OpenIDView(APIView):
    def get(self,request):
        code=request.query_params.get('code')
        if not code:
            return Response(data={'message':"no code data"}, status=HTTP_400_BAD_REQUEST)


        oauth_actor=OAuth()
        try:
            access_token=oauth_actor.get_access_token(code)
            openid=oauth_actor.get_openid(access_token)
        except Exception as error:
            logger.error(str(error))
            return Response(data={"message":"can not get opend id from qq"}, status= HTTP_503_SERVICE_UNAVAILABLE)
        else:
            try:
                oauth_user = OAuthQQUser.objects.get(openid=openid)
            except Exception as error:
                logger.info('user has not register with QQ Openid')
                token= oauth_actor.generate_OpenID_Token(openid)
                return Response(data={"access_token":token})
            else:
                username=oauth_user.user.username
                user_id=oauth_user.user.id
                jwt_payload_handler= api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler= api_settings.JWT_ENCODE_HANDLER
                payload=jwt_payload_handler(oauth_user.user)
                token=jwt_encode_handler(payload)
                response= Response(data={
                    'token':token,
                    'username':username,
                    'user_id':user_id,
                }, status= HTTP_200_OK)
                return response



class OpenIDUserView(CreateAPIView):
    serializer_class = BandOpenIDSerializer
    queryset = OAuthQQUser.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qqauthuser=self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(qqauthuser.user)
        token = jwt_encode_handler(payload)
        response = Response(data={
            'token': token,
            'username': qqauthuser.user.username,
            'user_id': qqauthuser.user.id,
        }, status=HTTP_200_OK)
        return response

    def perform_create(self, serializer):
        user=serializer.save()
        return user




