import unittest

from blog.models import BlogPageTag
from django.core.exceptions import ValidationError
from django.test import TestCase


class TestBlogPageTag(TestCase):
    def setUp(self):
        """ Let's set up the environment for the tests """
        self.blog_tag = BlogPageTag.objects.create(name="Test Tag")

    def test_create_blog_tag(self):
        """ Test if the tag has been created """
        self.assertEqual(BlogPageTag.objects.count(), 1)

    def test_blog_tag_name(self):
        """ Test if the tag name is correct """
        self.assertEqual(self.blog_tag.name, "Test Tag")

    def test_blog_tag_content_object(self):
        """ Test if the tag content object is None by default """
        self.assertIsNone(self.blog_tag.content_object)

    def test_blog_tag_on_delete(self):
        """ Test if the tag has DO_NOTHING on_delete policy """
        self.assertEqual(self.blog_tag._meta.get_field('content_object').remote_field.on_delete, models.DO_NOTHING)

    def test_blog_tag_db_table(self):
        """ Test the name of the database table """
        self.assertEqual(self.blog_tag._meta.db_table, 'blog_page_tags')


if __name__ == '__main__':
    unittest.main()
