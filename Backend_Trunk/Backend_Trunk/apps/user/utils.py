from .models import User
from django.contrib.auth.backends import ModelBackend
import re
import logging
logger=logging.getLogger('django')

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token':token,
        'user_id':user.id,
        'username':user.username
    }


def get_user_by_account(account):
    """

    :param account:
    :return User object:
    """

    """
    不能使用filter因为filter查出来的是queryset，而不是对象
    """

    try:
        if re.match(r'^1[3456789]\d{9}$', account):
            user=User.objects.get(mobile=account)
        else:
            user=User.objects.get(username=account)
    except Exception as error:
        logger.info('user doesnot exist')
        return None
    else:
        return user


class UserNameAndMobileAuthBackend(ModelBackend):
    """
    customize mobile and username authentication
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user=get_user_by_account(username)
        print(user)
        if user and user.check_password(password):
            return user
        else:
            return None

