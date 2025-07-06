"""
Database Models and Helper Functions for Nemesis Blog Platform
Designed for Supabase PostgreSQL integration with FastHTML

This module provides:
- Pydantic models for data validation
- Database connection utilities
- CRUD operations for all entities
- Helper functions for common queries
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field, validator
from supabase import create_client, Client
import os
from enum import Enum

# =====================================================
# CONFIGURATION
# =====================================================

class DatabaseConfig:
    """Database configuration for Supabase"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
    
    def get_client(self) -> Client:
        """Get Supabase client instance"""
        return create_client(self.supabase_url, self.supabase_key)

# Global database config instance
db_config = DatabaseConfig()

# =====================================================
# ENUMS
# =====================================================

class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    AUTHOR = "author"
    USER = "user"

class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SCHEDULED = "scheduled"

class CommentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SPAM = "spam"
    TRASH = "trash"

class ContactStatus(str, Enum):
    NEW = "new"
    READ = "read"
    REPLIED = "replied"
    ARCHIVED = "archived"

class SubscriberStatus(str, Enum):
    ACTIVE = "active"
    UNSUBSCRIBED = "unsubscribed"
    BOUNCED = "bounced"

# =====================================================
# PYDANTIC MODELS
# =====================================================

class UserModel(BaseModel):
    """User model for authors, commenters, and admin users"""
    id: Optional[str] = None
    email: EmailStr
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    website_url: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    email_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CategoryModel(BaseModel):
    """Category model for blog post categorization"""
    id: Optional[str] = None
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')  # Hex color
    icon: Optional[str] = None  # FontAwesome icon class
    post_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TagModel(BaseModel):
    """Tag model for flexible post tagging"""
    id: Optional[str] = None
    name: str = Field(..., max_length=50)
    slug: str = Field(..., max_length=50)
    post_count: int = 0
    created_at: Optional[datetime] = None

class PostModel(BaseModel):
    """Main blog post model"""
    id: Optional[str] = None
    title: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255)
    excerpt: Optional[str] = None
    content: str
    featured_image_url: Optional[str] = None
    featured_image_alt: Optional[str] = None
    author_id: Optional[str] = None
    category_id: Optional[str] = None
    
    # Status and visibility
    status: PostStatus = PostStatus.DRAFT
    is_featured: bool = False
    is_video_post: bool = False
    
    # SEO metadata
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    
    # Engagement metrics
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    
    # Timestamps
    published_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Related data (populated by joins)
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    category_name: Optional[str] = None
    category_slug: Optional[str] = None
    category_color: Optional[str] = None
    tags: Optional[List[str]] = []

class CommentModel(BaseModel):
    """Comment model for blog post comments"""
    id: Optional[str] = None
    post_id: str
    parent_id: Optional[str] = None  # For replies
    
    # Commenter information
    user_id: Optional[str] = None  # Registered users
    guest_name: Optional[str] = Field(None, max_length=100)
    guest_email: Optional[EmailStr] = None
    guest_website: Optional[str] = None
    
    # Comment content
    content: str
    
    # Moderation
    status: CommentStatus = CommentStatus.PENDING
    is_pinned: bool = False
    
    # Metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Related data
    commenter_name: Optional[str] = None
    commenter_avatar: Optional[str] = None
    replies: Optional[List['CommentModel']] = []

class ContactSubmissionModel(BaseModel):
    """Contact form submission model"""
    id: Optional[str] = None
    name: str = Field(..., max_length=100)
    email: EmailStr
    website: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=255)
    message: str
    
    # Status tracking
    status: ContactStatus = ContactStatus.NEW
    
    # Metadata
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class NewsletterSubscriberModel(BaseModel):
    """Newsletter subscriber model"""
    id: Optional[str] = None
    email: EmailStr
    status: SubscriberStatus = SubscriberStatus.ACTIVE
    
    # Subscription metadata
    source: Optional[str] = None  # 'footer_form', 'popup', etc.
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Email preferences
    confirmed_at: Optional[datetime] = None
    unsubscribed_at: Optional[datetime] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MediaUploadModel(BaseModel):
    """Media upload model for images and files"""
    id: Optional[str] = None
    filename: str = Field(..., max_length=255)
    original_filename: str = Field(..., max_length=255)
    file_path: str
    file_url: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = Field(None, max_length=100)
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    
    # Relationships
    uploaded_by: Optional[str] = None
    post_id: Optional[str] = None
    
    # Image metadata
    width: Optional[int] = None
    height: Optional[int] = None
    
    # Timestamps
    created_at: Optional[datetime] = None

