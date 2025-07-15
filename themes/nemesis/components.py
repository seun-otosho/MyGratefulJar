from datetime import datetime

from django.urls import reverse
from fastcore.basics import NotStr
from fasthtml.common import *
from fasthtml.components import Link, Div
from fasthtml.xtend import Script

from themes.nemesis.meta import sample_posts


def search_overlay():
    """Search overlay component"""
    return Div(
        id="fbt-content-overlay",
        onclick="closeNav()"
    )


def search_form():
    """Search form component"""
    return Form(
        autocomplete="off",
        id="search",
        role="search"
    )(
        Div(cls="input")(
            Input(cls="search", name="search", placeholder="Search...", type="text"),
            Button(cls="submit fa fa-search", type="submit", value="")
        ),
        Button(id="close", type="reset", value="×")
    )


def navbar(request):
    """Main navigation component"""
    if request.user.is_authenticated:
        nav_items = [
            # A form is the correct way to do a POST for logout
            Form(
                Li(cls="nav-item")(A(href=reverse('account_logout'), cls="nav-link", type="submit", )("Logout"), ),
                action=reverse('account_logout'),
                method="post",
                style="display: inline;"
            )
        ]
    else:
        nav_items = [
            Li(cls="nav-item")(A(href=reverse('account_login'), cls="nav-link")("Login")),
            Li(cls="nav-item")(A(href=reverse('account_signup'), cls="nav-link")("Sign Up")),
        ]
    return Nav(cls="navbar navbar-expand-xl navbar-fbt fbt-nav-skin fbt_sticky_nav")(
        Div(cls="container nav-mobile-px clearfix")(
            Div(cls="navbar-brand order-2 order-xl-1 m-auto")(
                A(href="/")(
                    Img(alt="Nemesis", src="/static/images/logo_nemesis.png")
                )
            ),
            Button(
                cls="navbar-toggler order-1 order-xl-2",
                aria_expanded="false", aria_label="Toggle navigation", data_target="#navbar-menu",
                data_toggle="collapse",
                type="button"
            )("☰"),
            Div(cls="header-buttons order-3 order-lg-4")(
                Span(cls="fa fa-search navbar-search search-trigger"),
                Span(cls="fbt-sidenav ml-1 active", onclick="openNav()")("☰")
            ),
            Div(cls="collapse navbar-collapse order-4 order-xl-3 clearfix", id="navbar-menu")(
                Ul(cls="navbar-nav m-auto clearfix")(
                    Li(cls="nav-item dropdown")(
                        A(href="#", cls="nav-link dropdown-toggle", aria_haspopup="true", aria_expanded="false",
                          data_toggle="dropdown")("Home"),
                        Div(cls="dropdown-menu")(
                            A(href="/", cls="dropdown-item")("Home 1"),
                            A(href="/blog", cls="dropdown-item")("Blog"),
                        )
                    ),
                    Li(cls="nav-item")(
                        A(href=reverse("contact"), cls="nav-link")("Contact")
                    ),
                    Li(cls="nav-item")(
                        A(href="#", cls="nav-link")("Sport")
                    ),
                    Li(cls="nav-item")(
                        A(href="#", cls="nav-link")("Policy")
                    ),
                    Li(cls="nav-item")(
                        A(href="#", cls="nav-link")("Lifestyle")
                    ),
                    *nav_items
                )
            )
        )
    )


