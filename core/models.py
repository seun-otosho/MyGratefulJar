from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.forms.models import AbstractFormField, AbstractEmailForm
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.contrib.settings.models import BaseGenericSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.fields import RichTextField

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


class FormField(AbstractFormField):
    page = ParentalKey('ContactPage', on_delete=models.DO_NOTHING, related_name='form_fields')


class ContactPage(AbstractEmailForm):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('intro'),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address'),
                FieldPanel('to_address'),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]

    template = "core/nemesis/email_form_page.html"

    def get_landing_page_template(self, *args, **kwargs):
        return "core/nemesis/email_form_page_landing.html"


@register_setting
class SocialMediaLinks(BaseGenericSetting):
    facebook = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedIn = models.URLField(blank=True, null=True)
    x = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)

    panels = [
        FieldPanel('github'),
        FieldPanel('linkedIn'),
        FieldPanel('x'),
        FieldPanel('youtube'),
    ]

    class Meta:
        db_table = "social_media"
        verbose_name = "Social Media"


@register_setting
class BrandSettings(BaseGenericSetting):
    # name = models.CharField(max_length=256)
    logo = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True, related_name="+",)

    class Meta:
        db_table = "brand"
