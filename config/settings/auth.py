from .base import *

INSTALLED_APPS += [
    # Allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount', # Optional, for social logins
]

MIDDLEWARE += [
    "allauth.account.middleware.AccountMiddleware"
]


# Required for Allauth
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Required for Allauth
SITE_ID = 1

# Allauth settings (redirects)
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Optional: Configure Allauth to use email for login, require email, etc.
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'optional' # Change to 'mandatory' for production
