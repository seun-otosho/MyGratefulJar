from django import forms
from django.conf import settings
from django.db import models
from django.utils import timezone
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail.search import index

# User = get_user_model()

class PostAnalytics(models.Model):
    post = models.OneToOneField('BlogPage', on_delete=models.CASCADE, related_name='analytics')
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    shares = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Post analytics'

    def __str__(self):
        return f'Analytics for {self.post.title}'

class Share(models.Model):
    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('tiktok', 'TikTok'),
        ('threads', 'Threads'),
    )

    post = models.ForeignKey('BlogPage', on_delete=models.CASCADE, related_name='share_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user', 'platform')

class BlogCategory(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=88)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
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
    intro = models.CharField(max_length=256)
    body = RichTextField(blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = models.ManyToManyField(
        'blog.BlogCategory',
        # null=True,
        blank=True,
        # on_delete=models.SET_NULL,
        related_name='blog_pages'
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, blank=True, null=True, related_name="+", )

    # Draft-publish workflow
    is_published = models.BooleanField(default=False)

    # Social media sharing settings
    share_to_facebook = models.BooleanField(default=False)
    share_to_twitter = models.BooleanField(default=False)
    share_to_instagram = models.BooleanField(default=False)
    share_to_tiktok = models.BooleanField(default=False)
    share_to_threads = models.BooleanField(default=False)

    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('pending', 'Pending Moderation'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='draft'
    )

    moderation_notes = models.TextField(blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_posts'
    )

    @property
    def like_count(self):
        return self.analytics.likes.count() if hasattr(self, 'analytics') else 0

    @property
    def share_count(self):
        return self.analytics.shares if hasattr(self, 'analytics') else 0

    def increase_view_count(self):
        analytics, created = PostAnalytics.objects.get_or_create(post=self)
        analytics.views += 1
        analytics.save()

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            # FieldPanel('author'),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
            FieldPanel('tags'),
        ], heading="Blog information"),
        # FieldPanel('featured_image'),
        FieldPanel('intro'),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('share_to_facebook'),
            FieldPanel('share_to_twitter'),
            FieldPanel('share_to_instagram'),
            FieldPanel('share_to_tiktok'),
        ], heading="Social Media Sharing"),
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
    author = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, related_name='comments')
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


