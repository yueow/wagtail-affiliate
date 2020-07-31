import os
from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'bsp_db',
#        'USER': 'bsp_admin',
#        'PASSWORD': 'rjKfSm2341',
#        'HOST': 'localhost',
#        'PORT': '',
#    }
}

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
#        'LOCATION': '/tmp/memcached.sock',
#    }
#}


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