def hero_slider(featured_post):
    """Hero slider component with featured post"""
    return Div(cls="slider-container")(
        Div(cls="slider-container-row", id="slider-posts")(
            Div(cls="widget fbt_fp-slider")(
                Div(cls="widget-content")(
                    Div(cls="container")(
                        Div(cls="row align-items-center slider-width")(
                            Div(cls="col-lg-7")(
                                Div(cls="fbt-shape-container")(
                                    Div(cls="fbt-item-thumbnail radius-10")(
                                        A(cls="post-image-link", href=f"/blog/post/{featured_post['id']}")(
                                            Img(alt="", cls="post-thumbnail lazyloaded", src=featured_post['image'])
                                        )
                                    )
                                )
                            ),
                            Div(cls="col-lg-5 mt-4 mt-lg-0")(
                                Div(cls="fbt-shape-title pl-xl-5 pl-lg-4")(
                                    H1(cls="display-4")(
                                        A(href=f"/blog/post/{featured_post['id']}")(featured_post['title'])
                                    ),
                                    Div(cls="post-meta my-4")(
                                        Span(cls="post-author")(featured_post['author']),
                                        Span(cls="post-date published")(featured_post['date'])
                                    ),
                                    A(href=f"/blog/post/{featured_post['id']}")(
                                        Span(cls="fbt_read_more btn btn-primary-slider radius-25 px-5 mt-2")(
                                            "Keep reading ...")
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def blog_post_card(post):
    """Individual blog post card component"""
    video_icon = Span(cls="video-icon")(I(cls="fa fa-play")) if post['is_video'] else ""

    return Div(cls="blog-post fbt-index-post card radius-10")(
        Div(cls="fbt-post-thumbnail")(
            A(href=f"/blog/post/{post['id']}")(
                Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
            ),
            video_icon
        ),
        Div(cls="fbt-post-caption card-body")(
            H3(cls="post-title h4 card-title")(
                A(href=f"/blog/post/{post['id']}")(post['title'])
            ),
            Div(cls="post-meta")(
                Span(cls="post-author")(A(href="#")(post['author'])),
                Span(cls="post-date published")(post['date'])
            ),
            P(cls="post-excerpt card-text")(post['excerpt'])
        )
    )


def newsletter_section():
    """Newsletter subscription section"""
    return Div(cls="fbt-bottom-section clearfix", id="fbt_bottom_section")(
        Div(cls="widget FollowByEmail")(
            Div(cls="widget-content")(
                Div(cls="container")(
                    Div(cls="row justify-content-center")(
                        Div(cls="follow-by-email-inner subscriber-form col-lg-10")(
                            Div(cls="card radius-10 p-5")(
                                Div(cls="row justify-content-center align-items-center py-3")(
                                    Div(cls="col-lg-3")(
                                        H2(cls="title h1 mb-4 mb-lg-0 text-center text-lg-left")(
                                            "Subscribe to our Newsletter")
                                    ),
                                    Div(cls="col-lg-8 pl-lg-4")(
                                        Form(action="#", cls="fbt-email-form", method="post")(
                                            Input(autocomplete="off", cls="follow-by-email-address", name="email",
                                                  placeholder="Enter your Email", type="email"),
                                            Input(cls="follow-by-email-submit", type="submit", value="Subscribe")
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def footer():
    """Footer component"""
    return Div(cls="footer-dark pt-4", id="footer-content")(
        Div(cls="container pb-4")(
            Div(cls="row clearfix")(
                Div(cls="col-lg-4")(
                    Div(cls="footer-1", id="footer-1")(
                        Div(cls="logoImage")(
                            Div(cls="widget-content")(
                                Img(alt="", src="/static/images/logo-light.png")
                            )
                        ),
                        Div(cls="widget Text")(
                            Div(cls="widget-content")(
                                P("Phasellus deserunt. Convallis perspiciatis fusce fermentum accumsan, arcu aliquam, velit venenatis augue proin, enim etiam dolor. Mi ac lectus vitae cum, fusce purus posuere.")
                            )
                        )
                    )
                ),
                Div(cls="col-lg-2 ml-lg-auto")(
                    Div(cls="footer-2 section", id="footer-2")(
                        Div(cls="widget")(
                            H4(cls="title title-heading")("About"),
                            Div(cls="widget-content list-label-widget-content")(
                                Ul(cls="list-unstyled")(
                                    Li(A(cls="label-name", href="/")("Home")),
                                    Li(A(cls="label-name", href="#")("Lifestyle")),
                                    Li(A(cls="label-name", href="#")("People")),
                                    Li(A(cls="label-name", href="#")("Sport"))
                                )
                            )
                        )
                    )
                ),
                Div(cls="col-lg-2")(
                    Div(cls="footer-3 section", id="footer-3")(
                        Div(cls="widget")(
                            H4(cls="title title-heading")("Categories"),
                            Div(cls="widget-content list-label-widget-content")(
                                Ul(cls="list-unstyled")(
                                    Li(A(cls="label-name", href="#")("Business")),
                                    Li(A(cls="label-name", href="#")("Design")),
                                    Li(A(cls="label-name", href="#")("Lifestyle")),
                                    Li(A(cls="label-name", href="#")("Technology"))
                                )
                            )
                        )
                    )
                )
            )
        ),
        Div(id="credits")(
            Div(cls="container")(
                Div(cls="row divider py-4")(
                    Div(cls="col-lg-6")(
                        Div(cls="copyright-section text-center text-lg-left")(
                            f"© {datetime.now().year} Nemesis | All Rights Reserved"
                        )
                    ),
                    Div(cls="col-lg-6")(
                        Div(cls="footer-menu section", id="footer-menu")(
                            Div(cls="widget socialList")(
                                Div(cls="widget-content")(
                                    Ul(cls="nav")(
                                        Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-facebook"))),
                                        Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-twitter"))),
                                        Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-instagram"))),
                                        Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-linkedin"))),
                                        Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-youtube-play")))
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )


def sidebar():
    """Sidebar component"""
    return Div(cls="sidebar-wrapper", id="sidebar-wrapper")(
        Div(cls="sidebar-wrapper__content")(
            Div(cls="navigation-container clearfix")(
                Span(cls="closebtn", onclick="closeNav()")("×")
            ),
            Div(cls="sidebar-top section", id="menu_sidebar")(
                Div(cls="widget LinkList")(
                    Div(cls="widget-content fbt-sidebar--menu")(
                        Ul(cls="list-group")(
                            Li(cls="list-group-item")(A(href="/")("HOME")),
                            Li(cls="list-group-item")(A(href="#")("ABOUT")),
                            Li(cls="list-group-item")(A(href="#")("SERVICES")),
                            Li(cls="list-group-item")(A(href="/contact")("CONTACT")),
                            Li(cls="list-group-item")(A(href="#")("PRIVACY"))
                        )
                    )
                )
            ),
            Div(cls="sidebar section", id="main_sidebar")(
                Div(cls="widget Label")(
                    Div(cls="fbt-sep-title")(
                        H4(cls="title title-heading-left")("Categories"),
                        Div(cls="title-sep-container")(
                            Div(cls="title-sep sep-double")
                        )
                    ),
                    Div(cls="widget-content cloud-label--widget-content")(
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Business")),
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Design")),
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Entertainment")),
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Lifestyle")),
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Technology")),
                        A(href="#")(Span(cls="badge badge-success py-1 px-2 mb-1")("Sport"))
                    )
                )
            )
        )
    )

def headline_section():
    """Top headline section with navigation and social links"""
    return Div(cls="fbt-headline clearfix", id="headline")(
        Div(cls="container")(
            Div(cls="row align-items-center justify-content-between py-1 py-md-0")(
                Div(cls="col-md-7 left-headline-content")(
                    Div(cls="fbt-left-headline", id="left-headline")(
                        Ul(cls="nav justify-content-center justify-content-md-start")(
                            Li(cls="nav-item")(A(cls="nav-link", href="#")("About")),
                            Li(cls="nav-item")(A(cls="nav-link", href="#")("Services")),
                            Li(cls="nav-item")(A(cls="nav-link", href="/contact")("Contact"))
                        )
                    )
                ),
                Div(cls="col-md-5 right-headline-content")(
                    Div(cls="fbt-right-headline", id="right-headline")(
                        Ul(cls="nav justify-content-center justify-content-md-end social-icons")(
                            Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-facebook"))),
                            Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-twitter"))),
                            Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-instagram"))),
                            Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-linkedin"))),
                            Li(cls="nav-item")(A(cls="nav-link", href="#")(I(cls="fa fa-youtube-play")))
                        )
                    )
                )
            )
        )
    )

def magazine_navbar():
    """Magazine-style navigation with mega menus"""
    return Nav(cls="navbar navbar-expand-xl navbar-fbt fbt-nav-skin fbt_sticky_nav m-0")(
        Div(cls="container nav-mobile-px clearfix")(
            Div(cls="navbar-brand order-2 order-xl-1 m-auto")(
                A(href="/blog")(
                    Img(alt="Nemesis", src="/static/images/logo_nemesis.png")
                )
            ),
            Button(
                cls="navbar-toggler order-1 order-xl-2",
                aria_expanded="false", aria_label="Toggle navigation",
                data_target="#navbar-menu", data_toggle="collapse",
                type="button"
            )("☰"),
            Div(cls="header-buttons order-3 order-lg-4")(
                Span(cls="fa fa-search navbar-search search-trigger"),
                Span(cls="fbt-sidenav ml-1 active", onclick="openNav()")("☰")
            ),
            Div(cls="collapse navbar-collapse order-4 order-xl-3 clearfix", id="navbar-menu")(
                Ul(cls="navbar-nav m-auto clearfix")(
                    Li(cls="nav-item dropdown")(
                        A(href="#", cls="nav-link dropdown-toggle", aria_haspopup="true", aria_expanded="false", data_toggle="dropdown")("Home"),
                        Div(cls="dropdown-menu")(
                            A(href="/", cls="dropdown-item")("Home 1"),
                            A(href="/blog", cls="dropdown-item")("Blog"),
                        )
                    ),
                    Li(cls="nav-item")(
                        A(href="/contact", cls="nav-link")("Contact")
                    ),
                    Li(cls="nav-item")(
                        A(href="/blog", cls="nav-link")("Blog")
                    ),
                    Li(cls="nav-item")(
                        A(href="#", cls="nav-link")("Policy")
                    )
                )
            )
        )
    )

def gallery_section(featured_posts):
    """Gallery section with featured posts"""
    return Div(cls="fbt-gallery bg-light py-5 mt-n5 mb-5")(
        Div(cls="container-fluid fbt-elastic-container fbt-gallery-1 px-lg-5")(
            Div(cls="row px-2")(
                *[gallery_post_card(post) for post in featured_posts[:5]]
            )
        )
    )

def gallery_post_card(post):
    """Individual gallery post card"""
    video_icon = Span(cls="video-icon")(I(cls="fa fa-play")) if post.get('is_video') else ""

    return Div(cls="col-lg col-md-6 mb-4 mb-lg-0 px-2")(
        Div(cls="post-item card")(
            Div(cls="fbt-post-thumbnail")(
                A(href=f"/blog/post/{post['id']}")(
                    Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
                ),
                video_icon
            ),
            Div(cls="fbt-post-caption")(
                Div(cls="title-caption text-center p-4")(
                    Div(cls="post-meta mb-2")(
                        Span(cls="post-author")(A(href="#")(post['author'])),
                        Span(cls="post-date published")(post['date'])
                    ),
                    H3(cls="post-title")(
                        A(href=f"/blog/post/{post['id']}")(post['title'])
                    )
                )
            )
        )
    )

def magazine_post_card(post):
    """Magazine-style post card for main listing"""
    video_icon = Span(cls="video-icon")(I(cls="fa fa-play")) if post.get('is_video') else ""

    return Div(cls="fbt_magazine-blog-post fbt-index-post row align-items-center justify-content-between")(
        Div(cls="col-xl-6 col-md-5")(
            Div(cls="fbt-post-thumbnail")(
                A(href=f"/blog/post/{post['id']}")(
                    Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
                ),
                video_icon
            )
        ),
        Div(cls="col-xl-6 col-md-7")(
            Div(cls="fbt-post-caption mt-3 mt-md-0")(
                Span(cls="post-tag index-post-tag")(post.get('category', 'General')),
                H3(cls="post-title")(
                    A(href=f"/blog/post/{post['id']}")(post['title'])
                ),
                Div(cls="post-meta mb-2")(
                    Span(cls="post-author")(A(href="#")(post['author'])),
                    Span(cls="post-date published")(post['date'])
                ),
                P(cls="post-excerpt")(post['excerpt'])
            )
        )
    )

def popular_post_item(post):
    """Individual popular post item"""
    return Article(cls="post mb-3")(
        Div(cls="post-content media align-items-center")(
            Div(cls="fbt-item-thumbnail clearfix")(
                A(href=f"/blog/post/{post['id']}")(
                    Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
                )
            ),
            Div(cls="ml-3 fbt-title-caption media-body")(
                Span(cls="pp-post-tag")(post.get('category', 'General')),
                H3(cls="post-title")(
                    A(href=f"/blog/post/{post['id']}")(post['title'])
                ),
                Div(cls="post-meta")(
                    Span(cls="post-date published")(post['date'])
                )
            )
        )
    )


def blog_sidebar(featured_post, popular_posts):
    """Blog sidebar with featured post and popular posts"""
    return Div(cls="fbt-main-sidebar col-lg-4")(
        Div(cls="fbt-main-sidebar__content h-100 pl-lg-3")(
            # Featured Post Widget
            Div(cls="widget FeaturedPost mb-5")(
                Div(cls="fbt-sep-title")(
                    H4(cls="title title-heading-left")("Featured Post"),
                    Div(cls="title-sep-container")(
                        Div(cls="title-sep sep-double")
                    )
                ),
                Div(cls="widget-content")(
                    Div(cls="FeaturedPostContainer")(
                        Div(cls="fbt-item-thumbnail")(
                            A(cls="post-image-link", href=f"/blog/post/{featured_post['id']}")(
                                Img(alt="", cls="post-thumbnail lazyloaded", src=featured_post['image'])
                            )
                        ),
                        Div(cls="fbt-title-section mt-3")(
                            Div(cls="post-meta mb-2")(
                                Span(cls="post-author")(featured_post['author']),
                                Span(cls="post-date published")(featured_post['date'])
                            ),
                            H3(cls="post-title")(
                                A(href=f"/blog/post/{featured_post['id']}")(featured_post['title'])
                            ),
                            P(cls="post-excerpt")(featured_post['excerpt'])
                        )
                    )
                )
            ),
            # Popular Posts Widget
            Div(cls="widget fbt_list_posts mb-5")(
                Div(cls="fbt-sep-title")(
                    H4(cls="title title-heading-left")("Popular Posts"),
                    Div(cls="title-sep-container")(
                        Div(cls="title-sep sep-double")
                    )
                ),
                Div(cls="widget-content")(
                    *[popular_post_item(post) for post in popular_posts]
                )
            )
        )
    )


def pagination_nav(current_page=2, total_pages=3):
    """Pagination navigation"""
    return Div(cls="pagenav", id="blog-pager")(
        Span(cls="showpageOf")(f"{current_page} / {total_pages}"),
        Span(cls="showpage firstpage")(
            A(href="#")(I(cls="fa fa-angle-double-left"))
        ),
        Span(cls="showpage")(
            A(href="#")(I(cls="fa fa-angle-left"))
        ),
        Span(cls="displaypageNum")(A(href="#")("1")),
        Span(cls="page current")("2"),
        Span(cls="displaypageNum")(A(href="#")("3")),
        Span(cls="displaypageNum")(
            A(href="#")(I(cls="fa fa-angle-right"))
        ),
        Span(cls="displaypageNum lastpage")(
            A(href="#")(I(cls="fa fa-angle-double-right"))
        )
    )


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


def wave():
    return Div(cls="fbt-bottom-shape")(
        # SVG wave shape
        NotStr('''<svg class="fbt-footer-wave-big" preserveAspectRatio="none" version="1.1" viewBox="5 0 1366 222" width="100%">
                    <path d="M-2.19,238H1366v-4.27c-67.87-24-146.44-43.08-230.75-53.19-253.33-27.78-293.94,51.64-541.13,29.89C318.08,186.31,289.49,32.92,6.9,11.73c-5.21-.42-10.56-.7-15.9-1V238Z" transform="translate(9.5 -10.22)"></path>
                </svg>''')
    )





# Extended sample data for full post content
def get_full_post_content(post_id):
    """Get full content for a specific post"""
    content_map = {
        1: {
            "content": """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut porttitor leo vel nulla posuere accumsan. Suspendisse sed tortor eget justo aliquam euismod. Morbi ut massa et neque iaculis lacinia a eu est. Etiam nec enim id mi maximus consequat sed ut tortor. Nullam velit ipsum, ornare id leo a, cursus mollis nunc. Etiam dignissim nulla vel ante mollis, lobortis aliquam lectus egestas.

Vivamus sit amet libero sit amet lorem dignissim varius. Nam id dictum sem. Maecenas eget nulla bibendum, accumsan arcu ac, vehicula risus. Nulla laoreet elit in lectus cursus, at tristique diam fringilla. Donec blandit, lacus sed mollis molestie, lorem lacus feugiat tortor, nec tincidunt libero dolor sit amet nulla.""",
            "highlighted_text": "Donec bibendum urna quis orci molestie sodales. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nunc id purus vel sapien pretium varius eu id risus.",
            "quote": "Donec dolor elit, pellentesque a massa pellentesque, euismod sagittis ipsum. Nullam a diam ac turpis iaculis vulputate. Nunc tellus libero, tempus id luctus eget, fermentum et quam. Aliquam erat volutpat.",
            "categories": ["Design", "Lifestyle", "Technology"],
            "tags": ["blog", "design", "web"]
        }
    }
    return content_map.get(post_id, {
        "content": "This is a sample blog post content. Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "highlighted_text": "This is highlighted content for emphasis.",
        "quote": "This is a sample quote from the blog post.",
        "categories": ["General"],
        "tags": ["sample"]
    })

def single_post_hero(post):
    """Single post hero section with image, title, meta, and social sharing"""
    return Div(cls="slider-container")(
        Div(cls="row align-items-center slider-width")(
            Div(cls="col-lg-7")(
                Div(cls="fbt-shape-container")(
                    Div(cls="fbt-item-thumbnail radius-10")(
                        Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
                    )
                )
            ),
            Div(cls="col-lg-5 mt-4 mt-lg-0")(
                Div(cls="fbt-shape-title pl-xl-5 pl-lg-4")(
                    H1(cls="post-title display-4")(post['title']),
                    Div(cls="item-post-meta mt-4")(
                        Div(cls="post-meta")(
                            Span(cls="post-author")(
                                A(href="#", target="_blank", title=post['author'])(post['author'])
                            ),
                            Span(cls="post-date published")(post['date'])
                        )
                    ),
                    Div(cls="mt-4")(
                        social_share_buttons()
                    )
                )
            )
        )
    )

def post_content_body(content_data):
    """Post content body with formatted text, highlights, and quotes"""
    return Div(cls="post-body post-content")(
        P(content_data.get('content', 'Sample post content...')),
        Br(),
        Mark(content_data.get('highlighted_text', 'Highlighted content here.')),
        P("Proin condimentum faucibus placerat. Donec massa justo, porttitor tincidunt eros a, vehicula malesuada tortor. Praesent nec sem ut justo efficitur tempus."),
        Br(),
        Blockquote(cls="tr_bq fbt-shape-container")(
            Div(cls="card shadow-lg radius-10 px-5 pt-5 pb-4")(
                P(cls="pl-5")(content_data.get('quote', 'Sample quote content.'))
            )
        ),
        P("Nunc accumsan ex ligula, in malesuada sapien consectetur in. Praesent non lectus sed dolor imperdiet mollis a sit amet sem. Vivamus eu commodo ligula. Phasellus in lacus eu urna ullamcorper lacinia.")
    )

def post_footer_section(post, content_data):
    """Post footer with categories and social sharing"""
    return Div(cls="post-footer")(
        Div(cls="row justify-content-center")(
            Div(cls="col-xl-8 col-lg-9")(
                Div(cls="row align-items-center my-4")(
                    Div(cls="col-lg-8 text-center text-lg-left mb-3 mb-lg-0")(
                        Div(cls="post-labels")(
                            Span(cls="mr-2")("Categories:"),
                            Span(cls="label-head Label")(
                                *[A(cls="label-link badge badge-secondary py-1 px-3 mr-1", href="#")(cat)
                                  for cat in content_data.get('categories', [post.get('category', 'General')])]
                            )
                        )
                    ),
                    Div(cls="col-lg-4 text-center text-lg-right")(
                        social_share_buttons()
                    )
                )
            )
        )
    )

def post_navigation(current_post_id):
    """Previous/Next post navigation"""
    # Find previous and next posts
    current_index = next((i for i, post in enumerate(sample_posts) if post['id'] == current_post_id), 0)
    prev_post = sample_posts[current_index - 1] if current_index > 0 else None
    next_post = sample_posts[current_index + 1] if current_index < len(sample_posts) - 1 else None

    return Div(cls="fbt-item-post-pager")(
        Div(cls="card shadow-lg radius-10 mt-3 mb-5")(
            Div(cls="post-pager row")(
                Div(cls="previous col-lg-6 bg-primary px-5 py-5 text-left")(
                    A(cls="fbt-newer-link text-white", href=f"/blog/post/{prev_post['id']}" if prev_post else "#")(
                        Strong(cls="lead text-left pl-3")(I(cls="fa fa-angle-left"), " Previous"),
                        Div(cls="h2 text-white fbt-np-title mt-2 pl-3")(
                            prev_post['title'][:50] + "..." if prev_post and len(prev_post['title']) > 50
                            else prev_post['title'] if prev_post else "No previous post"
                        )
                    ) if prev_post else Div(cls="text-white pl-3")("No previous post")
                ),
                Div(cls="next col-lg-6 bg-warning px-5 py-5 text-right")(
                    A(cls="fbt-older-link text-white", href=f"/blog/post/{next_post['id']}" if next_post else "#")(
                        Strong(cls="lead text-right pr-3")("Next ", I(cls="fa fa-angle-right")),
                        Div(cls="h2 text-white text-right fbt-np-title mt-2 pr-3")(
                            next_post['title'][:50] + "..." if next_post and len(next_post['title']) > 50
                            else next_post['title'] if next_post else "No next post"
                        )
                    ) if next_post else Div(cls="text-white pr-3")("No next post")
                )
            )
        )
    )

def related_posts_section(current_post_id):
    """Related posts section"""
    # Get 3 random posts excluding current one
    related = [post for post in sample_posts if post['id'] != current_post_id][:3]

    return Div(cls="fbt-rel-post-wrapper mb-5")(
        Div(cls="row justify-content-center align-items-center")(
            Div(cls="col-xl-3 mb-4 mb-xl-0")(
                Div(cls="title-wrap fbt-shape-title")(
                    H3(cls="display-4")("You may like these posts")
                )
            ),
            Div(cls="col-xl-9 pl-xl-5")(
                Div(id="related-posts")(
                    Div(cls="row")(
                        *[related_post_card(post) for post in related]
                    )
                )
            )
        )
    )


def related_post_card(post):
    """Individual related post card"""
    video_icon = Span(cls="video-icon")(I(cls="fa fa-play")) if post.get('is_video') else ""

    return Div(cls="col-lg-4 col-md-12 mb-5 mb-lg-0 rp-item")(
        Div(cls="card radius-10")(
            Div(cls="fbt-post-thumbnail")(
                A(href=f"/blog/post/{post['id']}")(
                    Div(cls="fbt-resize lazyloaded", style=f"background-image: url({post['image']})")
                ),
                video_icon
            ),
            Div(cls="fbt-post-caption card-body")(
                H5(
                    A(href=f"/blog/post/{post['id']}")(
                        post['title'][:40] + "..." if len(post['title']) > 40 else post['title']
                    )
                )
            )
        )
    )

def social_share_buttons():
    """Social sharing buttons component"""
    return Div(cls="sharepost clearfix")(
        Div(cls="post-share clearfix")(
            Ul(
                Li(A(cls="facebook fbt-share", href="#", rel="nofollow", target="_blank")(I(cls="fa fa-facebook"))),
                Li(A(cls="twitter fbt-share", href="#", rel="nofollow", target="_blank")(I(cls="fa fa-twitter"))),
                Li(A(cls="linkedin fbt-linkedin", href="#", rel="nofollow", target="_blank")(I(cls="fa fa-linkedin"))),
                Li(A(cls="pinterest fbt-pinterest", href="#", target="_blank")(I(cls="fa fa-pinterest-p"))),
                Li(A(cls="email fbt-email", href="#", rel="nofollow")(I(cls="fa fa-envelope-o")))
            )
        )
    )

def comments_section(post_id):
    """Comments section with existing comments and comment form"""
    # Sample comments data
    comments = [
        {"id": 1, "author": "John Doe", "avatar": "/static/images/user-1.jpg", "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut porttitor leo vel nulla posuere accumsan. Suspendisse sed tortor eget justo aliquam euismod.", "replies": [
            {"id": 2, "author": "Jane Smith", "avatar": "/static/images/user-2.jpg", "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut porttitor leo vel nulla posuere accumsan."}
        ]},
        {"id": 3, "author": "Bob Wilson", "avatar": "/static/images/user-4.jpg", "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut porttitor leo vel nulla posuere accumsan. Suspendisse sed tortor eget justo aliquam euismod.", "replies": []},
        {"id": 4, "author": "Alice Brown", "avatar": "/static/images/user-3.jpg", "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut porttitor leo vel nulla posuere accumsan. Suspendisse sed tortor eget justo aliquam euismod.", "replies": [
            {"id": 5, "author": "Charlie Davis", "avatar": "/static/images/user-4.jpg", "content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut porttitor leo vel nulla posuere accumsan."}
        ]}
    ]

    return Div(cls="blog-post-comments")(
        Section(cls="comments embed", id="comments")(
            Div(cls="fbt-comment-button--section list-inline text-center")(
                Div(cls="fbt-comment-button list-inline-item")(
                    H3(cls="h4 title fbt-comment-title")(f"{len(comments)} Comments"),
                    Span(cls="fa comment_toogle_button")
                )
            ),
            Div(cls="comment-list--form")(
                Div(cls="comment-list")(
                    *[comment_item(comment) for comment in comments],
                    Div(cls="nav pt-4 mt-n5 mb-5 justify-content-end fbt_bottom_toogle")(
                        Span("Hide Comments")
                    ),
                    comment_form(post_id)
                )
            )
        )
    )

def comment_item(comment):
    """Individual comment item"""
    return Div(cls="media comment mb-4 border")(
        A(cls="mr-4", href="#")(
            Img(src=comment['avatar'], alt="")
        ),
        Div(cls="media-body")(
            H5(cls="mb-2")(comment['author']),
            P(comment['content']),
            Div(cls="comments__actions")(
                Span(cls="button")(
                    A(href="#")(I(cls="fa fa-comments"), "Reply")
                )
            ),
            *[comment_reply(reply) for reply in comment.get('replies', [])]
        )
    )

def comment_reply(reply):
    """Comment reply item"""
    return Div(cls="comment-reply media mt-4")(
        A(cls="mr-4", href="#")(
            Img(src=reply['avatar'], alt="")
        ),
        Div(cls="media-body")(
            H5(cls="mb-2")(reply['author']),
            P(reply['content']),
            Div(cls="comments__actions")(
                Span(cls="button")(
                    A(href="#")(I(cls="fa fa-comments"), "Reply")
                )
            )
        )
    )

def comment_form(post_id):
    """Comment submission form"""
    return Div(
        Div(cls="fbt-sep-title")(
            H4(cls="title title-heading-left")("Leave Your Comment"),
            Div(cls="title-sep-container")(
                Div(cls="title-sep sep-double")
            )
        ),
        Form(cls="comment-form", method="POST", action=f"/blog/post/{post_id}/comment")(
            Div(cls="row")(
                Div(cls="col-md-4")(
                    Div(cls="form-group")(
                        Label(**{"for": "comment-name"})("Name*"),
                        Input(cls="form-control shadow-none radius-0", id="comment-name", name="name", type="text", required=True)
                    )
                ),
                Div(cls="col-md-4")(
                    Div(cls="form-group")(
                        Label(**{"for": "comment-email"})("E-mail*"),
                        Input(cls="form-control shadow-none radius-0", id="comment-email", name="email", type="email", required=True)
                    )
                ),
                Div(cls="col-md-4")(
                    Div(cls="form-group")(
                        Label(**{"for": "comment-website"})("Website"),
                        Input(cls="form-control shadow-none radius-0", id="comment-website", name="website", type="url")
                    )
                )
            ),
            Div(cls="row")(
                Div(cls="col-md-12")(
                    Div(cls="form-group")(
                        Label(**{"for": "comment-message"})("Comment*"),
                        Textarea(cls="form-control shadow-none radius-0", rows="5", id="comment-message", name="comment", required=True)
                    )
                )
            ),
            Button(cls="btn btn-success radius-0", type="submit")(
                I(cls="fa fa-paper-plane-o mr-2"),
                "Submit Comment"
            )
        )
    )

