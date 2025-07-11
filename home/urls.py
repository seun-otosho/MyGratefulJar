from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    # path('about/', views.AboutPageView.as_view(), name='about'),
    path('items/', views.item_list_view, name='item_list'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]
