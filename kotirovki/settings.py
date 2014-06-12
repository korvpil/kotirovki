"""
Django settings for kotirovki project.
"""
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
import os

DEBUG = True
TEMPLATE_DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ROOT_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.abspath(os.path.join(ROOT_PATH, os.pardir))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7v329%q+#o%8)n4^6lw@b%qejezpdc^zko*o$(zn_%^ab2f0fn'


DEFAULT_SERVER = '127.0.0.1:8000'
EMAIL_CONFIRMATION_LIFETIME = 86400
RESTORE_PASSWORD_LIFETIME = 86400
CONFIRM_EMAIL_LINK = 'http://' + DEFAULT_SERVER + '/email/activate?code={code}'
RESTORE_PASSWORD_LINK = 'http://' + DEFAULT_SERVER + '/email/restore?code={code}'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = ROOT_PATH + '/media/'
MEDIA_URL = '/media/'

STATIC_ROOT = ROOT_PATH + '/collect_static/'
STATIC_URL = '/static/'

STATICFILES_DIRS = (ROOT_PATH + '/static/',)

TEMPLATE_DIRS = (
    os.path.join('templates')
)

ALLOWED_HOSTS = []
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'korviinn@gmail.com'
EMAIL_HOST_PASSWORD = 'gb521990003'


TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

# Application definition

INSTALLED_APPS = (
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps',
    'south'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'kotirovki.urls'

WSGI_APPLICATION = 'kotirovki.wsgi.application'


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'kotirovki',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'g521990003',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

AUTH_USER_MODEL = 'apps.User'
