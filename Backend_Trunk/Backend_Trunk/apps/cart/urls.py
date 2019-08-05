from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [

    url(r'cart/$', views.Cart.as_view()),

]