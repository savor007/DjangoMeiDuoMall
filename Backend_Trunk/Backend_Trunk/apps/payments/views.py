from django.shortcuts import render
import os
from alipay import AliPay
from django.conf import settings
from orders.models import OrderGoods, OrderInfo
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import *
from django.utils import timezone
from datetime import datetime, timedelta
import logging
from .models import Payment
# Create your views here.

logger=logging.getLogger('django')
alipay_actor=AliPay(
            appid= settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"RSA_Keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"RSA_Keys/alipay_public_key.pem"),
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG,
            )

class PaymentLink(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, order_id):
        user=request.user
        try:
            order= OrderInfo.objects.get(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"], user=user)
        except Exception as error:
            logger.info(("order id %s" % order_id) + "can not be found" )
            return Response(data={'message':'查找不到相应的订单信息'})

        """
        ALIPAY_APPID='2016101100662391'
        ALIPAY_URL='https://openapi.alipaydev.com/gateway.do?'
        ALIPAY_DEBUG=True
        """
        order_string=alipay_actor.api_alipay_trade_page_pay(
            out_trade_no= order_id,
            total_amount=str(order.total_amount),
            subject="美多商城 order id " +order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
            body="the user name is "+user.username,
            time_express='25h',

        )
        alipay_str= settings.ALIPAY_URL+order_string
        return Response(data={'alipay_url': alipay_str}, status= HTTP_200_OK)



class PaymentStatus(APIView):
    def put(self, request):
        requery_dict=request.query_params
        parameters_dict=requery_dict.dict()
        order_id=parameters_dict.get('out_trade_no')
        trade_id=parameters_dict.get('trade_no')
        if order_id==None or trade_id==None:
            """
            没有找到查询参数
            """
            return Response(data={'message':'参数错误'}, status= HTTP_400_BAD_REQUEST)
        try:
            order=OrderInfo.objects.get(order_id=order_id)
        except Exception as error:
            logger.error('order id %s 找不到对应订单信息' % order_id)
            return Response(data={'message': '参数错误'}, status=HTTP_400_BAD_REQUEST)

        signature=parameters_dict.pop('sign')
        logger.info(str(parameters_dict))
        if alipay_actor.verify(parameters_dict,signature):
            """
            使用支付宝公钥解密正确, 保存支付信息到payment数据库表中
            """
            Payment.objects.create(order=order,trade_id=trade_id)
            """
            更新order数据表，update到已经付款的状态
            """
            order.status=OrderInfo.ORDER_STATUS_ENUM["UNSEND"]
            order.save()
            return Response(data={'trade_id': trade_id}, status=HTTP_202_ACCEPTED)
        else:
            return Response(data={'message': '参数校验错误'}, status=HTTP_400_BAD_REQUEST)





