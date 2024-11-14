from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from allauth.account.forms import SignupForm
User = get_user_model()

from wagtail.users.forms import UserEditForm, UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    country = CountryField().formfield()


class CustomUserEditForm(UserEditForm):
    country = forms.CharField(required=True, label=_("Country"))



class CustomSignupForm(SignupForm):
    # first_name = forms.CharField(max_length=30, label='First Name')
    # last_name = forms.CharField(max_length=30, label='Last Name')

    def save(self, request):
        # user = super(CustomSignupForm, self).save(request)
        # user.first_name = self.cleaned_data['first_name']
        # user.last_name = self.cleaned_data['last_name']
        # user.save()
        return super(CustomSignupForm, self).save(request)

class SocialMediaSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'auto_share',
            'facebook_profile',
            'twitter_profile',
            'instagram_profile',
            'tiktok_profile',
            'threads_profile',
        ]
