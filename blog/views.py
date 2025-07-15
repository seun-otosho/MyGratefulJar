from django.http import HttpResponse
from fastcore.xml import to_xml

from blog.components import blog_listing, post_detail
from themes.nemesis.main import MagazineLayout, BaseLayout


def post(request, post_id):
    page = BaseLayout(
        request,
        "Welcome",
        "",
        "item",
        *post_detail(post_id),
    )
    return HttpResponse(to_xml(page), content_type="text/html")


def blog(request):
    # featured_post = next((post for post in sample_posts if post['is_featured']), sample_posts[0])
    page = MagazineLayout(
        request,
        "Blog Magazine",
        "",
        *blog_listing(),
        # slider=hero_slider(featured_post)
    )
    return HttpResponse(to_xml(page), content_type="text/html")
