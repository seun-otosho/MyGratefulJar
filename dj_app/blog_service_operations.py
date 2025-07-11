from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, Count, F
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from typing import Dict, List, Optional, Any
import logging

from .models import (
    Post, Category, Tag, Comment, ContactSubmission, 
    NewsletterSubscriber, User
)

logger = logging.getLogger(__name__)


class BlogService:
    """Service class for blog operations"""
    
    def get_homepage_data(self) -> Dict[str, Any]:
        """Get homepage data including featured posts and latest posts"""
        try:
            # Featured posts for hero slider
            featured_posts = Post.objects.filter(
                status=Post.PostStatus.PUBLISHED,
                is_featured=True,
                published_at__lte=timezone.now()
            ).select_related('author', 'category').prefetch_related('tags')[:3]
            
            # Latest posts
            latest_posts = Post.objects.filter(
                status=Post.PostStatus.PUBLISHED,
                published_at__lte=timezone.now()
            ).select_related('author', 'category').prefetch_related('tags')[:6]
            
            # Popular posts
            popular_posts = Post.objects.filter(
                status=Post.PostStatus.PUBLISHED,
                published_at__lte=timezone.now()
            ).select_related('author', 'category').order_by('-view_count')[:4]
            
            # Categories with post counts
            categories = Category.objects.filter(
                is_active=True
            ).annotate(
                published_post_count=Count('posts', filter=Q(posts__status=Post.PostStatus.PUBLISHED))
            ).order_by('name')
            
            return {
                'featured_posts': [self._format_post_for_template(post) for post in featured_posts],
                'latest_posts': [self._format_post_for_template(post) for post in latest_posts],
                'popular_posts': [self._format_post_for_template(post) for post in popular_posts],
                'categories': [self._format_category_for_template(cat) for cat in categories],
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error getting homepage data: {str(e)}")
            return self._get_fallback_homepage_data()
    
    def get_blog_listing_data(self, page: int = 1, category_slug: str = None, 
                            tag_slug: str = None, sort_by: str = 'latest') -> Dict[str, Any]:
        """Get blog listing data with pagination and filtering"""
        try:
            # Build queryset
            queryset = Post.objects.filter(
                status=Post.PostStatus.PUBLISHED,
                published_at__lte=timezone.now()
            ).select_related('author', 'category').prefetch_related('tags')
            
            # Apply filters
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
            from django.core.paginator import Paginator
            paginator = Paginator(queryset, 9)
            posts = paginator.get_page(page)
            
            return {
                'posts': [self._format_post_for_template(post) for post in posts],
                'pagination': {
                    'current_page': posts.number,
                    'total_pages': paginator.num_pages,
                    'has_next': posts.has_next(),
                    'has_previous': posts.has_previous(),
                    'total_posts': paginator.count
                },
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error getting blog listing data: {str(e)}")
            return self._get_fallback_blog_data()
    
    def get_post_data(self, slug: str) -> Dict[str, Any]:
        """Get single post data with comments"""
        try:
            post = Post.objects.filter(
                slug=slug,
                status=Post.PostStatus.PUBLISHED,
                published_at__lte=timezone.now()
            ).select_related('author', 'category').prefetch_related('tags').first()
            
            if not post:
                return {'success': False, 'error': 'Post not found'}
            
            # Increment view count
            post.increment_view_count()
            
            # Get comments
            comments = Comment.objects.filter(
                post=post,
                status=Comment.CommentStatus.APPROVED,
                parent=None
            ).select_related('user').prefetch_related('replies')
            
            # Get related posts
            related_posts = Post.objects.filter(
                status=Post.PostStatus.PUBLISHED,
                published_at__lte=timezone.now(),
                category=post.category
            ).exclude(id=post.id).select_related('author', 'category')[:3]
            
            return {
                'post': self._get_post_content_data(post),
                'comments': self._format_comments_for_template(comments),
                'related_posts': [self._format_post_for_template(p) for p in related_posts],
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error getting post data for {slug}: {str(e)}")
            return {'success': False, 'error': 'Failed to load post'}
    
    def search_posts(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search posts using full-text search"""
        try:
            if not query:
                return {'posts': [], 'total': 0, 'success': True}
            
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
            ).select_related('author', 'category').prefetch_related('tags').order_by('-rank')[:limit]
            
            return {
                'posts': [self._format_post_for_template(post) for post in posts],
                'total': len(posts),
                'query': query,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error searching posts: {str(e)}")
            return {'posts': [], 'total': 0, 'success': False, 'error': 'Search failed'}
    
    def get_category_posts(self, category_slug: str, limit: int = 10) -> Dict[str, Any]:
        """Get posts from a specific category"""
        try:
            category = Category.objects.filter(slug=category_slug, is_active=True).first()
            if not category:
                return {'success': False, 'error': 'Category not found'}
            
            posts = Post.objects.filter(
                category=category,
                status=Post.PostStatus.PUBLISHED,
                published_at__lte=timezone.now()
            ).select_related('author', 'category').prefetch_related('tags')[:limit]
            
            return {
                'category': self._format_category_for_template(category),
                'posts': [self._format_post_for_template(post) for post in posts],
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error getting category posts: {str(e)}")
            return {'success': False, 'error': 'Failed to load category posts'}
    
    @transaction.atomic
    def submit_contact_form(self, name: str, email: str, message: str, 
                          website: str = None, subject: str = None,
                          ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Submit contact form"""
        try:
            contact = ContactSubmission.objects.create(
                name=name,
                email=email,
                website=website or '',
                subject=subject or '',
                message=message,
                ip_address=ip_address,
                user_agent=user_agent or ''
            )
            
            return {
                'success': True,
                'message': 'Thank you for your message! We will get back to you soon.',
                'contact_id': str(contact.id)
            }
            
        except Exception as e:
            logger.error(f"Error submitting contact form: {str(e)}")
            return {'success': False, 'error': 'Failed to submit contact form'}
    
    @transaction.atomic
    def submit_comment(self, post_slug: str, content: str, user: User = None,
                      guest_name: str = None, guest_email: str = None,
                      guest_website: str = None, parent_id: str = None,
                      ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Submit comment on a post"""
        try:
            post = Post.objects.filter(
                slug=post_slug,
                status=Post.PostStatus.PUBLISHED
            ).first()
            
            if not post:
                return {'success': False, 'error': 'Post not found'}
            
            # Create comment
            comment = Comment(
                post=post,
                content=content,
                ip_address=ip_address,
                user_agent=user_agent or ''
            )
            
            # Handle authenticated vs guest users
            if user and user.is_authenticated:
                comment.user = user
            else:
                comment.guest_name = guest_name or ''
                comment.guest_email = guest_email or ''
                comment.guest_website = guest_website or ''
            
            # Handle parent comment for replies
            if parent_id:
                try:
                    parent = Comment.objects.get(id=parent_id, post=post)
                    comment.parent = parent
                except Comment.DoesNotExist:
                    pass
            
            comment.save()
            
            return {
                'success': True,
                'message': 'Comment submitted successfully! It will be visible after approval.',
                'comment_id': str(comment.id)
            }
            
        except Exception as e:
            logger.error(f"Error submitting comment: {str(e)}")
            return {'success': False, 'error': 'Failed to submit comment'}
    
    @transaction.atomic
    def subscribe_newsletter(self, email: str, source: str = 'footer_form',
                           ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Subscribe to newsletter"""
        try:
            # Check if already subscribed
            if NewsletterSubscriber.objects.filter(email=email).exists():
                return {'success': False, 'error': 'Email already subscribed'}
            
            subscriber = NewsletterSubscriber.objects.create(
                email=email,
                source=source,
                ip_address=ip_address,
                user_agent=user_agent or ''
            )
            
            return {
                'success': True,
                'message': 'Thank you for subscribing to our newsletter!',
                'subscriber_id': str(subscriber.id)
            }
            
        except Exception as e:
            logger.error(f"Error subscribing to newsletter: {str(e)}")
            return {'success': False, 'error': 'Failed to subscribe'}
    
    def _format_post_for_template(self, post: Post) -> Dict[str, Any]:
        """Format post data for template rendering"""
        return {
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
            'like_count': post.like_count,
            'share_count': post.share_count,
            'is_featured': post.is_featured,
            'is_video_post': post.is_video_post,
            'meta_title': post.meta_title,
            'meta_description': post.meta_description
        }
    
    def _format_category_for_template(self, category: Category) -> Dict[str, Any]:
        """Format category data for template rendering"""
        return {
            'id': str(category.id),
            'name': category.name,
            'slug': category.slug,
            'description': category.description,
            'color': category.color,
            'icon': category.icon,
            'post_count': getattr(category, 'published_post_count', category.post_count),
            'is_active': category.is_active
        }
    
    def _format_comments_for_template(self, comments) -> List[Dict[str, Any]]:
        """Format comments data for template rendering"""
        comments_data = []
        
        for comment in comments:
            comment_data = {
                'id': str(comment.id),
                'content': comment.content,
                'commenter_name': comment.commenter_name,
                'commenter_avatar': comment.commenter_avatar,
                'created_at': comment.created_at.isoformat(),
                'is_pinned': comment.is_pinned,
                'replies': []
            }
            
            # Add replies
            for reply in comment.get_replies():
                comment_data['replies'].append({
                    'id': str(reply.id),
                    'content': reply.content,
                    'commenter_name': reply.commenter_name,
                    'commenter_avatar': reply.commenter_avatar,
                    'created_at': reply.created_at.isoformat()
                })
            
            comments_data.append(comment_data)
        
        return comments_data
    
    def _get_post_content_data(self, post: Post) -> Dict[str, Any]:
        """Get detailed post content data"""
        return {
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
            'like_count': post.like_count,
            'share_count': post.share_count,
            'is_video_post': post.is_video_post,
            'meta_title': post.meta_title,
            'meta_description': post.meta_description,
            'meta_keywords': post.meta_keywords
        }
    
    def _get_fallback_homepage_data(self) -> Dict[str, Any]:
        """Fallback homepage data when main query fails"""
        return {
            'featured_posts': [],
            'latest_posts': [],
            'popular_posts': [],
            'categories': [],
            'success': False,
            'error': 'Failed to load homepage data'
        }
    
    def _get_fallback_blog_data(self) -> Dict[str, Any]:
        """Fallback blog data when main query fails"""
        return {
            'posts': [],
            'pagination': {
                'current_page': 1,
                'total_pages': 1,
                'has_next': False,
                'has_previous': False,
                'total_posts': 0
            },
            'success': False,
            'error': 'Failed to load blog data'
        }


# Create service instance
blog_service = BlogService()


# Helper functions for backward compatibility
def get_homepage_data():
    """Get homepage data"""
    return blog_service.get_homepage_data()


def get_blog_listing_data(page=1, category_slug=None, tag_slug=None, sort_by='latest'):
    """Get blog listing data"""
    return blog_service.get_blog_listing_data(page, category_slug, tag_slug, sort_by)


def get_post_data(slug):
    """Get post data"""
    return blog_service.get_post_data(slug)


def search_posts(query, limit=20):
    """Search posts"""
    return blog_service.search_posts(query, limit)


def submit_contact_form(name, email, message, website=None, subject=None, ip_address=None, user_agent=None):
    """Submit contact form"""
    return blog_service.submit_contact_form(name, email, message, website, subject, ip_address, user_agent)


def submit_comment(post_slug, content, user=None, guest_name=None, guest_email=None, 
                   guest_website=None, parent_id=None, ip_address=None, user_agent=None):
    """Submit comment"""
    return blog_service.submit_comment(post_slug, content, user, guest_name, guest_email, 
                                     guest_website, parent_id, ip_address, user_agent)


def subscribe_newsletter(email, source='footer_form', ip_address=None, user_agent=None):
    """Subscribe to newsletter"""
    return blog_service.subscribe_newsletter(email, source, ip_address, user_agent)
