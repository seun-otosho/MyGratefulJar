from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, F
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.db import transaction
import json

from .models import (
    Post, Category, Tag, Comment, ContactSubmission, 
    NewsletterSubscriber, User
)
from .forms import (
    ContactForm, CommentForm, NewsletterForm, 
    PostSearchForm, PostFilterForm
)


class HomeView(ListView):
    """Homepage view with featured posts and latest posts"""
    
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    
    def get_queryset(self):
        return Post.objects.filter(
            status=Post.PostStatus.PUBLISHED,
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags')[:6]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured posts for hero slider
        context['featured_posts'] = Post.objects.filter(
            status=Post.PostStatus.PUBLISHED,
            is_featured=True,
            published_at__lte=timezone.now()
        ).select_related('author', 'category')[:3]
        
        # Latest posts
        context['latest_posts'] = Post.objects.filter(
            status=Post.PostStatus.PUBLISHED,
            published_at__lte=timezone.now()
        ).select_related('author', 'category')[:6]
        
        # Popular posts
        context['popular_posts'] = Post.objects.filter(
            status=Post.PostStatus.PUBLISHED,
            published_at__lte=timezone.now()
        ).select_related('author', 'category').order_by('-view_count')[:4]
        
        # Categories
        context['categories'] = Category.objects.filter(
            is_active=True
        ).annotate(
            published_post_count=Count('posts', filter=Q(posts__status=Post.PostStatus.PUBLISHED))
        ).order_by('name')
        
        return context


class BlogListView(ListView):
    """Blog listing page with pagination and filtering"""
    
    model = Post
    template_name = 'blog/blog.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Post.objects.filter(
            status=Post.PostStatus.PUBLISHED,
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags')
        
        # Apply filters
        category_slug = self.request.GET.get('category')
        tag_slug = self.request.GET.get('tag')
        sort_by = self.request.GET.get('sort_by', 'latest')
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Apply sorting
        if sort_by == 'oldest':
            queryset = queryset.order_by('published_at')
        elif sort_by == 'popular':
            queryset = queryset.order_by('-view_count')
        elif sort_by == 'commented':
            queryset = queryset.order_by('-comment_count')
        else:  # latest
            queryset = queryset.order_by('-published_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter form
        context['filter_form'] = PostFilterForm(self.request.GET)
        
        # Add categories and tags
        context['categories'] = Category.objects.filter(is_active=True)
        context['tags'] = Tag.objects.all()
        
        # Add current filters
        context['current_category'] = self.request.GET.get('category')
        context['current_tag'] = self.request.GET.get('tag')
        context['current_sort'] = self.request.GET.get('sort_by', 'latest')
        
        return context


class PostDetailView(DetailView):
    """Individual post detail view"""
    
    model = Post
    template_name = 'blog/single.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(
            status=Post.PostStatus.PUBLISHED,
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Increment view count
        obj.increment_view_count()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add comments
        context['comments'] = Comment.objects.filter(
            post=self.object,
            status=Comment.CommentStatus.APPROVED,
            parent=None
        ).select_related('user').prefetch_related('replies')
        
        # Add comment form
        context['comment_form'] = CommentForm(user=self.request.user)
        
        # Add related posts
        context['related_posts'] = Post.objects.filter(
            status=Post.PostStatus.PUBLISHED,
            published_at__lte=timezone.now(),
            category=self.object.category
        ).exclude(id=self.object.id).select_related('author', 'category')[:3]
        
        return context


class CategoryDetailView(ListView):
    """Category detail view showing posts in a category"""
    
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(
            status=Post.PostStatus.PUBLISHED,
            published_at__lte=timezone.now(),
            category=self.category
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagDetailView(ListView):
    """Tag detail view showing posts with a specific tag"""
    
    model = Post
    template_name = 'blog/tag.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(
            status=Post.PostStatus.PUBLISHED,
            published_at__lte=timezone.now(),
            tags=self.tag
        ).select_related('author', 'category').prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class SearchView(ListView):
    """Search view for posts"""
    
    model = Post
    template_name = 'blog/search.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        
        if not query:
            return Post.objects.none()
        
        # Use PostgreSQL full-text search
        search_vector = SearchVector('title', weight='A') + SearchVector('excerpt', weight='B') + SearchVector('content', weight='C')
        search_query = SearchQuery(query)
        
        return Post.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(
            search=search_query,
            status=Post.PostStatus.PUBLISHED,
            published_at__lte=timezone.now()
        ).select_related('author', 'category').prefetch_related('tags').order_by('-rank')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['search_form'] = PostSearchForm(self.request.GET)
        return context


def contact_view(request):
    """Contact form view"""
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            # Add IP address and user agent
            contact.ip_address = request.META.get('REMOTE_ADDR')
            contact.user_agent = request.META.get('HTTP_USER_AGENT', '')
            contact.save()
            
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('blog:contact')
    else:
        form = ContactForm()
    
    return render(request, 'blog/contact.html', {'form': form})


@require_POST
def submit_comment(request, post_slug):
    """Submit comment via AJAX"""
    
    post = get_object_or_404(Post, slug=post_slug, status=Post.PostStatus.PUBLISHED)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, user=request.user)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.ip_address = request.META.get('REMOTE_ADDR')
            comment.user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Handle parent comment for replies
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent = Comment.objects.get(id=parent_id, post=post)
                    comment.parent = parent
                except Comment.DoesNotExist:
                    pass
            
            comment.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Comment submitted successfully! It will be visible after approval.',
                    'comment_id': str(comment.id)
                })
            else:
                messages.success(request, 'Comment submitted successfully! It will be visible after approval.')
                return redirect('blog:post_detail', slug=post_slug)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })
    else:
        messages.error(request, 'There was an error submitting your comment.')
        return redirect('blog:post_detail', slug=post_slug)


