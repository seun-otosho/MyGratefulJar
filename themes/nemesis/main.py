from fasthtml.common import *

from .components import (
    footer, navbar, newsletter_section, search_overlay, search_form, sidebar, headline_section, magazine_navbar,
    gallery_section, custom_hdrs, wave
)
from .meta import sample_posts


# Custom CSS and JS headers to match the original template


def Base(request, title: str, body_class: str, page_class: str, *children, slider=None, extra_css=None, extra_js=None):
    if request.user.is_authenticated:
        pass
    else:
        pass

    return Html(
        Head(
            Title(title + " - My Grateful Jar" if title else "My Grateful Jar"),
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

            Div(id="page-wrapper", cls=("%s-view" % page_class))(
                navbar(request),
                slider if slider else "",
                Div(cls="outer-wrapper clearfix", id="outer-wrapper")(
                    Div(cls="container fbt-elastic-container")(
                        Div(cls="row justify-content-center")(
                            Div(cls="fbt-main-wrapper col-xl-12")(
                                Div(id="main-wrapper")(
                                    Div(cls="main-section", id="main_content")(

                                        *children,

                                        cls=body_class,

                                    )
                                )
                            ),
                            sidebar()
                        )
                    )
                ),
                newsletter_section(),
                wave(),
                footer()
            )
        ),
        # Add extra JS if provided
        *([Script(src=js) for js in extra_js] if extra_js else []),
        Script(src="/static/js/jquery.min.js"),
        Script(src="/static/js/bootstrap.bundle.min.js"),
        Script(src="/static/js/plugins.js"),
        Script(src="/static/js/main.js"),
    )


def BaseLayout(request, title: str, body_class: str, page_class: str, *children, slider=None, extra_css=None,
               extra_js=None):
    if request.user.is_authenticated:
        pass
    else:
        pass

    return Base(
        request,
        title,
        body_class,
        page_class,
        *children,

    )


def MagazineLayout(
        request, title: str, body_class: str, *children, slider=None, gallery_posts=None, extra_css=None, extra_js=None
):
    gallery_posts = sample_posts[1:6]  # Posts for gallery section
    if request.user.is_authenticated:
        pass

    return Base(
        request,
        title,
        body_class,
        Div(id="page-wrapper", cls="magazine-view feed-view")(
            headline_section(),
            magazine_navbar(),
            Div(cls="outer-wrapper my-5", id="outer-wrapper")(

                gallery_section(gallery_posts),
                *children,

            )
        ),
    )
