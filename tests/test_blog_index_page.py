import unittest
from unittest.mock import MagicMock

from blog.models import BlogIndexPage


class TestBlogIndexPage(unittest.TestCase):

    def setUp(self):
        self.blog_index_page = BlogIndexPage()

    def test_intro_field(self):
        self.assertTrue(hasattr(self.blog_index_page, "intro"))

    def test_get_context(self):
        request = MagicMock()
        super_get_context_return_val = {'dummy_key': 'dummy_val'}
        self.blog_index_page.get_context = MagicMock(return_value=super_get_context_return_val)
        self.blog_index_page.get_children = MagicMock()
        blogpages = ['blogpage1', 'blogpage2']
        self.blog_index_page.get_children().live().order_by = MagicMock(return_value=blogpages)

        expected_context = super_get_context_return_val
        expected_context['blogpages'] = blogpages

        context = self.blog_index_page.get_context(request)

        self.assertDictEqual(context, expected_context)

    def test_meta_db_table(self):
        self.assertEqual(self.blog_index_page.Meta.db_table, 'blog_index')


if __name__ == '__main__':
    unittest.main()
