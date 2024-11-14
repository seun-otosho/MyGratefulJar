from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from wagtail.contrib.forms.models import AbstractFormField, AbstractEmailForm
from wagtail.contrib.settings.models import BaseGenericSetting

USERNAME_REGEX = '^[a-zA-Z0-9.@_]*$'


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        user.is_active = True
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password=None):
        """
        Creates and saves a superuser with the given email, date of birth and password.
        """
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        user.is_active = user.is_admin = user.is_staff = user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractUser, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        db_index=True, verbose_name=_('username'), max_length=50, unique=True,
        validators=[RegexValidator(regex=USERNAME_REGEX,
                                   message="Username must be Alpha-Numeric and may also contain '.', '@' and '_'.",
                                   code='Invalid Username.')])
    # date_of_birth = models.DateField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False, db_index=True, )
    is_superuser = models.BooleanField(default=False, db_index=True, )


    # Additional fields for user profile
    bio = models.TextField(max_length=500, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    website = models.URLField(max_length=200, blank=True)

    # Social media fields
    facebook_profile = models.URLField(blank=True)
    twitter_profile = models.URLField(blank=True)
    instagram_profile = models.URLField(blank=True)
    tiktok_profile = models.URLField(blank=True)
    threads_profile = models.URLField(blank=True)

    # Sharing preferences
    auto_share = models.BooleanField(default=False)

    # Social media tokens (encrypted)
    facebook_token = models.CharField(max_length=255, blank=True)
    twitter_token = models.CharField(max_length=255, blank=True)
    instagram_token = models.CharField(max_length=255, blank=True)
    tiktok_token = models.CharField(max_length=255, blank=True)

    country = CountryField()

    def __str__(self):
        return self.get_full_name() if self.get_full_name() != "" else self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'

