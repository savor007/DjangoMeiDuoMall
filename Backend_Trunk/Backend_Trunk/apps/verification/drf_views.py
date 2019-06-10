
from rest_framework.generics import GenericAPIView
from .serializers import ImageCodeSerializer
from rest_framework.response import Response
from django_redis import get_redis_connection
from Backend_Trunk.libs.yuntongxun import sms
from Backend_Trunk.utils.constants import SMS_CODE_EXPIRY, MOBILE_REQUEST_EXPRIRY
from rest_framework.status import *
import logging
import random
from celery_tasks.sms.tasks import send_sms_code

logger=logging.getLogger('django')


class Get_SMS_Verification_Code(GenericAPIView):
    serializer_class = ImageCodeSerializer
    def get(self, request, mobile):

        verify_serializer= self.get_serializer(data=request.query_params)
        """
            def get_serializer(self, *args, **kwargs):
        """
        # Return the serializer instance that should be used for validating and
        # deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)
        """
        """
         def get_serializer_context(self):
        """
        # Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }
        """
        """
        GenericAPIVIEW=>APIVIEW=>base.VIEW, base VIEW has property of kwargs, so GenerericAPIVIEW have kwargs
        """
        try:
            verify_serializer.is_valid(raise_exception=True)
        except Exception as err:
            Response(status=HTTP_404_NOT_FOUND, data=str(err))
        """
        view function will stop and exception will be handled by exception handler
        """
        sms_code= "%06d" % random.randint(0, 999999)
        logger.info("sms verfication code is "+  sms_code )
        # SMS_Sender=sms.CCP()
        # sms_result=-1
        # sms_result= SMS_Sender.send_template_sms(mobile, [sms_code, SMS_CODE_EXPIRY/60] ,1)
        # if sms_result!=0:
        #     return Response(status=HTTP_500_INTERNAL_SERVER_ERROR, data='can not send sms code!')

        send_sms_code.delay(mobile, sms_code)
        """

        save sms code into redis
        """
        redis_handle=get_redis_connection('verify_codes')
        redis_pipeline= redis_handle.pipeline()
        redis_pipeline.multi()
        redis_pipeline.setex("send_flag_"+ mobile, MOBILE_REQUEST_EXPRIRY, 1 )
        redis_pipeline.setex("sms_verification_code_for_"+mobile,SMS_CODE_EXPIRY, sms_code)

        redis_pipeline.execute()

        return Response(status=HTTP_200_OK, data={"messsage":"OK"})








