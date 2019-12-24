from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from .views import AreaViewSet
from django.conf.urls import include
from rest_framework.routers import DefaultRouter


urlpatterns=[]
router=DefaultRouter()
router.register(prefix=r'areas', viewset=AreaViewSet, base_name='AreaQuiryRelated')

# urlpatterns=[       # get method get openid
#     url(r'', include(router.urls)),
# ]


urlpatterns+=router.urls