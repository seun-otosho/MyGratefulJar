# core/components.py
from django.urls import reverse
from fasthtml.common import *
# This Django utility helps resolve static file paths
from django.templatetags.static import static
from fasthtml.components import Div, Span
from fasthtml.xtend import A

from themes.nemesis.components import blog_post_card
from themes.nemesis.main import BaseLayout
from themes.nemesis.meta import sample_posts
from django.middleware.csrf import get_token


def homepage(request):
    """Homepage route"""
    # Get featured post and regular posts
    regular_posts = [post for post in sample_posts if not post['is_featured']]
    content = [
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
    ]
    return content

# A component to render our contact form
def ContactFormComponent(form, request):
    # We need the request to generate the CSRF token
    csrf_token = get_token(request)
    return Form(
        H2('Contact Us'),
        # Manually add the CSRF token, as we aren't using {% csrf_token %}
        Input(type='hidden', name='csrfmiddlewaretoken', value=csrf_token),
        # Render the form fields. `form.as_p` generates <p>-wrapped fields.
        # `Raw` tells FastHTML to inject the HTML string directly.
        NotStr(form.as_p()),
        # Raw(form.as_p()),
        Button('Submit', type='submit')
    )


# --- ols COMPONENTS ---


def BaseLayout(*children, title: str, request): # Add request as a parameter
    # We can now build the nav dynamically
    if request.user.is_authenticated:
        nav_items = [
            A('Home', href="/"),
            A('Items', href=reverse('item_list')),
            A('About', href=reverse('about')),
            A('Contact', href=reverse('contact')),
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
            A('Home', href="/"),
            A('Items', href=reverse('item_list')),
            A('About', href=reverse('about')),
            A('Contact', href=reverse('contact')),
            A('Login', href=reverse('account_login')),
            A('Sign Up', href=reverse('account_signup'))
        ]

    return Html(
        Head(
            Title(title),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Link(rel="stylesheet", href=static('/css/style.css'))
        ),
        Body(
            Nav(*nav_items), # Use the dynamic nav items
            Main(*children)
        )
    )


# A component to display a list of items
def ItemListPage(items: list[str]):
    return Div(
        H2('A List of Items'),
        Ul(
            # We can use loops directly in our component definition
            *[Li(item) for item in items]
        )
    )

# A simple "About" page
def AboutPage():
    return Div(
        H2('About Us'),
        P('This is a demo project combining Django and FastHTML.')
    )

