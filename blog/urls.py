from django.urls import path

from blog import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog, name='blog'),

    path('post/<int:post_id>', views.post, name='post'),
    #
    # path('items/', views.item_list_view, name='item_list'),
    # path('about/', views.about_view, name='about'),
    # path('contact/', views.contact_view, name='contact'),
]
