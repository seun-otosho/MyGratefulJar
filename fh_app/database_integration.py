"""
Database Integration Module for FastHTML Nemesis Blog
Connects FastHTML routes to Supabase database operations
"""
# cp
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our database models and operations
from database_models import (
    db, 
    PostModel, 
    CategoryModel, 
    CommentModel, 
    ContactSubmissionModel,
    NewsletterSubscriberModel,
    format_date,
    truncate_text,
    create_slug
)

class BlogDataService:
    """
    Service class to handle all blog data operations
    Provides clean interface between FastHTML routes and database
    """
    
    def __init__(self):
        self.db = db
    
    # =====================================================
    # HOMEPAGE DATA
    # =====================================================
    
    async def get_homepage_data(self) -> Dict[str, Any]:
        """Get all data needed for homepage"""
        try:
            # Get featured post for hero slider
            featured_posts = await self.db.get_featured_posts(limit=1)
            featured_post = featured_posts[0] if featured_posts else None
            
            # Get regular posts for card layout (excluding featured)
            all_posts = await self.db.get_published_posts(limit=10)
            regular_posts = [post for post in all_posts if not post.is_featured][:6]
            
            # Get categories for sidebar
            categories = await self.db.get_active_categories()
            
            return {
                "featured_post": self._format_post_for_template(featured_post) if featured_post else None,
                "regular_posts": [self._format_post_for_template(post) for post in regular_posts],
                "categories": [self._format_category_for_template(cat) for cat in categories]
            }
        except Exception as e:
            print(f"Error getting homepage data: {e}")
            return self._get_fallback_homepage_data()
    
    # =====================================================
    # BLOG LISTING DATA
    # =====================================================
    
    async def get_blog_listing_data(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get all data needed for blog listing page"""
        try:
            offset = (page - 1) * per_page
            
            # Get posts for main listing
            posts = await self.db.get_published_posts(limit=per_page, offset=offset)
            
            # Get featured posts for gallery section
            featured_posts = await self.db.get_featured_posts(limit=5)
            
            # Get featured post for sidebar
            sidebar_featured = featured_posts[0] if featured_posts else posts[0] if posts else None
            
            # Get popular posts for sidebar (for now, just recent posts)
            popular_posts = await self.db.get_published_posts(limit=4)
            
            return {
                "posts": [self._format_post_for_template(post) for post in posts],
                "gallery_posts": [self._format_post_for_template(post) for post in featured_posts],
                "sidebar_featured": self._format_post_for_template(sidebar_featured) if sidebar_featured else None,
                "popular_posts": [self._format_post_for_template(post) for post in popular_posts],
                "current_page": page,
                "has_more": len(posts) == per_page
            }
        except Exception as e:
            print(f"Error getting blog listing data: {e}")
            return self._get_fallback_blog_data()
    
    # =====================================================
    # SINGLE POST DATA
    # =====================================================
    
    async def get_post_data(self, post_id: str) -> Dict[str, Any]:
        """Get all data needed for single post page"""
        try:
            # Get the main post
            post = await self.db.get_post_by_id(post_id)
            if not post:
                return None
            
            # Get post comments
            comments = await self.db.get_post_comments(post_id)
            
            # Get related posts (same category, excluding current post)
            related_posts = []
            if post.category_slug:
                category_posts = await self.db.get_posts_by_category(post.category_slug, limit=4)
                related_posts = [p for p in category_posts if p.id != post_id][:3]
            
            # If not enough related posts, get recent posts
            if len(related_posts) < 3:
                recent_posts = await self.db.get_published_posts(limit=5)
                for recent_post in recent_posts:
                    if recent_post.id != post_id and recent_post not in related_posts:
                        related_posts.append(recent_post)
                        if len(related_posts) >= 3:
                            break
            
            return {
                "post": self._format_post_for_template(post),
                "comments": self._format_comments_for_template(comments),
                "related_posts": [self._format_post_for_template(p) for p in related_posts],
                "content_data": self._get_post_content_data(post)
            }
        except Exception as e:
            print(f"Error getting post data for {post_id}: {e}")
            return None
    
    # =====================================================
    # SEARCH DATA
    # =====================================================
    
    async def search_posts(self, query: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Search posts and return formatted results"""
        try:
            if not query or len(query.strip()) < 2:
                return {"posts": [], "query": query, "total": 0}
            
            # Perform search
            posts = await self.db.search_posts(query.strip(), limit=per_page)
            
            return {
                "posts": [self._format_post_for_template(post) for post in posts],
                "query": query,
                "total": len(posts),
                "current_page": page
            }
        except Exception as e:
            print(f"Error searching posts: {e}")
            return {"posts": [], "query": query, "total": 0}
    
    # =====================================================
    # CATEGORY DATA
    # =====================================================
    
    async def get_category_posts(self, category_slug: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get posts for a specific category"""
        try:
            offset = (page - 1) * per_page
            
            # Get category info
            category = await self.db.get_category_by_slug(category_slug)
            if not category:
                return None
            
            # Get posts in category
            posts = await self.db.get_posts_by_category(category_slug, limit=per_page, offset=offset)
            
            return {
                "category": self._format_category_for_template(category),
                "posts": [self._format_post_for_template(post) for post in posts],
                "current_page": page,
                "has_more": len(posts) == per_page
            }
        except Exception as e:
            print(f"Error getting category posts for {category_slug}: {e}")
            return None
    
    # =====================================================
    # FORM SUBMISSIONS
    # =====================================================
    
    async def submit_contact_form(self, name: str, email: str, website: str = "", message: str = "") -> bool:
        """Handle contact form submission"""
        try:
            submission = ContactSubmissionModel(
                name=name.strip(),
                email=email.strip(),
                website=website.strip() if website else None,
                message=message.strip()
            )
            
            result = await self.db.create_contact_submission(submission)
            return result is not None
        except Exception as e:
            print(f"Error submitting contact form: {e}")
            return False
    
    async def submit_comment(self, post_id: str, name: str, email: str, website: str = "", comment: str = "") -> bool:
        """Handle comment submission"""
        try:
            comment_obj = CommentModel(
                post_id=post_id,
                guest_name=name.strip(),
                guest_email=email.strip(),
                guest_website=website.strip() if website else None,
                content=comment.strip()
            )
            
            result = await self.db.create_comment(comment_obj)
            return result is not None
        except Exception as e:
            print(f"Error submitting comment: {e}")
            return False
    
    async def subscribe_newsletter(self, email: str, source: str = "footer_form") -> bool:
        """Handle newsletter subscription"""
        try:
            result = await self.db.subscribe_to_newsletter(email.strip(), source)
            return result is not None
        except Exception as e:
            print(f"Error subscribing to newsletter: {e}")
            return False
    
    # =====================================================
    # HELPER METHODS
    # =====================================================
    
    def _format_post_for_template(self, post: PostModel) -> Dict[str, Any]:
        """Format post data for template consumption"""
        if not post:
            return None
        
        return {
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "excerpt": post.excerpt or truncate_text(post.content, 150),
            "content": post.content,
            "image": post.featured_image_url or "./images/default-post.jpg",
            "author": post.author_name or "Anonymous",
            "author_avatar": post.author_avatar or "./images/default-avatar.jpg",
            "date": format_date(post.published_at) if post.published_at else format_date(post.created_at),
            "category": post.category_name or "General",
            "category_slug": post.category_slug or "general",
            "category_color": post.category_color or "#007bff",
            "is_featured": post.is_featured,
            "is_video": post.is_video_post,
            "view_count": post.view_count,
            "comment_count": post.comment_count,
            "tags": post.tags or []
        }
    
    def _format_category_for_template(self, category: CategoryModel) -> Dict[str, Any]:
        """Format category data for template consumption"""
        if not category:
            return None
        
        return {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "color": category.color or "#007bff",
            "icon": category.icon,
            "post_count": category.post_count
        }
    
    def _format_comments_for_template(self, comments: List[CommentModel]) -> List[Dict[str, Any]]:
        """Format comments data for template consumption"""
        formatted_comments = []
        
        for comment in comments:
            formatted_comment = {
                "id": comment.id,
                "author": comment.commenter_name or comment.guest_name or "Anonymous",
                "avatar": comment.commenter_avatar or "./images/default-avatar.jpg",
                "content": comment.content,
                "date": format_date(comment.created_at) if comment.created_at else "",
                "website": comment.guest_website,
                "replies": []
            }
            
            # Handle replies (if parent_id is None, it's a top-level comment)
            if not comment.parent_id:
                formatted_comments.append(formatted_comment)
        
        return formatted_comments
    
    def _get_post_content_data(self, post: PostModel) -> Dict[str, Any]:
        """Get additional content data for single post"""
        return {
            "content": post.content,
            "highlighted_text": "Key insights and important information from this article.",
            "quote": "This article provides valuable insights into the topic discussed.",
            "categories": [post.category_name] if post.category_name else ["General"],
            "tags": post.tags or ["blog", "article"]
        }
    
    def _get_fallback_homepage_data(self) -> Dict[str, Any]:
        """Fallback data when database is unavailable"""
        return {
            "featured_post": None,
            "regular_posts": [],
            "categories": [
                {"name": "Design", "slug": "design", "color": "#007bff"},
                {"name": "Technology", "slug": "technology", "color": "#28a745"},
                {"name": "Lifestyle", "slug": "lifestyle", "color": "#ffc107"}
            ]
        }
    
    def _get_fallback_blog_data(self) -> Dict[str, Any]:
        """Fallback data for blog listing when database is unavailable"""
        return {
            "posts": [],
            "gallery_posts": [],
            "sidebar_featured": None,
            "popular_posts": [],
            "current_page": 1,
            "has_more": False
        }

# =====================================================
# GLOBAL SERVICE INSTANCE
# =====================================================

# Create global blog data service instance
blog_service = BlogDataService()

# =====================================================
# UTILITY FUNCTIONS FOR FASTHTML INTEGRATION
# =====================================================

async def get_homepage_data():
    """Convenience function for homepage route"""
    return await blog_service.get_homepage_data()

async def get_blog_listing_data(page: int = 1):
    """Convenience function for blog listing route"""
    return await blog_service.get_blog_listing_data(page)

async def get_post_data(post_id: str):
    """Convenience function for single post route"""
    return await blog_service.get_post_data(post_id)

async def search_posts(query: str):
    """Convenience function for search route"""
    return await blog_service.search_posts(query)

async def submit_contact_form(name: str, email: str, website: str = "", message: str = ""):
    """Convenience function for contact form submission"""
    return await blog_service.submit_contact_form(name, email, website, message)

async def submit_comment(post_id: str, name: str, email: str, website: str = "", comment: str = ""):
    """Convenience function for comment submission"""
    return await blog_service.submit_comment(post_id, name, email, website, comment)

async def subscribe_newsletter(email: str):
    """Convenience function for newsletter subscription"""
    return await blog_service.subscribe_newsletter(email)

# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    """
    Example usage in FastHTML routes:
    
    @rt("/")
    async def homepage():
        data = await get_homepage_data()
        featured_post = data["featured_post"]
        regular_posts = data["regular_posts"]
        categories = data["categories"]
        
        return render_homepage(featured_post, regular_posts, categories)
    
    @rt("/blog")
    async def blog_listing():
        data = await get_blog_listing_data()
        return render_blog_listing(data)
    
    @rt("/post/{post_id}")
    async def single_post(post_id: str):
        data = await get_post_data(post_id)
        if not data:
            return "Post not found", 404
        return render_single_post(data)
    """
    print("Database integration module loaded successfully!")
    print("Use the convenience functions in your FastHTML routes.")