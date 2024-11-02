from .base import *

INSTALLED_APPS += [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]

# AllAuth settings
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# AllAuth settings
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_MIN_LENGTH = 4
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/blog/'
ACCOUNT_LOGOUT_ON_GET = True

MIDDLEWARE += [
    # AllAuth settings
    "allauth.account.middleware.AccountMiddleware"
]


ACCOUNT_FORMS = {
    "signup": "core.forms.CustomSignupForm",
}


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'FETCH_USERINFO' : True
    }
}
