from .base import *

DEBUG = False
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", ]
SECRET_KEY = "change me later. .."
try:
    from .local import *
except ImportError:
    pass
