from django.urls import path

from . import views

# app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('base/', views.base, name='base'),

    path('welcome/', views.welcome, name='welcome'),

    path('items/', views.item_list_view, name='item_list'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]
