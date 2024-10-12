import unittest
from datetime import datetime
import os

from django import setup
from django.db.models import QuerySet

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
setup()

import pytest
import factory
from django.urls import reverse
from blog.models import Comment, BlogPage
from django.contrib.auth import get_user_model
from factory import SubFactory, Faker

User = get_user_model()

# Define factories
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = Faker('user_name')
    email = Faker('email')


class BlogPageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BlogPage  # Assuming BlogPage is a model in your project

    title = Faker('sentence')


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    page = SubFactory(BlogPageFactory)
    author = SubFactory(UserFactory)
    email = Faker('email')
    content = Faker('text')
    approved = False
    parent = None


# Define unit tests
@pytest.mark.django_db
def test_comment_creation():
    comment = CommentFactory()
    assert comment is not None
    assert comment.page is not None
    assert comment.author is not None
    assert isinstance(comment.children, QuerySet)  # Check children property

@pytest.mark.django_db
def test_comment_str():
    comment = CommentFactory()
    assert str(comment) == f'Comment by {comment.author} on {comment.page}'

@pytest.mark.django_db
def test_is_parent_property():
    parent_comment = CommentFactory()
    child_comment = CommentFactory(parent=parent_comment)

    assert parent_comment.is_parent is True
    assert child_comment.is_parent is False
