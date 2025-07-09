from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    You can add additional fields here as needed.
    """
    # Example additional fields (uncomment and modify as needed):
    # phone_number = models.CharField(max_length=20, blank=True, null=True)
    # date_of_birth = models.DateField(blank=True, null=True)
    # bio = models.TextField(max_length=500, blank=True)
    # avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    def __str__(self):
        return self.username