"""
Django settings for Backend_Trunk project.

Generated by 'django-admin startproject' using Django 1.11.17.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


import sys
import datetime


sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w1ilwh+ebh%u^#v!r(q#s-+3mdh%d^zs3)lnywmjpi!$22s@l*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['api.meiduo.site','www.meiduo.site', '127.0.0.1']

#REMOTE_DATABASE_IPADRRESS = "10.144.157.48"
REMOTE_DATABASE_IPADRRESS = "192.168.210.128"
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'ckeditor',
    'ckeditor_uploader',
    'django_crontab',
    'user.apps.UserConfig',
    'verification.apps.VerificationConfig',
    'oauth.apps.OauthConfig',
    'area.apps.AreaConfig',
    'goods.apps.GoodsConfig',
    'advertisements.apps.AdvertisementsConfig'

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Backend_Trunk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Backend_Trunk.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST':REMOTE_DATABASE_IPADRRESS,
        'PORT':3306,
        'USER':'WinsonSun',
        'PASSWORD':'dalianREN163',
        'NAME':'meiduo_mall'
    }
}

CACHES={
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://"+REMOTE_DATABASE_IPADRRESS+"/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://"+REMOTE_DATABASE_IPADRRESS+"/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "verify_codes": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://"+REMOTE_DATABASE_IPADRRESS+"/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "browser_histroy": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://"+REMOTE_DATABASE_IPADRRESS+"/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), "logs/meiduo.log"),
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
        },
    }
}


REST_FRAMEWORK={
    # EXCEPTION
    'EXCEPTION_HANDLER':'Backend_Trunk.utils.Exceptions.exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES':(
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS':'Backend_Trunk.utils.models.StandardResultSetPagination'
}

JWT_AUTH={
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'user.utils.jwt_response_payload_handler'
}

"""
#Model for Django Authentication System
"""

AUTH_USER_MODEL='user.User'


AUTHENTICATION_BACKENDS=['user.utils.UserNameAndMobileAuthBackend']

CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8080',
    'http://localhost:8000',
    'http://www.meiduo.site:8080',
    'http://api.meiduo.site:8000',
)

CORS_ALLOW_CREDENTIALS =True

QQ_APP_ID='101474184'
QQ_APP_KEY = 'c6ce949e04e12ecc909ae6a8b09b637c'
QQ_REDIRECT_URL = 'http://www.meiduo.site:8080/oauth_callback.html'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25

EMAIL_HOST_USER = 'sunwei_cv@163.com'

EMAIL_HOST_PASSWORD = 'dg200131018'

EMAIL_FROM = 'python<sunwei_cv@163.com>'

REST_FRAMEWORK_EXTENSIONS={
    'DEFAULT_CACHE_RESPONSE_TIMEOUT':60*60*12,
    'DEFAULT_USE_CACHE':'default',
}

CKEDITOR_CONFIGS={
    'default':{
        'toolbar':'full',
        'height':300,
        # 'width':300,
    },
}

CKEDITOR_UPLOAD_PATH=''     #用来设置图片保存路径，使用了FastDF，所以该项设置为空字符
DEFAULT_FILE_STORAGE='Backend_Trunk.utils.FastDFS.FileStorage.FastDFSStorage'
DFS_BASE_URL= 'http://'+REMOTE_DATABASE_IPADRRESS+':8888/'
DFS_CLIENT_CONF=os.path.join(BASE_DIR, 'utils/FastDFS/client.conf')

GENERATED_STATIC_HTML_FILES_DIR= os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'FrondENDMaterials')

TEMPLATES=[
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },

    },
]
CRONJOBS=[('*/5 * * * *', 'advertisements.crons.generate_static_index_html', '>>/Users/sunwei/Documents/Django Practice/DjangoMeiDuoMall/Backend_Trunk/logs/crontab.log')]
CRONTAB_COMMAND_PREFIX='LANG_ALL=zh_cn.UTF-8'


