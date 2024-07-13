from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro')
    ]

    class Meta:
        db_table = "blog"


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.DO_NOTHING
    )

    class Meta:
        db_table = 'blog_page_tags'


class BlogPage(Page):
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, blank=True, null=True, related_name="+",)
    date = models.DateTimeField(auto_now_add=True)
    intro = models.CharField(max_length=256)
    body = RichTextField(blank=True)

    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            # FieldPanel('date'),
            # FieldPanel('authors', widget=forms.CheckboxSelectMultiple),

            # Add this:
            FieldPanel('tags'),
        ], heading="Blog information"),
        FieldPanel('body'),
        FieldPanel('image'),
        FieldPanel('intro'),
    ]

    class Meta:
        db_table = "blog_pages"
        verbose_name = "Blog Page"