class SiteSettingModel(BaseModel):
    """Site settings model for global configuration"""
    id: Optional[str] = None
    setting_key: str = Field(..., max_length=100)
    setting_value: Optional[str] = None
    setting_type: str = Field(default="text", pattern=r'^(text|number|boolean|json)$')
    description: Optional[str] = None
    is_public: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# =====================================================
# DATABASE OPERATIONS
# =====================================================

class DatabaseOperations:
    """Database operations class for CRUD operations"""
    
    def __init__(self):
        self.client = db_config.get_client()
    
    # =====================================================
    # POSTS OPERATIONS
    # =====================================================
    
    async def get_published_posts(self, limit: int = 10, offset: int = 0) -> List[PostModel]:
        """Get published posts with author and category info"""
        try:
            response = self.client.from_("published_posts_view") \
                .select("*") \
                .order("published_at", desc=True) \
                .range(offset, offset + limit - 1) \
                .execute()
            
            return [PostModel(**post) for post in response.data]
        except Exception as e:
            print(f"Error fetching published posts: {e}")
            return []
    
    async def get_post_by_id(self, post_id: str) -> Optional[PostModel]:
        """Get a single post by ID"""
        try:
            response = self.client.from_("published_posts_view") \
                .select("*") \
                .eq("id", post_id) \
                .single() \
                .execute()
            
            return PostModel(**response.data) if response.data else None
        except Exception as e:
            print(f"Error fetching post {post_id}: {e}")
            return None
    
    async def get_post_by_slug(self, slug: str) -> Optional[PostModel]:
        """Get a single post by slug"""
        try:
            response = self.client.from_("published_posts_view") \
                .select("*") \
                .eq("slug", slug) \
                .single() \
                .execute()
            
            return PostModel(**response.data) if response.data else None
        except Exception as e:
            print(f"Error fetching post with slug {slug}: {e}")
            return None
    
    async def get_featured_posts(self, limit: int = 5) -> List[PostModel]:
        """Get featured posts for hero slider"""
        try:
            response = self.client.from_("published_posts_view") \
                .select("*") \
                .eq("is_featured", True) \
                .order("published_at", desc=True) \
                .limit(limit) \
                .execute()
            
            return [PostModel(**post) for post in response.data]
        except Exception as e:
            print(f"Error fetching featured posts: {e}")
            return []
    
    async def get_posts_by_category(self, category_slug: str, limit: int = 10, offset: int = 0) -> List[PostModel]:
        """Get posts by category"""
        try:
            response = self.client.from_("published_posts_view") \
                .select("*") \
                .eq("category_slug", category_slug) \
                .order("published_at", desc=True) \
                .range(offset, offset + limit - 1) \
                .execute()
            
            return [PostModel(**post) for post in response.data]
        except Exception as e:
            print(f"Error fetching posts for category {category_slug}: {e}")
            return []
    
    async def search_posts(self, query: str, limit: int = 10) -> List[PostModel]:
        """Search posts using full-text search"""
        try:
            response = self.client.from_("posts") \
                .select("*, users(display_name, avatar_url), categories(name, slug, color)") \
                .text_search("title,excerpt,content", query) \
                .eq("status", "published") \
                .order("published_at", desc=True) \
                .limit(limit) \
                .execute()
            
            return [PostModel(**post) for post in response.data]
        except Exception as e:
            print(f"Error searching posts: {e}")
            return []
    
    async def create_post(self, post: PostModel) -> Optional[PostModel]:
        """Create a new blog post"""
        try:
            post_data = post.dict(exclude_unset=True, exclude={"id", "created_at", "updated_at"})
            response = self.client.from_("posts") \
                .insert(post_data) \
                .execute()
            
            return PostModel(**response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error creating post: {e}")
            return None
    
    async def update_post(self, post_id: str, post_data: Dict[str, Any]) -> Optional[PostModel]:
        """Update an existing post"""
        try:
            response = self.client.from_("posts") \
                .update(post_data) \
                .eq("id", post_id) \
                .execute()
            
            return PostModel(**response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error updating post {post_id}: {e}")
            return None
    
    # =====================================================
    # COMMENTS OPERATIONS
    # =====================================================
    
    async def get_post_comments(self, post_id: str) -> List[CommentModel]:
        """Get approved comments for a post"""
        try:
            response = self.client.from_("comment_threads_view") \
                .select("*") \
                .eq("post_id", post_id) \
                .order("created_at", desc=False) \
                .execute()
            
            return [CommentModel(**comment) for comment in response.data]
        except Exception as e:
            print(f"Error fetching comments for post {post_id}: {e}")
            return []
    
    async def create_comment(self, comment: CommentModel) -> Optional[CommentModel]:
        """Create a new comment"""
        try:
            comment_data = comment.dict(exclude_unset=True, exclude={"id", "created_at", "updated_at"})
            response = self.client.from_("comments") \
                .insert(comment_data) \
                .execute()
            
            return CommentModel(**response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error creating comment: {e}")
            return None
    
    # =====================================================
    # CATEGORIES OPERATIONS
    # =====================================================
    
    async def get_active_categories(self) -> List[CategoryModel]:
        """Get all active categories"""
        try:
            response = self.client.from_("categories") \
                .select("*") \
                .eq("is_active", True) \
                .order("name") \
                .execute()
            
            return [CategoryModel(**category) for category in response.data]
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []
    
    async def get_category_by_slug(self, slug: str) -> Optional[CategoryModel]:
        """Get category by slug"""
        try:
            response = self.client.from_("categories") \
                .select("*") \
                .eq("slug", slug) \
                .single() \
                .execute()
            
            return CategoryModel(**response.data) if response.data else None
        except Exception as e:
            print(f"Error fetching category {slug}: {e}")
            return None
    
    # =====================================================
    # CONTACT OPERATIONS
    # =====================================================
    
    async def create_contact_submission(self, submission: ContactSubmissionModel) -> Optional[ContactSubmissionModel]:
        """Create a new contact form submission"""
        try:
            submission_data = submission.dict(exclude_unset=True, exclude={"id", "created_at", "updated_at"})
            response = self.client.from_("contact_submissions") \
                .insert(submission_data) \
                .execute()
            
            return ContactSubmissionModel(**response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error creating contact submission: {e}")
            return None
    
    # =====================================================
    # NEWSLETTER OPERATIONS
    # =====================================================
    
    async def subscribe_to_newsletter(self, email: str, source: str = "footer_form") -> Optional[NewsletterSubscriberModel]:
        """Subscribe email to newsletter"""
        try:
            subscriber_data = {
                "email": email,
                "source": source,
                "status": SubscriberStatus.ACTIVE
            }
            response = self.client.from_("newsletter_subscribers") \
                .insert(subscriber_data) \
                .execute()
            
            return NewsletterSubscriberModel(**response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error subscribing to newsletter: {e}")
            return None
    
    # =====================================================
    # SITE SETTINGS OPERATIONS
    # =====================================================
    
    async def get_public_settings(self) -> Dict[str, Any]:
        """Get public site settings"""
        try:
            response = self.client.from_("site_settings") \
                .select("setting_key, setting_value, setting_type") \
                .eq("is_public", True) \
                .execute()
            
            settings = {}
            for setting in response.data:
                key = setting["setting_key"]
                value = setting["setting_value"]
                setting_type = setting["setting_type"]
                
                # Convert value based on type
                if setting_type == "boolean":
                    settings[key] = value.lower() == "true"
                elif setting_type == "number":
                    settings[key] = int(value) if value else 0
                elif setting_type == "json":
                    import json
                    settings[key] = json.loads(value) if value else {}
                else:
                    settings[key] = value
            
            return settings
        except Exception as e:
            print(f"Error fetching site settings: {e}")
            return {}

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def create_slug(text: str) -> str:
    """Create URL-friendly slug from text"""
    import re
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def format_date(date: datetime) -> str:
    """Format date for display"""
    if not date:
        return ""
    return date.strftime("%B %d, %Y")

def truncate_text(text: str, length: int = 150) -> str:
    """Truncate text to specified length"""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + "..."

# =====================================================
# GLOBAL DATABASE INSTANCE
# =====================================================

# Create global database operations instance
db = DatabaseOperations()

# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    """
    Example usage of the database models and operations.
    
    To use this in your FastHTML application:
    
    1. Set environment variables:
       export SUPABASE_URL="your-supabase-url"
       export SUPABASE_ANON_KEY="your-supabase-anon-key"
    
    2. Import and use:
       from database_models import db, PostModel, CommentModel
       
       # Get published posts
       posts = await db.get_published_posts(limit=10)
       
       # Get post by ID
       post = await db.get_post_by_id("post-uuid")
       
       # Create comment
       comment = CommentModel(
           post_id="post-uuid",
           guest_name="John Doe",
           guest_email="john@example.com",
           content="Great article!"
       )
       await db.create_comment(comment)
    """
    print("Database models and operations loaded successfully!")
    print("Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables to use.")