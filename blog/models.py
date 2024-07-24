from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from modelcluster.models import ClusterableModel
# from wagtail.admin.panels import FieldPanel, MultiFieldPanel
# from wagtail.fields import RichTextField, StreamField
# from wagtail.models import Page
# from wagtail.search import index


# class BlogIndexPage(Page):
#     intro = RichTextField(blank=True)

#     content_panels = Page.content_panels + [FieldPanel('intro'), ]

#     class Meta:
#         db_table = "blog"


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'Post',
        related_name='tagged_items',
        on_delete=models.DO_NOTHING
    )

    class Meta:
        db_table = 'blog_page_tags'


# class BlogPage(Page):
#     intro = models.CharField(max_length=256)
#     # body = RichTextField(blank=True)
#     body = StreamField(
#         BlogStreamBlock(),
#         blank=True,
#         use_json_field=True,
#         help_text="Use this section to express your gratefulness.",
#     )

class Post(ClusterableModel, models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, blank=True, null=True, related_name="+", )
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    # tags = models.ManyToManyField(BlogPageTag, blank=True)

    # date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

