from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin for the CustomUser model.
    Extends Django's built-in UserAdmin.
    """
    # Add any custom fields to the admin interface here
    # For example, if you add phone_number field:
    # fieldsets = UserAdmin.fieldsets + (
    #     ('Additional Info', {'fields': ('phone_number', 'date_of_birth', 'bio', 'avatar')}),
    # )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     ('Additional Info', {'fields': ('phone_number', 'date_of_birth', 'bio', 'avatar')}),
    # )
    pass