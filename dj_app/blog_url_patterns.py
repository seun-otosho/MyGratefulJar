from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('contact/', views.contact_view, name='contact'),
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Post detail
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    
    # Category and tag pages
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category'),
    path('tag/<slug:slug>/', views.TagDetailView.as_view(), name='tag'),
    
    # AJAX endpoints
    path('ajax/comment/<slug:post_slug>/', views.submit_comment, name='submit_comment'),
    path('ajax/newsletter/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # API endpoints
    path('api/homepage/', views.get_homepage_data, name='api_homepage'),
    path('api/blog/', views.get_blog_listing_data, name='api_blog_listing'),
    path('api/post/<slug:slug>/', views.get_post_data, name='api_post_data'),
    path('api/search/', views.search_posts, name='api_search'),
]
