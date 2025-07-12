# myproject/urls.py
from django.contrib import admin
from django.urls import path, include

from accounts import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Our custom auth views
    path('accounts/login/', views.CustomLoginView.as_view(), name='account_login'),
    path('accounts/signup/', views.CustomSignupView.as_view(), name='account_signup'),

    # Include the rest of Allauth's URLs (for logout, password reset, etc.)
    path('accounts/', include('allauth.urls')),

]