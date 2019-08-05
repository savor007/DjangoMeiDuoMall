from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from goods.models import SKU
from .serializers import OrderSettlementSKUSerializer,OrderSettlementSerializer,SaveOrderSerializer
from django_redis import get_redis_connection
from decimal import Decimal
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
# Create your views here.


class OrderSettlementVIEW(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user=self.request.user
        cart_dict=dict()
        cart_selected_list=list()
        redis_handle=get_redis_connection('carts')
        cart_list_raw = redis_handle.hgetall("Cart_of_userid_%s" % user.id)

        cart_selected_raw = redis_handle.smembers("selected_cart_of_user%s" % user.id)
        for item in cart_selected_raw:
            cart_selected_list.append(int(item.decode()))

        for key, value in cart_list_raw.items():
            fomatted_sku_id=int(key.decode())
            if fomatted_sku_id in cart_selected_list:
                cart_dict[fomatted_sku_id] = value.decode()

        sku_list=SKU.objects.filter(id__in=cart_dict.keys())
        for sku in sku_list:

            sku.count=cart_dict[sku.id]

        myserializer=OrderSettlementSKUSerializer(instance=sku_list, many=True)
        skus_dict=myserializer.data

        return Response(data={"freight": Decimal('10.00'),"skus":skus_dict})


class LaunchedOrder(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = SaveOrderSerializer







