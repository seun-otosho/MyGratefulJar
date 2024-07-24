# from django.contrib import admin
from django.urls import path, include
from blog import views

urlpatterns = [
    path('', views.blog_index, name='blog_index'),
    path('create/', views.create_blog_post, name='create_blog_post'),
    path('post/<slug:slug>/', views.blog_post, name='blog_post'),
    
    path('add-comment/<int:page_id>/', views.add_comment, name='add_comment'),

    path('post/<slug:slug>/', views.blog_post, name='blog_post'),
    path('post/<slug:slug>/comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),

]
