from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting
from wagtail.contrib.settings.registry import register_setting


@register_setting
class FooterLinks(BaseGenericSetting):
    facebook = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedIn = models.URLField(blank=True, null=True)
    x = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)

    panels = [
        FieldPanel('github'),
        FieldPanel('linkedIn'),
        FieldPanel('x'),
        FieldPanel('youtube'),
    ]


@register_setting
class BrandSettings(BaseGenericSetting):
    # name = models.CharField(max_length=256)
    logo = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True, related_name="+",)