@require_POST
def newsletter_subscribe(request):
    """Newsletter subscription via AJAX"""
    
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            subscriber = form.save(commit=False)
            subscriber.source = request.POST.get('source', 'footer_form')
            subscriber.ip_address = request.META.get('REMOTE_ADDR')
            subscriber.user_agent = request.META.get('HTTP_USER_AGENT', '')
            subscriber.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for subscribing to our newsletter!'
                })
            else:
                messages.success(request, 'Thank you for subscribing to our newsletter!')
                return redirect('blog:home')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })
    else:
        messages.error(request, 'There was an error subscribing to the newsletter.')
        return redirect('blog:home')


def get_homepage_data(request):
    """API endpoint for homepage data"""
    
    # Featured posts
    featured_posts = Post.objects.filter(
        status=Post.PostStatus.PUBLISHED,
        is_featured=True,
        published_at__lte=timezone.now()
    ).select_related('author', 'category').values(
        'id', 'title', 'slug', 'excerpt', 'featured_image_url', 
        'published_at', 'author__display_name', 'category__name'
    )[:3]
    
    # Latest posts
    latest_posts = Post.objects.filter(
        status=Post.PostStatus.PUBLISHED,
        published_at__lte=timezone.now()
    ).select_related('author', 'category').values(
        'id', 'title', 'slug', 'excerpt', 'featured_image_url', 
        'published_at', 'author__display_name', 'category__name'
    )[:6]
    
    # Categories
    categories = Category.objects.filter(is_active=True).values(
        'id', 'name', 'slug', 'color', 'icon', 'post_count'
    )
    
    data = {
        'featured_posts': list(featured_posts),
        'latest_posts': list(latest_posts),
        'categories': list(categories)
    }
    
    return JsonResponse(data)


