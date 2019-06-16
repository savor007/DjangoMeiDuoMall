from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from .views import *


urlpatterns={
    url(r'qq/authorization/$',QQAuthURLView.as_view()),
    url(r'qq/user/', OpenIDView.as_view()),         # get method get openid
    url(r'qq/user_oauth/', OpenIDUserView.as_view())      # post method create new oauth user
}