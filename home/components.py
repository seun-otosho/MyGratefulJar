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

def contact_hero_section():
    """Contact page hero section with background image"""
    return Div(cls="slider-container")(
        Div(cls="row align-items-center")(
            Div(cls="col-lg-12")(
                Div(cls="fbt-shape-container card shadow-none")(
                    Div(cls="fbt-item-thumbnail radius-10")(
                        Img(alt="Contact Us", cls="post-thumbnail", src="/static/images/page-img-1.jpg")
                    ),
                    Div(cls="card-img-overlay radius-10")(
                        Div(cls="fbt-page-shape-title d-table w-100")(
                            Div(cls="d-table-cell align-middle")(
                                Div(cls="row justify-content-center")(
                                    Div(cls="col-xl-8 col-lg-9 p-0")(
                                        H1(cls="post-title display-4 text-white text-center")("Contact Us")
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )

def contact_form():
    """Contact form component"""
    return Form(id="fbt-contact-form", cls="contact-form", method="POST", action="/contact")(
        Div(cls="row")(
            Div(cls="col-md-9")(
                Div(cls="form-group")(
                    Label(**{"for": "name"})("Name*"),
                    Input(cls="form-control shadow-none radius-0", id="name", name="name", type="text", required=True)
                )
            ),
            Div(cls="col-md-9")(
                Div(cls="form-group")(
                    Label(**{"for": "email"})("E-mail*"),
                    Input(cls="form-control shadow-none radius-0", id="email", name="email", type="email", required=True)
                )
            ),
            Div(cls="col-md-9")(
                Div(cls="form-group")(
                    Label(**{"for": "website"})("Website"),
                    Input(cls="form-control shadow-none radius-0", id="website", name="website", type="url")
                )
            )
        ),
        Div(cls="row mb-4")(
            Div(cls="col-md-12")(
                Div(cls="form-group")(
                    Label(**{"for": "message"})("Message*"),
                    Textarea(cls="form-control shadow-none radius-0", rows="9", id="message", name="message", required=True)
                )
            )
        ),
        Button(cls="btn btn-success radius-0", type="submit", id="submit-contact")(
            I(cls="fa fa-paper-plane-o mr-2"),
            "Submit Message"
        )
    )

def contact_info_sidebar():
    """Contact information sidebar"""
    return Div(cls="col-xl-3 col-lg-4 pl-lg-5 order-1 order-lg-2")(
        Div(cls="fbt-sep-title")(
            H4(cls="title title-heading-left")("Contact Us"),
            Div(cls="title-sep-container")(
                Div(cls="title-sep sep-double")
            )
        ),
        P(cls="mb-4")(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Ut porttitor leo vel nulla posuere accumsan. "
            "Suspendisse sed tortor eget justo aliquam euismod. "
            "Morbi ut massa et neque iaculis lacinia a eu..."
        ),
        Div(cls="fbt-contact-info")(
            # Address
            Div(cls="fbt-contact-info-box")(
                Div(cls="fbt-contact-info-box-content")(
                    Div(cls="fbt-sep-title")(
                        H4(cls="title title-heading-left")("Webagency"),
                        Div(cls="title-sep-container")(
                            Div(cls="title-sep sep-double")
                        )
                    ),
                    P("Vouliagmenis Ave 325,", Br(), "Athens CA 17575")
                )
            ),
            # Email
            Div(cls="fbt-contact-info-box")(
                Div(cls="fbt-contact-info-box-content")(
                    Div(cls="fbt-sep-title")(
                        H4(cls="title title-heading-left")("Email Us"),
                        Div(cls="title-sep-container")(
                            Div(cls="title-sep sep-double")
                        )
                    ),
                    P("info@nemesis.com")
                )
            ),
            # Phone
            Div(cls="fbt-contact-info-box")(
                Div(cls="fbt-contact-info-box-content")(
                    Div(cls="fbt-sep-title")(
                        H4(cls="title title-heading-left")("Call Us"),
                        Div(cls="title-sep-container")(
                            Div(cls="title-sep sep-double")
                        )
                    ),
                    P("+123-456-7890")
                )
            )
        )
    )

def contact_page():
    """Contact page with form and information"""
    return Div(cls="blog-posts fbt-item-post-wrap")(
        Div(cls="blog-post fbt-item-post")(
            contact_hero_section(),
            Div(cls="row justify-content-center")(
                Div(cls="col-xl-8 col-lg-8 order-2 order-lg-1 mt-4 mt-lg-0")(
                    contact_form()
                ),
                contact_info_sidebar()
            )
        )
    )

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
        # NotStr(form.as_div()),
        form,
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

