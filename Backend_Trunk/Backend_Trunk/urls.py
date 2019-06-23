"""Backend_Trunk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from Backend_Trunk.apps.verification.views import *
from Backend_Trunk.apps.verification.drf_views import *


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^image_codes/(?P<image_code_id>.+)/$', Get_Image_Verification_Code),
    url(r'^sms_codes/(?P<mobile>1[35678][0-9]{9})/', Get_SMS_Verification_Code.as_view()),
    url(r'^', include('user.urls')),
    url(r'^oauth/', include('oauth.urls')),
    url(r'', include('area.urls')),
    url(r'', include('goods.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
]
