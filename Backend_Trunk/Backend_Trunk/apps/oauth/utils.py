from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
from itsdangerous import TimedJSONWebSignatureSerializer as ID_Serializer, BadData
from django.conf import settings
import json
import logging
from Backend_Trunk.utils.constants import *
from Backend_Trunk.utils.Exceptions import QQAPIError
from django.conf import settings
import re
from .models import OAuthQQUser

logger=logging.getLogger('django')


class OAuth():
    def __init__(self, app_id=None, app_key=None, redirect_uri=None, stat=None):
        self.app_id= app_id or settings.QQ_APP_ID
        self.app_key=app_key or settings.QQ_APP_KEY
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URL
        self.state=stat or '/'    #用于保存登陆成功后跳转的页面路径，跳转到到首页


    def get_auth_url(self):
        params={
         'response_type':'code',
         'client_id':self.app_id,
         'redirect_uri':self.redirect_uri,
         'state':self.state,
         'scope':'get_user_info',
        }
        url='https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        return url

    def get_access_token(self, code):
        """"
        get code from QQ
        return access_token
        """
        params = {
            "grant_type": "authorization_code",
            "client_id": self.app_id,
            "client_secret":self.app_key,
            "code":code,
            "redirect_uri":self.redirect_uri,
        }

        url='https://graph.qq.com/oauth2.0/token?'+urlencode(params)
        response=urlopen(url)
        response_str=response.read().decode()
        data=parse_qs(response_str)
        logger.info(str(data))
        access_token=data.get('access_token', None)
        if not access_token:
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            """
            见qq开发文档，接口调用错误时会返回msg和code字段
            """
            raise QQAPIError
        return access_token

    def get_openid(self, access_token):
        """

        :param access_token:
        :return:open_id
        """
        logger.info(str(access_token))
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token[0]
        response = urlopen(url)
        response_str = response.read().decode()
        try:
            """
            response_str的数据格式字符串，example  "callback( {"cliend_id":"YOUR_APPID", "openid":"your openid"} )\n"
            """
            # TODO use Regex match_result=re.match(r'openid:(?P<myopenid>w+)', response_str)
            # TODO print(match_result.myopenid)
            data=json.loads(response_str[10:-4])
        except Exception as error:
            data=parse_qs(response_str)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIError
        openid=data.get('openid', None)
        return openid



    @staticmethod
    def generate_OpenID_Token(openid):
        myserializer=ID_Serializer(settings.SECRET_KEY , expires_in= SAVE_QQ_TOKEN_EXPIRE )
        data={"openid":openid}
        token= myserializer.dumps(data)
        return token.decode()


    @staticmethod
    def release_openid_token(token):
        """

        :param token:包含用户openid
        :return:openid
        """
        myserializer = ID_Serializer(settings.SECRET_KEY , expires_in=SAVE_QQ_TOKEN_EXPIRE)
        try:

            data = myserializer.loads(token)
        except Exception as error:
            logger.error(str(error))
            return None
        else:
            return data.get('openid')




