from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.status import *
from .serializers import CartSerializer, CartGetSerializer ,CartDelSerializer
from django_redis import get_redis_connection
from rest_framework.response import Response
import logging
import base64
import pickle
from goods.models import SKU

logger=logging.getLogger('django')

# Create your views here.
class Cart(APIView):

    def perform_authentication(self, request):
        pass

    def get(self, request):
        """

        :param request:
        :return:
        """
        """
        判断客户是否登陆
        """
        cart_list = dict()
        selected_cart_list = set()
        sku_list=[]
        try:
            user=self.request.user
        except Exception:
            user =None

        if user and user.is_authenticated:
            """
            用户已经登陆，从redis中取购物车数据
            """
            redis_handle = get_redis_connection('carts')
            cart_list=redis_handle.hgetall("Cart_of_userid_%s" % user.id)
            selected_cart_list=redis_handle.smembers("selected_cart_of_user%s" % user.id)

            for sku_id, count in cart_list.items():
                sku=SKU.objects.get(id=int(sku_id.decode()))
                sku.count=int(count.decode())
                sku.selected=sku_id in selected_cart_list
                sku_list.append(sku)

        else:
            """
            用户没有登陆，从cookies中取数据
            """
            cookie = self.request.COOKIES
            logger.info(str(cookie))
            cookie_cart_str = cookie.get('cart')
            if cookie_cart_str:
                cart_info_cookie = pickle.loads(base64.b64decode(cookie_cart_str.encode()))
                logger.info(str(cart_info_cookie))
                for sku_id, detail in cart_info_cookie.items():
                    sku = SKU.objects.get(id=sku_id)
                    sku.count = int(detail.get('count'))
                    sku.selected = detail.get('selected')
                    sku_list.append(sku)


        logger.info(str(sku_list))
        myserializer= CartGetSerializer(instance=sku_list, many=True)
        logger.info(str(myserializer.data))
        return Response(data=myserializer.data, status=HTTP_200_OK)




    def post(self, request):
        myserializer=CartSerializer(data=request.data)
        myserializer.is_valid(raise_exception=True)

        sku_id=myserializer.validated_data.get('sku_id')
        count=myserializer.validated_data.get('count')
        select=myserializer.validated_data.get('selected')
        response=Response(data= myserializer.validated_data)
        try:
            user = self.request.user
        except Exception:
            user=None

        if user and user.is_authenticated:
            """
            客户已经登陆， 将购物车数据放到redis
            """
            redis_handle=get_redis_connection('carts')
            redis_pl=redis_handle.pipeline()
            redis_pl.hincrby("Cart_of_userid_%s" % user.id, sku_id, count)
            if select:
                redis_pl.sadd("selected_cart_of_user%s" % user.id, sku_id)
            redis_pl.execute()
            return response

        else:
            cookie=self.request.COOKIES
            logger.info(str(cookie))
            cookie_cart_str=cookie.get('cart')
            if cookie_cart_str:
                cart_info_cookie=pickle.loads(base64.b64decode(cookie_cart_str.encode()))
                logger.info(str(cart_info_cookie))
                if sku_id in cart_info_cookie.keys():
                    orginal_count=int(cart_info_cookie[sku_id]['count'])
                    cart_info_cookie[sku_id]['count']=orginal_count+ count
                    cart_info_cookie[sku_id]['selected']=select
                else:
                    cart_info_cookie[sku_id] = {"count": count, "selected": select}
            else:
                cart_info_cookie=dict()
                cart_info_cookie[sku_id]={"count":count,"selected":select}

            logger.info(str(cart_info_cookie))
            cookie_cart_str=base64.b64encode(pickle.dumps(cart_info_cookie)).decode()
            response.set_cookie(key='cart',value=cookie_cart_str)
            logger.info(cookie_cart_str)
            return response


    def put(self,request):
        myserializer = CartSerializer(data=request.data)
        myserializer.is_valid(raise_exception=True)

        sku_id = myserializer.validated_data.get('sku_id')
        count = myserializer.validated_data.get('count')
        select = myserializer.validated_data.get('selected')
        response = Response(data=myserializer.validated_data)
        try:
            user = self.request.user
        except Exception:
            user=None

        if user and user.is_authenticated:
            """
            客户已经登陆， 将购物车数据放到redis
            """
            redis_handle=get_redis_connection('carts')
            redis_pl=redis_handle.pipeline()
            redis_pl.hset("Cart_of_userid_%s" % user.id, sku_id, count)
            if select:
                redis_pl.sadd("selected_cart_of_user%s" % user.id, sku_id)
            else:
                redis_pl.srem("selected_cart_of_user%s" % user.id, sku_id)
            redis_pl.execute()
            return response

        else:
            cookie=self.request.COOKIES
            logger.info(str(cookie))
            cookie_cart_str=cookie.get('cart')
            if cookie_cart_str:
                cart_info_cookie=pickle.loads(base64.b64decode(cookie_cart_str.encode()))
                logger.info(str(cart_info_cookie))
                if sku_id in cart_info_cookie.keys():
                    cart_info_cookie[sku_id]['count']=count
                    cart_info_cookie[sku_id]['selected']=select
                else:
                    cart_info_cookie[sku_id] = {"count": count, "selected": select}
            else:
                cart_info_cookie=dict()
                cart_info_cookie[sku_id]={"count":count,"selected":select}

            logger.info(str(cart_info_cookie))
            cookie_cart_str=base64.b64encode(pickle.dumps(cart_info_cookie)).decode()
            response.set_cookie(key='cart',value=cookie_cart_str)
            logger.info(cookie_cart_str)
            return response


    def delete(self, request):
        myserializer=CartDelSerializer(data=request.data)
        myserializer.is_valid(raise_exception= True)
        sku_id = myserializer.validated_data.get('sku_id')
        response = Response(status=HTTP_204_NO_CONTENT)
        try:
            user = self.request.user
        except Exception:
            user = None

        if user and user.is_authenticated:
            """
            客户已经登陆， 将购物车数据放到redis
            """
            redis_handle = get_redis_connection('carts')
            redis_pl = redis_handle.pipeline()
            redis_pl.hdel("Cart_of_userid_%s" % user.id, sku_id)
            redis_pl.srem("selected_cart_of_user%s" % user.id, sku_id)
            redis_pl.execute()
            return response

        else:
            cookie = self.request.COOKIES
            logger.info(str(cookie))
            cookie_cart_str = cookie.get('cart')
            if cookie_cart_str:
                cart_info_cookie = pickle.loads(base64.b64decode(cookie_cart_str.encode()))
                logger.info(str(cart_info_cookie))
                if sku_id in cart_info_cookie.keys():
                    del cart_info_cookie[sku_id]

            logger.info(str(cart_info_cookie))
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_info_cookie)).decode()
            response.set_cookie(key='cart', value=cookie_cart_str)
            logger.info(cookie_cart_str)
            return response

