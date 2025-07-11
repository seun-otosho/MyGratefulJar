import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.postgres.search import SearchVector
from django.core.validators import EmailValidator


class User(AbstractUser):
    """Extended user model for blog authors and commenters"""
    
    class UserRole(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        EDITOR = 'editor', 'Editor'
        AUTHOR = 'author', 'Author'
        USER = 'user', 'User'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.USER)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.display_name or self.username


class Category(models.Model):
    """Blog post categories"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, blank=True, help_text="Hex color code")
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    post_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})


class Tag(models.Model):
    """Blog post tags"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    post_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:tag', kwargs={'slug': self.slug})


class Post(models.Model):
    """Blog post model"""
    
    class PostStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'
        SCHEDULED = 'scheduled', 'Scheduled'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(blank=True, help_text="Short description for cards/listings")
    content = models.TextField(help_text="Full post content (HTML/Markdown)")
    featured_image_url = models.URLField(blank=True)
    featured_image_alt = models.CharField(max_length=255, blank=True)
    
    # Relationships
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=PostStatus.choices, default=PostStatus.DRAFT)
    is_featured = models.BooleanField(default=False, help_text="For hero slider")
    is_video_post = models.BooleanField(default=False)
    
    # SEO fields
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    
    # Engagement metrics
    view_count = models.IntegerField(default=0)
    like_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    
    # Timestamps
    published_at = models.DateTimeField(null=True, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['published_at']),
            models.Index(fields=['author']),
            models.Index(fields=['category']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['slug']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-set published_at when status changes to published
        if self.status == self.PostStatus.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    @property
    def author_name(self):
        return self.author.display_name or self.author.username if self.author else "Anonymous"
    
    @property
    def author_avatar(self):
        return self.author.avatar_url if self.author else ""
    
    @property
    def category_name(self):
        return self.category.name if self.category else ""
    
    @property
    def category_slug(self):
        return self.category.slug if self.category else ""
    
    @property
    def category_color(self):
        return self.category.color if self.category else ""
    
    def get_tags_list(self):
        return list(self.tags.all())
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class Comment(models.Model):
    """Hierarchical comments system"""
    
    class CommentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        SPAM = 'spam', 'Spam'
        TRASH = 'trash', 'Trash'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Commenter information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    guest_name = models.CharField(max_length=100, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_website = models.URLField(blank=True)
    
    # Content
    content = models.TextField()
    
    # Moderation
    status = models.CharField(max_length=20, choices=CommentStatus.choices, default=CommentStatus.PENDING)
    is_pinned = models.BooleanField(default=False)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['parent']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.commenter_name} on {self.post.title}"
    
    @property
    def commenter_name(self):
        if self.user:
            return self.user.display_name or self.user.username
        return self.guest_name or "Anonymous"
    
    @property
    def commenter_avatar(self):
        if self.user:
            return self.user.avatar_url
        return ""
    
    @property
    def is_reply(self):
        return self.parent is not None
    
    def get_replies(self):
        return self.replies.filter(status=self.CommentStatus.APPROVED)


class ContactSubmission(models.Model):
    """Contact form submissions"""
    
    class ContactStatus(models.TextChoices):
        NEW = 'new', 'New'
        READ = 'read', 'Read'
        REPLIED = 'replied', 'Replied'
        ARCHIVED = 'archived', 'Archived'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.URLField(blank=True)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    
    # Status tracking
    status = models.CharField(max_length=20, choices=ContactStatus.choices, default=ContactStatus.NEW)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Contact from {self.name} - {self.subject}"


class NewsletterSubscriber(models.Model):
    """Newsletter subscription"""
    
    class SubscriberStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        UNSUBSCRIBED = 'unsubscribed', 'Unsubscribed'
        BOUNCED = 'bounced', 'Bounced'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=20, choices=SubscriberStatus.choices, default=SubscriberStatus.ACTIVE)
    
    # Subscription metadata
    source = models.CharField(max_length=50, blank=True, help_text="footer_form, popup, etc.")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Email preferences
    confirmed_at = models.DateTimeField(null=True, blank=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.status})"


class MediaUpload(models.Model):
    """Track uploaded images and files"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file_path = models.TextField()
    file_url = models.URLField()
    file_size = models.IntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True)
    alt_text = models.TextField(blank=True)
    caption = models.TextField(blank=True)
    
    # Relationships
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Image metadata
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.filename


class SiteSetting(models.Model):
    """Global site configuration"""
    
    class SettingType(models.TextChoices):
        TEXT = 'text', 'Text'
        NUMBER = 'number', 'Number'
        BOOLEAN = 'boolean', 'Boolean'
        JSON = 'json', 'JSON'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    setting_key = models.CharField(max_length=100, unique=True)
    setting_value = models.TextField(blank=True)
    setting_type = models.CharField(max_length=20, choices=SettingType.choices, default=SettingType.TEXT)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False, help_text="Can be accessed by frontend")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['setting_key']
    
    def __str__(self):
        return self.setting_key


# Signal handlers to update counts
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Post)
def update_category_post_count_on_save(sender, instance, **kwargs):
    if instance.category:
        instance.category.post_count = instance.category.posts.filter(status=Post.PostStatus.PUBLISHED).count()
        instance.category.save(update_fields=['post_count'])

@receiver(post_delete, sender=Post)
def update_category_post_count_on_delete(sender, instance, **kwargs):
    if instance.category:
        instance.category.post_count = instance.category.posts.filter(status=Post.PostStatus.PUBLISHED).count()
        instance.category.save(update_fields=['post_count'])

@receiver(post_save, sender=Comment)
def update_post_comment_count_on_save(sender, instance, **kwargs):
    if instance.post:
        instance.post.comment_count = instance.post.comments.filter(status=Comment.CommentStatus.APPROVED).count()
        instance.post.save(update_fields=['comment_count'])

@receiver(post_delete, sender=Comment)
def update_post_comment_count_on_delete(sender, instance, **kwargs):
    if instance.post:
        instance.post.comment_count = instance.post.comments.filter(status=Comment.CommentStatus.APPROVED).count()
        instance.post.save(update_fields=['comment_count'])
