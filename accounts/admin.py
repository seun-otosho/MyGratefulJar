from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    """Inline admin for Profile model"""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('display_name', 'bio', 'avatar_url', 'website_url', 'role')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for custom User model"""
    
    inlines = [ProfileInline]
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    # Use the base UserAdmin fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': (),  # Profile fields will be handled by the inline
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


# Alternative approach if you want to register Profile separately
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin for Profile model"""
    
    list_display = ('user', 'display_name', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'display_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Profile Information', {
            'fields': ('user', 'display_name', 'bio', 'avatar_url', 'website_url', 'role')
        }),
        ('Verification', {
            'fields': ('email_verified',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')