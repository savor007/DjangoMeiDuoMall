from rest_framework import serializers
from goods.models import SKU




class CartSerializer(serializers.Serializer):
    sku_id=serializers.IntegerField(min_value=1)
    count=serializers.IntegerField(min_value=1)
    selected=serializers.BooleanField()


    def validate(self, attrs):
        sku_id=attrs['sku_id']
        count=attrs['count']
        select=attrs['selected']
        try:
            sku= SKU.objects.get(id=sku_id)
        except Exception as error:
            raise serializers.ValidationError("查询不到指定产品")
        if sku.stock<count:
            raise serializers.ValidationError("产品余量不足")
        return attrs



class CartGetSerializer(serializers.ModelSerializer):
    count=serializers.IntegerField(min_value=1)
    selected=serializers.BooleanField()


    class Meta:
        model=SKU
        fields=('id', 'count', 'selected', 'name','default_image_url', 'price')



class CartDelSerializer(serializers.Serializer):
    sku_id=serializers.IntegerField(min_value=1,required= True)

    def validate(self, attrs):
        sku_id=attrs['sku_id']

        try:
            sku= SKU.objects.get(id=sku_id)
        except Exception as error:
            raise serializers.ValidationError("查询不到指定产品")
        return attrs
