from rest_framework import serializers


from django_redis import get_redis_connection
from redis.exceptions import RedisError
import logging

logger=logging.getLogger('django')
class ImageCodeSerializer(serializers.Serializer):
    """
    verify the image code
    60 seconds expiry
    """
    image_code_id=serializers.UUIDField()
    text=serializers.CharField(max_length=4, min_length=4)


    def validate(self, attrs):
        """
        validation
        :param attrs:
        :return:
        """
        image_code_id= attrs.get('image_code_id')
        received_verification_code= attrs.get('text')
        redis_handle=get_redis_connection("verify_codes")
        real_verification_code= redis_handle.get('img_'+str(image_code_id))
        print('img_'+str(image_code_id))
        if real_verification_code is None:
            raise serializers.ValidationError('image verication code expiried or does not exist')

        try:
            redis_handle.delete('img_'+str(image_code_id))
        except RedisError as error:
            logger.error(error)

        real_verification_str= real_verification_code.decode()
        if real_verification_str.lower()!= received_verification_code.lower():
            raise serializers.ValidationError('the input image code is wrong')
        """
        check the last time of this mobile number reqeust sms code
        """
        mobile= self.context['view'].kwargs.get('mobile',None)
        if mobile:
            send_flag= redis_handle.get("send_flag_"+ mobile)
            if send_flag:
                raise serializers.ValidationError('too frequent for sms code request from mobile: '+ mobile)


        return attrs