from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

User = get_user_model()

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
        FieldPanel('image'),
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

    # def save(self, *args, **kwargs):
    #     # self.owner = request.user
    #     super().save(*args, **kwargs)

    class Meta:
        db_table = 'blog_pages'

    # def save(self, clean=True, user=None, log_action=False, **kwargs):
    #     if not self.slug:
    #         self.slug = self.title.replace(" ", "-")
    #     return super().save(self, clean=True, user=None, log_action=False, **kwargs)


class Comment(models.Model):
    page = ParentalKey(BlogPage, on_delete=models.DO_NOTHING, related_name='comments')
    author = models.ForeignKey(User, models.DO_NOTHING, related_name='comments')
    email = models.EmailField()
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='replies')

    @property
    def children(self):
        return Comment.objects.filter(parent=self).order_by('created_date')

    @property
    def is_parent(self):
        return self.parent is None

    def __str__(self):
        return f'Comment by {self.author} on {self.page}'

    class Meta:
        db_table = 'blog_comments'
        ordering = ['created_date']


