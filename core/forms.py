from django import forms
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from wagtail.users.forms import UserEditForm, UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    country = CountryField().formfield()


class CustomUserEditForm(UserEditForm):
    country = forms.CharField(required=True, label=_("Country"))
