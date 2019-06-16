from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [

    url(r'^username/(?P<username>\w{5,23})/count/$', views.UserAccount_UserName.as_view()),
    url(r'^mobile/(?P<mobile>1[35678][0-9]{9})/count/$', views.UserAccount_Mobile.as_view()),
    url(r'^users/$', views.UserData.as_view()),

    # JWT默认的视图函（obtain jwt token）只是返回token，但是我们需要username和userid
    # 在utils中重新定义，并在setting中进行配置, 根据官方文档， obtain jwt token也是通过username和passpord对用户身份进行确认
    url(r'^authorizations/$',view=obtain_jwt_token, name='authorizations' ),
    url(r'^accounts/(?P<account>\w{5,20})/sms/token/',views.SMSCodeTokenView.as_view()),
    url(r'^sms_codes/', views.SMS_Verifcation_ByToken.as_view()),
    url(r'^accounts/(?P<account>\w{5,20})/password/token/', views.Password_Token.as_view()),
    url(r'^users/(?P<pk>\d+)/password/$', views.PasswordVIEW.as_view()),
    url(r'^user_info/$', views.UserInfoView.as_view())
]