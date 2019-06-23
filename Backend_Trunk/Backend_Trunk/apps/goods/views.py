from django.shortcuts import render
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from .models import SKU
from Backend_Trunk.utils.constants import HOT_SKU_COUNT, USER_BROWSER_HISTORY_COUNT
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from .serializers import HotSKUSerializer
from django_redis import get_redis_connection
# Create your views here.
import logging

logger=logging.getLogger('django')

class hotskus(ListCacheResponseMixin, ListAPIView):

    serializer_class = HotSKUSerializer
    pagination_class = None


    def get_queryset(self):
        category_id= self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:HOT_SKU_COUNT]



class UserBroswerHistory(APIView):
    permissions = [IsAuthenticated]

    def post(self, request):
        sku_id=self.request.data.get('sku_id')
        user_id=self.request.user.id

        try:
            sku=SKU.objects.get(id=sku_id)
        except Exception as error:
            logger.error("商品不存在")
            return Response(data={
                "message": "商品不存在"
            },status=HTTP_404_NOT_FOUND)

        redis_handle= get_redis_connection("browser_histroy")
        history_list=redis_handle.lrange("history_"+str(user_id),0, USER_BROWSER_HISTORY_COUNT)
        if len(history_list)==0 or sku_id not in history_list:
           redis_handle.lpush("history_"+str(user_id),sku_id)
           redis_handle.ltrim("history_"+str(user_id),0,USER_BROWSER_HISTORY_COUNT )
        return Response(data={
            "sku_id":sku_id
        }, status=HTTP_201_CREATED)


    def get(self, request):
        user_id=self.request.user.id
        redis_handle=get_redis_connection('browser_histroy')
        history_list = redis_handle.lrange("history_" + str(user_id), 0, USER_BROWSER_HISTORY_COUNT)
        myserilizer=HotSKUSerializer(instance=SKU.objects.filter(id__in=history_list,is_launched=True), many=True)
        return Response(data=myserilizer.data)


class GoodsinCategory(ListAPIView):
    """
    REST Framework 提供了对排序的支持， 使用rest frame提供的OrderingFilter过滤器后端， orderingfilter过滤器要使用ordering_fields
    属性来指明可以进行排序的字段有哪些
    """
    serializer_class = HotSKUSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields=('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id, is_launched=True)






