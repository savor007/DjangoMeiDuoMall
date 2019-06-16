from rest_framework.views import exception_handler as drf_exception_handler
import logging
from django.db import DatabaseError
from redis.exceptions import RedisError
from rest_framework.response import Response
from rest_framework import status




#get the logger defined in the settings
logger=logging.getLogger('django')


def exception_handler(exc , context):
    """
    customize the exceptions
    :param exc:  exception
    :param context:
    :return:  Response
    """

    response= drf_exception_handler(exc, context)
    if response is None:
        view=context['view']
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            logger.error('[%s] %s' % (view, exc))
            response=Response({'message':'database or redis error'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

    return response


def QQAPIError(BaseException):
    pass