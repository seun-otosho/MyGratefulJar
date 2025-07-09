from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    User, Category, Tag, Post, Comment, ContactSubmission,
    NewsletterSubscriber, MediaUpload, SiteSetting
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom User model"""
    
    list_display = ('username', 'email', 'display_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'email_verified', 'created_at')
    search_fields = ('username', 'email', 'display_name')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('display_name', 'bio', 'avatar_url', 'website_url', 'role', 'email_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model"""
    
    list_display = ('name', 'slug', 'color_display', 'post_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Appearance', {
            'fields': ('color', 'icon')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('post_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('post_count', 'created_at', 'updated_at')
    
    def color_display(self, obj):
        if obj.color:
            return format_html(
                '<span style="background-color: {}; padding: 2px 6px; border-radius: 3px; color: white;">{}</span>',
                obj.color,
                obj.color
            )
        return '-'
    color_display.short_description = 'Color'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin for Tag model"""
    
    list_display = ('name', 'slug', 'post_count', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    
    readonly_fields = ('post_count', 'created_at')


class PostTagInline(admin.TabularInline):
    """Inline for Post tags"""
    model = Post.tags.through
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin for Post model"""
    
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'published_at', 'view_count')
    list_filter = ('status', 'is_featured', 'is_video_post', 'category', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image_url', 'featured_image_alt', 'is_video_post')
        }),
        ('Relationships', {
            'fields': ('author', 'category', 'tags')
        }),
        ('Publishing', {
            'fields': ('status', 'is_featured', 'published_at', 'scheduled_for')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('view_count', 'like_count', 'comment_count', 'share_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('view_count', 'like_count', 'comment_count', 'share_count', 'created_at', 'updated_at')
    filter_horizontal = ('tags',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')
    
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for Comment model"""
    
    list_display = ('commenter_name', 'post', 'status', 'is_reply', 'created_at')
    list_filter = ('status', 'is_pinned', 'created_at')
    search_fields = ('content', 'guest_name', 'guest_email', 'post__title')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('post', 'parent', 'content', 'status', 'is_pinned')
        }),
        ('Commenter Info', {
            'fields': ('user', 'guest_name', 'guest_email', 'guest_website')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('post', 'user', 'parent')
    
    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    """Admin for ContactSubmission model"""
    
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'website', 'subject', 'message', 'status')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    """Admin for NewsletterSubscriber model"""
    
    list_display = ('email', 'status', 'source', 'created_at')
    list_filter = ('status', 'source', 'created_at')
    search_fields = ('email',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('email', 'status', 'source')
        }),
        ('Subscription Details', {
            'fields': ('confirmed_at', 'unsubscribed_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MediaUpload)
class MediaUploadAdmin(admin.ModelAdmin):
    """Admin for MediaUpload model"""
    
    list_display = ('filename', 'mime_type', 'file_size', 'uploaded_by', 'post', 'created_at')
    list_filter = ('mime_type', 'uploaded_by', 'created_at')
    search_fields = ('filename', 'original_filename', 'alt_text', 'caption')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('filename', 'original_filename', 'file_path', 'file_url')
        }),
        ('Media Details', {
            'fields': ('file_size', 'mime_type', 'width', 'height', 'alt_text', 'caption')
        }),
        ('Relationships', {
            'fields': ('uploaded_by', 'post')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('uploaded_by', 'post')


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    """Admin for SiteSetting model"""
    
    list_display = ('setting_key', 'setting_type', 'is_public', 'updated_at')
    list_filter = ('setting_type', 'is_public', 'updated_at')
    search_fields = ('setting_key', 'setting_value', 'description')
    ordering = ('setting_key',)
    
    fieldsets = (
        (None, {
            'fields': ('setting_key', 'setting_value', 'setting_type', 'description', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


# Admin customizations
admin.site.site_header = 'Nemesis Blog Administration'
admin.site.site_title = 'Nemesis Blog Admin'
admin.site.index_title = 'Welcome to Nemesis Blog Administration'
