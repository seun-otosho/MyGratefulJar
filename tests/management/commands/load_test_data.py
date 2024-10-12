from django.core.management.base import BaseCommand
from blog.factories import BlogCategoryFactory, BlogPageFactory, CommentFactory


class Command(BaseCommand):
    help = 'Load test data into the database'

    def handle(self, *args, **kwargs):
        BlogCategoryFactory.create_batch(5)
        BlogPageFactory.create_batch(10)
        for _ in range(20):
            CommentFactory.create()
        self.stdout.write(self.style.SUCCESS('Successfully loaded test data'))
