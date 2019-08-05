from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU
from .models import OrderInfo, OrderGoods
from django.db import transaction
from decimal import Decimal
import logging


logger=logging.getLogger('django')

class OrderSettlementSKUSerializer(serializers.ModelSerializer):
    count=serializers.IntegerField(min_value= True, read_only=True)
    class Meta:
        model=SKU
        fields=['id', 'name', 'default_image_url','price','count']


class OrderSettlementSerializer(serializers.Serializer):
    freight=serializers.DecimalField(label="运费", max_digits=10, decimal_places=2)
    skus=OrderSettlementSKUSerializer(many=True)


class SaveOrderSerializer(serializers.ModelSerializer):
    address=serializers.IntegerField(write_only=True)
    pay_method=serializers.IntegerField(write_only=True)

    class Meta:
        model=OrderInfo
        fields=['order_id','address', 'pay_method']
        extra_kwargs={
            'order_id':{'read_only':True}
        }
    def validate(self, attrs):
        user=self.context.get('request').user
        try:
            address=user.addresses.get(id=(attrs['address']))
        except Exception as error:
            raise serializers.ValidationError("找不到相应收货地址")
        if attrs['pay_method'] not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            raise serializers.ValidationError("找不到对应的付款方式")
        return attrs



    def create(self, validated_data):
        """

        :param validated_data:
        :return:
        """
        user = self.context.get('request').user
        address_id=validated_data.get('address')
        pay_method=validated_data.get('pay_method')
        """
        获取登陆user信息和参数
        """
        cart_dict = dict()
        cart_selected_list = list()
        redis_handle = get_redis_connection('carts')
        cart_list_raw = redis_handle.hgetall("Cart_of_userid_%s" % user.id)
        sku_list=list()
        cart_selected_raw = redis_handle.smembers("selected_cart_of_user%s" % user.id)
        for item in cart_selected_raw:
            cart_selected_list.append(int(item.decode()))

        for key, value in cart_list_raw.items():
            fomatted_sku_id = int(key.decode())
            if fomatted_sku_id in cart_selected_list:
                cart_dict[fomatted_sku_id] = value.decode()


        total_price_amout=Decimal('0.00')
        total_count=0
        """
        获取购物车信息
        """
        with transaction.atomic():
            order_id = timezone.now().strftime("%Y%m%d%H%M%S") + ("%09d" % user.id)
            save_id=transaction.savepoint()
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address_id=validated_data['address'],
                freight=Decimal('10.00'),
                status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if validated_data['pay_method'] ==
                                                                OrderInfo.PAY_METHODS_ENUM['CASH'] else
                OrderInfo.ORDER_STATUS_ENUM["UNPAID"],
                total_count=total_count,
                total_amount=total_price_amout,
                pay_method=validated_data['pay_method']
            )
            try:
                sku_list = SKU.objects.filter(id__in=cart_dict.keys())
                for sku_item in sku_list:
                    while True:
                        sku=SKU.objects.get(id=sku_item.id)
                        count= int(cart_dict[sku.id])
                        original_stock=sku.stock
                        original_sales=sku.sales
                        if original_stock < count:
                            transaction.savepoint_rollback(save_id)
                            raise serializers.ValidationError(detail={'detail':"库存商品不足"})
                        else:
                            new_stock=original_stock-count
                            new_sales=original_sales+count
                            """
                            再次查询，确保余量小于count
                            """
                            result=SKU.objects.filter(id=sku.id, stock=original_stock).update(stock=new_stock, sales=new_sales)
                            if result==0:
                                """
                                表示没有记录被修改成功
                                """
                                continue
                            else:
                                sku.goods.sales+=count
                                sku.goods.save()
                                total_count+=count
                                total_price_amout=sku.price*count
                                OrderGoods.objects.create(
                                    order=order,
                                    sku=sku,
                                    count=count,
                                    price=sku.price,
                                )
                                break
                order.total_amount=total_price_amout
                order.total_amount+=order.freight
                order.total_count=total_count
                order.save()
                pl = redis_handle.pipeline()
                pl.hdel("Cart_of_userid_%s" % user.id, *cart_dict.keys())
                pl.srem("selected_cart_of_user%s" % user.id, *cart_dict.keys())
                pl.execute()
            except serializers.ValidationError as error:
                raise serializers.ValidationError(detail={'detail':'库存商品不足'})
            except Exception as error:
                logger.error(error)
                transaction.savepoint_rollback(save_id)
                raise serializers.ValidationError({"detail":error})
            """
            如果没有问题，则提交订单
            """
            transaction.savepoint_commit(save_id)
            """
            更新redis数据库中的数据
            """

            return order






