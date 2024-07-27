import os
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# EMAIL_HOST = "mail.gmail.com"
# EMAIL_PORT = 587
# EMAIL_HOST_USER = "omniotosho@gmail.com"

EMAIL_USE_TLS = True

EMAIL_HOST = "mail.mygratefuljar.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "share@mygratefuljar.com"

EMAIL_HOST_PASSWORD = str(os.getenv('EMAIL_HOST_PASSWORD'))
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
