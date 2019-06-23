from django.shortcuts import render
from .models import Area
from rest_framework.generics import ListAPIView
from .serializers import AreaSerializer, SubAreaSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin
# Create your views here.


class AreaViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    queryset = Area.objects.filter(parent=None)
    pagination_class = None


    def get_queryset(self):
        if self.action== 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()


    def get_serializer_class(self):
        if self.action=='list':
            return AreaSerializer
        else:
            return SubAreaSerializer


