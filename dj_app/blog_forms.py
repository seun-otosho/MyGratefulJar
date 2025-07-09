from django import forms
from django.core.validators import EmailValidator
from .models import Comment, ContactSubmission, NewsletterSubscriber, Post


class ContactForm(forms.ModelForm):
    """Contact form for website visitors"""
    
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'website', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'required': True
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Website (optional)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your Message',
                'rows': 5,
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['message'].required = True


class CommentForm(forms.ModelForm):
    """Comment form for blog posts"""
    
    class Meta:
        model = Comment
        fields = ['content', 'guest_name', 'guest_email', 'guest_website']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your comment here...',
                'rows': 4,
                'required': True
            }),
            'guest_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'guest_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email'
            }),
            'guest_website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Website (optional)'
            })
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        if user and user.is_authenticated:
            # Hide guest fields for authenticated users
            self.fields['guest_name'].widget = forms.HiddenInput()
            self.fields['guest_email'].widget = forms.HiddenInput()
            self.fields['guest_website'].widget = forms.HiddenInput()
        else:
            # Require guest fields for anonymous users
            self.fields['guest_name'].required = True
            self.fields['guest_email'].required = True
    
    def save(self, commit=True):
        comment = super().save(commit=False)
        
        if self.user and self.user.is_authenticated:
            comment.user = self.user
        
        if commit:
            comment.save()
        
        return comment


class NewsletterForm(forms.ModelForm):
    """Newsletter subscription form"""
    
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email already exists
        if NewsletterSubscriber.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already subscribed to our newsletter.")
        
        return email


class PostSearchForm(forms.Form):
    """Search form for blog posts"""
    
    query = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...',
            'type': 'search'
        }),
        required=True
    )
    
    category = forms.ModelChoiceField(
        queryset=None,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        self.fields['category'].queryset = Category.objects.filter(is_active=True)


class PostFilterForm(forms.Form):
    """Filter form for blog listing"""
    
    category = forms.ModelChoiceField(
        queryset=None,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    
    tag = forms.ModelChoiceField(
        queryset=None,
        empty_label="All Tags",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('latest', 'Latest'),
            ('oldest', 'Oldest'),
            ('popular', 'Most Popular'),
            ('commented', 'Most Commented'),
        ],
        initial='latest',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category, Tag
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['tag'].queryset = Tag.objects.all()
