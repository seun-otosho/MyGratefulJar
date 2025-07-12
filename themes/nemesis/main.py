from django.urls import reverse
from fasthtml.common import *

from .components import (
    blog_post_card, footer, hero_slider, navbar, newsletter_section, search_overlay, search_form, sidebar)
from .meta import sample_posts

# Custom CSS and JS headers to match the original template
custom_hdrs = [
    Link(rel="shortcut icon", href="/favicon.ico", type="image/x-icon"),
    Link(href="https://fonts.googleapis.com/css?family=Montserrat:900%7CNunito:400,700%7COswald%7CRoboto",
         rel="stylesheet"),
    Link(href="/static/css/animate.min.css", rel="stylesheet", media="screen"),
    Link(href="/static/css/fonts.css", rel="stylesheet", media="screen"),
    Link(href="/static/css/bootstrap.min.css", rel="stylesheet", media="screen"),
    Link(href="/static/css/style.css", rel="stylesheet", media="screen"),
    Script(src="/static/js/jquery.min.js"),
    Script(src="/static/js/bootstrap.bundle.min.js"),
    Script(src="/static/js/plugins.js"),
    Script(src="/static/js/main.js"),
]


def BaseLayout(request, title: str, body_class: str, *children, extra_css=None, extra_js=None):
    if request.user.is_authenticated:
        nav_items = [
            # *unauth_nav_items,
            # A form is the correct way to do a POST for logout
            Form(
                Button(f"Logout ({request.user.username})", type="submit"),
                action=reverse('account_logout'),
                method="post",
                style="display: inline;"
            )
        ]
    else:
        nav_items = [
            # *unauth_nav_items,
            A('Login', href=reverse('account_login')),
            A('Sign Up', href=reverse('account_signup'))
        ]

    return Html(
        Head(
            Title(title),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Link(rel="stylesheet", href="/static/css/config.css", type="text/css"),
            *custom_hdrs,
            # Add extra CSS if provided
            *([Link(rel="stylesheet", href=css) for css in extra_css] if extra_css else []),
        ),
        Body(
            # Nav(*nav_items),  # Use the dynamic nav items
            Main(*children),
            cls=body_class,
        )
    )

def homepage(request):
    """Homepage route"""
    # Get featured post and regular posts
    featured_post = next((post for post in sample_posts if post['is_featured']), sample_posts[0])
    regular_posts = [post for post in sample_posts if not post['is_featured']]

    return BaseLayout(
        request,
        "Nemesis | Minimal Blog HTML Template",
        "",
        search_overlay(),
        search_form(),
        Div(id="page-wrapper", cls="feed-view")(
            navbar(request),
            hero_slider(featured_post),
            Div(cls="outer-wrapper clearfix", id="outer-wrapper")(
                Div(cls="container fbt-elastic-container")(
                    Div(cls="row justify-content-center")(
                        Div(cls="fbt-main-wrapper col-xl-12")(
                            Div(id="main-wrapper")(
                                Div(cls="main-section", id="main_content")(
                                    Div(cls="blog-posts fbt-index-post-wrap card-columns")(
                                        *[blog_post_card(post) for post in regular_posts]
                                    ),
                                    Div(cls="blog-pager", id="blog-pager")(
                                        Div(cls="list-inline")(
                                            A(cls="blog-pager-older-link list-inline-item", href="#",
                                              title="More posts")(
                                                Div(cls="fbt-bp-message text-uppercase font-weight-bold")("More posts"),
                                                Span(aria_hidden="true", cls="fa fa-angle-down")
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        sidebar()
                    )
                )
            ),
            newsletter_section(),
            Div(cls="fbt-bottom-shape")(
                # SVG wave shape
                NotStr('''<svg class="fbt-footer-wave-big" preserveAspectRatio="none" version="1.1" viewBox="5 0 1366 222" width="100%">
                    <path d="M-2.19,238H1366v-4.27c-67.87-24-146.44-43.08-230.75-53.19-253.33-27.78-293.94,51.64-541.13,29.89C318.08,186.31,289.49,32.92,6.9,11.73c-5.21-.42-10.56-.7-15.9-1V238Z" transform="translate(9.5 -10.22)"></path>
                </svg>''')
            ),
            footer()
        )
    )
