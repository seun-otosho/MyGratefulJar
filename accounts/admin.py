from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom User model"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(Profile)
class ProfileAdmin(BaseUserAdmin):
    """Admin for Profile model (extends User)"""
    
    list_display = ('username', 'email', 'display_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'email_verified', 'created_at')
    search_fields = ('username', 'email', 'display_name')
    ordering = ('-created_at',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('display_name', 'bio', 'avatar_url', 'website_url', 'role', 'email_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = BaseUserAdmin.readonly_fields + ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request)