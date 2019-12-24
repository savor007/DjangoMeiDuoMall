from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [

    url(r'orders/settlement/$', views.OrderSettlementVIEW.as_view()),
    url(r'orders/$', views.LaunchedOrder.as_view())

]