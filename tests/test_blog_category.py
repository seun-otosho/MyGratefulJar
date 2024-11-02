import unittest

from blog.models import BlogCategory
from django.core.exceptions import ValidationError
from wagtail.images.tests.utils import Image, get_test_image_file


class TestBlogCategory(unittest.TestCase):
    def setUp(self):
        self.category_name = 'test_category'
        self.category_icon = Image.objects.create(title="Test image", file=get_test_image_file())
        self.blog_category = BlogCategory.objects.create(name=self.category_name, icon=self.category_icon)

    def tearDown(self):
        self.blog_category.delete()

    def test_blog_category_creation(self):
        self.assertIsInstance(self.blog_category, BlogCategory)
        self.assertEqual(self.blog_category.__str__(), self.category_name)
        self.assertEqual(self.blog_category.icon, self.category_icon)

    def test_blog_category_long_name(self):
        long_name = 'a' * 256
        with self.assertRaises(ValidationError):
            BlogCategory.objects.create(name=long_name, icon=self.category_icon)

    def test_meta_class(self):
        self.assertEqual(self.blog_category._meta.db_table, 'blog_categories')
        self.assertEqual(self.blog_category._meta.verbose_name_plural, 'Blog Categories')


if __name__ == '__main__':
    unittest.main()
