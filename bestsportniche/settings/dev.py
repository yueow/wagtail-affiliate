import os
from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': os.environ('DJANGO_DB_NAME'),
#        'USER': os.environ('DJANGO_DB_USER'),
#        'PASSWORD': os.environ('DJANGO_DB_PASSWORD'),
#        'HOST': os.environ('DJANGO_DB_HOST'),
#        'PORT': '',
}

DEBUG = True
# DEBUG = (os.environ('DEBUG_VALUE') == "True")

SECRET_KEY = 'q9x0npzk@#e4hfy)0h$ix*=bl$lh2pq&zf_t0e0a#+z#^=d=t('
# SECRET_KEY = os.environ('SECRET_KEY')

ALLOWED_HOSTS = ['*']
#ALLOWED_HOSTS = ['3.120.191.123', 'localhost', '127.0.0.1']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *
except ImportError:
    pass
