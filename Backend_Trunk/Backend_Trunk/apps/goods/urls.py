from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [

    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.hotskus.as_view()),
    url(r'^browse_histories/$', views.UserBroswerHistory.as_view()),
    url(r'^categories/(?P<category_id>\d+)/sku', views.GoodsinCategory.as_view()),

]