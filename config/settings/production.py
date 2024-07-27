from .base import *

DEBUG = False
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = str(os.getenv('SECRET_KEY'))

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["mygratefuljar.com"]
try:
    from .mail import *
except ImportError:
    pass
