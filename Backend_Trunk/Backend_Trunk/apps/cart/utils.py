import pickle
import base64
from django_redis import get_redis_connection
from rest_framework.response import Response
import logging


logger=logging.getLogger('django')


def Merge_Cookie_Cart(user_id:int, request, response):
    """
    合并后，要删除cookie，所以要传入response，将respone中的cookie删除
    :param user_id:
    :param request:
    :param respone:
    :return:
    """
    cookie = request.COOKIES
    logger.info(str(cookie))
    cookie_cart_str = cookie.get('cart')
    if cookie_cart_str:
        cart_info_cookie = pickle.loads(base64.b64decode(cookie_cart_str.encode()))
        logger.info(str(cart_info_cookie))
        redis_handle = get_redis_connection('carts')
        cart_list=dict()
        cart_list_raw = redis_handle.hgetall("Cart_of_userid_%s" % user_id)
        for key, value in cart_list_raw.items():
            cart_list[int(key.decode())]=value.decode()
        logger.info(str(cart_list))
        for sku_id, detail in cart_info_cookie.items():
            count=detail.get('count')
            selected=detail.get('selected')


            if sku_id not in cart_list.keys():
                redis_handle.hincrby("Cart_of_userid_%s" % user_id, sku_id, count)
            else:
                redis_handle.hset("Cart_of_userid_%s" % user_id, sku_id, count)
            if selected:
                redis_handle.sadd("selected_cart_of_user%s" % user_id, sku_id)


        response.delete_cookie('cart')
        return response
    else:
        return response
