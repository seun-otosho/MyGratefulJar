from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    # path('about/', views.AboutPageView.as_view(), name='about'),
]