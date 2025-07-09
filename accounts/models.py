import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    You can add additional fields here as needed.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Example additional fields (uncomment and modify as needed):
    # bio = models.TextField(max_length=500, blank=True)
    # avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'


class Profile(User):
    """Extended user model for blog authors and commenters"""

    class UserRole(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        EDITOR = 'editor', 'Editor'
        AUTHOR = 'author', 'Author'
        USER = 'user', 'User'

    display_name = models.CharField(max_length=100, blank=True)
    # phone_number = models.CharField(max_length=20, blank=True, null=True)
    # date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.USER)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.username

    class Meta:
        db_table = 'profiles'
