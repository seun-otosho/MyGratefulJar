from django.contrib import admin
from django.urls import path, include
from blog import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),
    path('create/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:post_pk>/comment/<int:comment_pk>/reply/', views.add_comment_to_comment, name='add_comment_to_comment'),
    
]
