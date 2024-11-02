import unittest

from blog import models
from blog.models import BlogPage, BlogCategory, BlogPageTag
from django.test import TestCase, RequestFactory
from django.utils import timezone

from wagtail.images.models import Image


class TestBlogPage(TestCase):

    def setUp(self):
        self.blog_page = BlogPage.objects.create(
            title="Test",
            slug="test",
            date=timezone.now(),
            intro="Intro test",
            body="Body test",
            categories=BlogCategory.objects.create(name='cat1'),
        )

    def test_intro(self):
        self.assertEqual(self.blog_page.intro, "Intro test")

    def test_body(self):
        self.assertEqual(self.blog_page.body, "Body test")

    def test_date(self):
        self.assertEqual(self.blog_page.date, timezone.now().date())

    def test_str_representation(self):
        self.assertEqual(str(self.blog_page), self.blog_page.title)

    def test_get_context(self):
        request = RequestFactory().get("/")
        context = self.blog_page.get_context(request)
        self.assertIn('comment_form', context)


if __name__ == "__main__":
    unittest.main()