def get_blog_listing_data(request):
    """API endpoint for blog listing data"""
    
    # Get query parameters
    page = int(request.GET.get('page', 1))
    category_slug = request.GET.get('category')
    tag_slug = request.GET.get('tag')
    sort_by = request.GET.get('sort_by', 'latest')
    
    # Build queryset
    queryset = Post.objects.filter(
        status=Post.PostStatus.PUBLISHED,
        published_at__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related('tags')
    
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    
    if tag_slug:
        queryset = queryset.filter(tags__slug=tag_slug)
    
    # Apply sorting
    if sort_by == 'oldest':
        queryset = queryset.order_by('published_at')
    elif sort_by == 'popular':
        queryset = queryset.order_by('-view_count')
    elif sort_by == 'commented':
        queryset = queryset.order_by('-comment_count')
    else:  # latest
        queryset = queryset.order_by('-published_at')
    
    # Paginate
    paginator = Paginator(queryset, 9)
    posts = paginator.get_page(page)
    
    # Serialize data
    posts_data = []
    for post in posts:
        posts_data.append({
            'id': str(post.id),
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt,
            'featured_image_url': post.featured_image_url,
            'published_at': post.published_at.isoformat() if post.published_at else None,
            'author_name': post.author_name,
            'author_avatar': post.author_avatar,
            'category_name': post.category_name,
            'category_slug': post.category_slug,
            'category_color': post.category_color,
            'tags': [{'name': tag.name, 'slug': tag.slug} for tag in post.tags.all()],
            'view_count': post.view_count,
            'comment_count': post.comment_count,
            'is_video_post': post.is_video_post
        })
    
    data = {
        'posts': posts_data,
        'pagination': {
            'current_page': posts.number,
            'total_pages': paginator.num_pages,
            'has_next': posts.has_next(),
            'has_previous': posts.has_previous(),
            'total_posts': paginator.count
        }
    }
    
    return JsonResponse(data)


def get_post_data(request, slug):
    """API endpoint for single post data"""
    
    post = get_object_or_404(
        Post.objects.select_related('author', 'category').prefetch_related('tags'),
        slug=slug,
        status=Post.PostStatus.PUBLISHED,
        published_at__lte=timezone.now()
    )
    
    # Increment view count
    post.increment_view_count()
    
    # Get comments
    comments = Comment.objects.filter(
        post=post,
        status=Comment.CommentStatus.APPROVED,
        parent=None
    ).select_related('user').prefetch_related('replies')
    
    # Serialize comments
    comments_data = []
    for comment in comments:
        comment_data = {
            'id': str(comment.id),
            'content': comment.content,
            'commenter_name': comment.commenter_name,
            'commenter_avatar': comment.commenter_avatar,
            'created_at': comment.created_at.isoformat(),
            'replies': []
        }
        
        for reply in comment.get_replies():
            comment_data['replies'].append({
                'id': str(reply.id),
                'content': reply.content,
                'commenter_name': reply.commenter_name,
                'commenter_avatar': reply.commenter_avatar,
                'created_at': reply.created_at.isoformat()
            })
        
        comments_data.append(comment_data)
    
    # Get related posts
    related_posts = Post.objects.filter(
        status=Post.PostStatus.PUBLISHED,
        published_at__lte=timezone.now(),
        category=post.category
    ).exclude(id=post.id).select_related('author', 'category')[:3]
    
    related_posts_data = []
    for related_post in related_posts:
        related_posts_data.append({
            'id': str(related_post.id),
            'title': related_post.title,
            'slug': related_post.slug,
            'excerpt': related_post.excerpt,
            'featured_image_url': related_post.featured_image_url,
            'published_at': related_post.published_at.isoformat() if related_post.published_at else None,
            'author_name': related_post.author_name,
            'category_name': related_post.category_name
        })
    
    data = {
        'post': {
            'id': str(post.id),
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt,
            'content': post.content,
            'featured_image_url': post.featured_image_url,
            'featured_image_alt': post.featured_image_alt,
            'published_at': post.published_at.isoformat() if post.published_at else None,
            'author_name': post.author_name,
            'author_avatar': post.author_avatar,
            'category_name': post.category_name,
            'category_slug': post.category_slug,
            'category_color': post.category_color,
            'tags': [{'name': tag.name, 'slug': tag.slug} for tag in post.tags.all()],
            'view_count': post.view_count,
            'comment_count': post.comment_count,
            'is_video_post': post.is_video_post,
            'meta_title': post.meta_title,
            'meta_description': post.meta_description
        },
        'comments': comments_data,
        'related_posts': related_posts_data
    }
    
    return JsonResponse(data)


def search_posts(request):
    """API endpoint for searching posts"""
    
    query = request.GET.get('q', '')
    
    if not query:
        return JsonResponse({'posts': [], 'total': 0})
    
    # Use PostgreSQL full-text search
    search_vector = SearchVector('title', weight='A') + SearchVector('excerpt', weight='B') + SearchVector('content', weight='C')
    search_query = SearchQuery(query)
    
    posts = Post.objects.annotate(
        search=search_vector,
        rank=SearchRank(search_vector, search_query)
    ).filter(
        search=search_query,
        status=Post.PostStatus.PUBLISHED,
        published_at__lte=timezone.now()
    ).select_related('author', 'category').prefetch_related('tags').order_by('-rank')[:20]
    
    posts_data = []
    for post in posts:
        posts_data.append({
            'id': str(post.id),
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt,
            'featured_image_url': post.featured_image_url,
            'published_at': post.published_at.isoformat() if post.published_at else None,
            'author_name': post.author_name,
            'category_name': post.category_name
        })
    
    return JsonResponse({
        'posts': posts_data,
        'total': len(posts_data),
        'query': query
    })
