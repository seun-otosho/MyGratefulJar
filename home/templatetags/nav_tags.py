from django import template
from wagtail.models import Page

register = template.Library()


@register.simple_tag
def get_navs() -> list:
    # return Page.objects.live().public().in_menu().filter(depth__gt=2)
    return Page.objects.live().public().in_menu().filter(depth__gt=2)
