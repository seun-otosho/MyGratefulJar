# from django.template.defaulttags import load
# from django.templatetags import static
# from fastcore.xml import Html
from fasthtml.common import *
# from wagtail.admin.templatetags import wagtailuserbar
# from wagtail.templatetags import wagtailcore_tags


# from fasthtml.components import Head, Title, Meta, Link, Body, Div
# from fasthtml.xtend import Script


def create_404_page():
    """Create a 404 error page in FastHTML"""
    content = Div(
        H1("Page not found"),
        H2("Sorry, this page could not be found."),
    )
    return base_template(
        title="Page not found",
        body_class="template-404",
        content=content
    )

def create_500_page():
    """Create a 500 error page in FastHTML"""
    content = Div(
        H1("Internal server error"),
        H2("Sorry, there seems to be an error. Please try again soon."),
    )
    return base_template(
        title="Internal server error",
        body_class="template-500",
        content=content
    )

# # Usage in your FastHTML app
# app = FastHTML()
#
# @app.get("/404")
# def not_found():
#     return create_404_page()

# @load static wagtailcore_tags wagtailuserbar
def base_template(title="", body_class="", content=None, extra_css=None, extra_js=None):
    """Base template for all pages"""
    return Html(
        Head(
            Title(title or "My Wagtail Site"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Link(rel="stylesheet", href="/static/css/config.css", type="text/css"),
            # Add extra CSS if provided
            *([Link(rel="stylesheet", href=css) for css in extra_css] if extra_css else []),
        ),
        Body(
            content or Div("No content provided"),
            cls=body_class,
            # Add extra JS if provided
            *([Script(src=js) for js in extra_js] if extra_js else []),
            )
    )
