# accounts/urls.py
from django.contrib import admin
from django.urls import path, include

from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),


    # --- OUR CUSTOM ALLAUTH VIEWS ---
    # Login / Signup
    path('accounts/login/', views.CustomLoginView.as_view(), name='account_login'),
    path('accounts/signup/', views.CustomSignupView.as_view(), name='account_signup'),

    # Password Reset Flow
    path('accounts/password/reset/', views.CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('accounts/password/reset/done/', views.CustomPasswordResetDoneView.as_view(), name='account_reset_password_done'),
    # Note: The URL for reset from key includes parameters that Django handles automatically
    path('accounts/password/reset/key/<uidb36>/<key>/', views.CustomPasswordResetFromKeyView.as_view(), name='account_reset_password_from_key'),
    path('accounts/password/reset/key/done/', views.CustomPasswordResetFromKeyDoneView.as_view(), name='account_reset_password_from_key_done'),

    # Password Change (for logged-in users)
    path('accounts/password/change/', views.CustomPasswordChangeView.as_view(), name='account_change_password'),

    # --- DEFAULT ALLAUTH URLS ---
    # This handles all other URLs like logout, email management, social auth, etc.
    # Our custom URLs above will be used instead of the defaults for the ones we defined.
    path('accounts/', include('allauth.urls')),

]