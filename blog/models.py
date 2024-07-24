from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from modelcluster.models import ClusterableModel

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.search import index
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase


class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        db_table = "blog_categories"
        verbose_name_plural = "Blog Categories"


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    def get_context(self, request):
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context

    class Meta:
        db_table = 'blog_index'


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.DO_NOTHING
    )

    class Meta:
        db_table = 'blog_page_tags'


class BlogPage(Page):
    date = models.DateField("Post date", default=timezone.now, )
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = models.ForeignKey(
        'blog.BlogCategory',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_pages'
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, blank=True, null=True, related_name="+", )

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('categories'),
        FieldPanel('tags'),
        InlinePanel('comments', label="Comments"),
    ]

    def get_context(self, request, *args, **kwargs):
        from .forms import CommentForm
        context = super().get_context(request, *args, **kwargs)
        context['comment_form'] = CommentForm()
        return context

    class Meta:
        db_table = 'blog_pages'


class Comment(models.Model):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=255)
    email = models.EmailField()
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f'Comment by {self.author} on {self.page}'

    class Meta:
        db_table = 'blog_comments'
