from django.shortcuts import render
from django.http import HttpResponse
from Backend_Trunk.libs.captcha import captcha
from Backend_Trunk.utils.constants import *
from django.utils.module_loading import import_string
import logging
from django_redis import get_redis_connection
from django.conf import settings
# Create your views here.

logger=logging.getLogger('django')


def Get_Image_Verification_Code(request, image_code_id):
    name, text, image= captcha.captcha.generate_captcha()
    # print(text)
    # print(logger.getEffectiveLevel())
    logger.info("the image verification code is " + text)
    redis_handler=get_redis_connection('verify_codes')
    redis_handler.setex("img_%s" % str(image_code_id), IMAGE_VERIFICATION_CODE_EXPIRY, text )
    return HttpResponse(content=image, content_type="images/jpg")

