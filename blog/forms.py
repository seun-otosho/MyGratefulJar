from django import forms
from .models import Comment, BlogPage


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-2 border rounded'}),
        }


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPage
        fields = ('title', 'intro', 'body', )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'intro': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'body': forms.Textarea(attrs={'rows': 10, 'class': 'w-full p-2 border rounded'}),
        }
