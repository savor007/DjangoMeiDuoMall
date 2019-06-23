from rest_framework import serializers
from .models import SKU


class HotSKUSerializer(serializers.ModelSerializer):
    class Meta:
        model=SKU
        fields=['id', 'name', 'price','default_image_url', 'comments']