from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [

    url(r'orders/(?P<order_id>\d+)/payment/$', views.PaymentLink.as_view()),
    url(r'payment/status/?', views.PaymentStatus.as_view())

]