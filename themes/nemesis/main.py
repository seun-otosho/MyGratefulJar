from django.urls import reverse
from fasthtml.common import *

from .components import (
    footer, hero_slider, navbar, newsletter_section, search_overlay, search_form, sidebar)
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


def BaseLayout(request, title: str, body_class: str, *children, slider=None, extra_css=None, extra_js=None):
    if request.user.is_authenticated:
        pass
    else:
        pass

    return Html(
        Head(
            Title(title + " - My Grateful Jar" if title else "My Grateful Jar" ),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Link(rel="stylesheet", href="/static/css/config.css", type="text/css"),
            *custom_hdrs,
            # Add extra CSS if provided
            *([Link(rel="stylesheet", href=css) for css in extra_css] if extra_css else []),
        ),
        Body(
            search_overlay(),
            search_form(),
            Div(id="page-wrapper", cls="feed-view")(
                navbar(request),
                slider if slider else "",
                Div(cls="outer-wrapper clearfix", id="outer-wrapper")(
                    Div(cls="container fbt-elastic-container")(
                        Div(cls="row justify-content-center")(
                            Div(cls="fbt-main-wrapper col-xl-12")(
                                Div(id="main-wrapper")(
                                    Div(cls="main-section", id="main_content")(
                                        Main(*children),
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
            ),
            cls=body_class,
        )
    )
