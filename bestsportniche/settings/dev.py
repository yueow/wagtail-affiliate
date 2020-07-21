import os
from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = (os.environ.get('DEBUG_VALUE') == "True")

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'q9x0npzk@#e4hfy)0h$ix*=bl$lh2pq&zf_t0e0a#+z#^=d=t('
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: define the correct hosts in production!
# ALLOWED_HOSTS = ['*'] 
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'herokuapp', 'aws-service'] 

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *
except ImportError:
    pass
