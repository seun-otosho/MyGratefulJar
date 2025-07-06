"""
FastHTML Nemesis Blog with Supabase Database Integration
Connects the existing FastHTML templates to live Supabase database
"""

from fasthtml.common import *
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database integration
from database_integration import (
    get_homepage_data,
    get_blog_listing_data, 
    get_post_data,
    search_posts,
    submit_contact_form,
    submit_comment,
    subscribe_newsletter
)

# Custom CSS and JS headers to match the original template
custom_hdrs = [
    Link(rel="shortcut icon", href="favicon.ico", type="image/x-icon"),
    Link(href="https://fonts.googleapis.com/css?family=Montserrat:900%7CNunito:400,700%7COswald%7CRoboto", rel="stylesheet"),
    Link(href="./css/animate.min.css", rel="stylesheet", media="screen"),
    Link(href="./css/fonts.css", rel="stylesheet", media="screen"),
    Link(href="./css/bootstrap.min.css", rel="stylesheet", media="screen"),
    Link(href="./css/style.css", rel="stylesheet", media="screen"),
    Script(src="./js/jquery.min.js"),
    Script(src="./js/bootstrap.bundle.min.js"),
    Script(src="./js/plugins.js"),
    Script(src="./js/main.js"),
]

app, rt = fast_app(hdrs=custom_hdrs)

# =====================================================
# TEMPLATE COMPONENTS (REUSED FROM ORIGINAL)
# =====================================================

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
        role="search",
        method="GET",
        action="/search"
    )(
        Div(cls="input")(
            Input(cls="search", name="q", placeholder="Search...", type="text"),
            Button(cls="submit fa fa-search", type="submit", value="")
        ),
        Button(id="close", type="reset", value="×")
    )

def navbar():
    """Main navigation component"""
    return Nav(cls="navbar navbar-expand-xl navbar-fbt fbt-nav-skin fbt_sticky_nav")(
        Div(cls="container nav-mobile-px clearfix")(
            Div(cls="navbar-brand order-2 order-xl-1 m-auto")(
                A(href="/")(
                    Img(alt="Nemesis", src="./images/logo_nemesis.png")
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
                        A(href="#", cls="nav-link")("Sport")
                    ),
                    Li(cls="nav-item")(
                        A(href="#", cls="nav-link")("Policy")
                    ),
                    Li(cls="nav-item")(
                        A(href="#", cls="nav-link")("Lifestyle")
                    )
                )
            )
        )
    )

def hero_slider(featured_post):
    """Hero slider component with featured post"""
    if not featured_post:
        return Div()  # Return empty div if no featured post
    
    return Div(cls="slider-container")(
        Div(cls="slider-container-row", id="slider-posts")(
            Div(cls="widget fbt_fp-slider")(
                Div(cls="widget-content")(
                    Div(cls="container")(
                        Div(cls="row align-items-center slider-width")(
                            Div(cls="col-lg-7")(
                                Div(cls="fbt-shape-container")(
                                    Div(cls="fbt-item-thumbnail radius-10")(
                                        A(cls="post-image-link", href=f"/post/{featured_post['id']}")(
                                            Img(alt="", cls="post-thumbnail lazyloaded", src=featured_post['image'])
                                        )
                                    )
                                )
                            ),
                            Div(cls="col-lg-5 mt-4 mt-lg-0")(
                                Div(cls="fbt-shape-title pl-xl-5 pl-lg-4")(
                                    H1(cls="display-4")(
                                        A(href=f"/post/{featured_post['id']}")(featured_post['title'])
                                    ),
                                    Div(cls="post-meta my-4")(
                                        Span(cls="post-author")(featured_post['author']),
                                        Span(cls="post-date published")(featured_post['date'])
                                    ),
                                    A(href=f"/post/{featured_post['id']}")(
                                        Span(cls="fbt_read_more btn btn-primary-slider radius-25 px-5 mt-2")("Keep reading ...")
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
    video_icon = Span(cls="video-icon")(I(cls="fa fa-play")) if post.get('is_video') else ""
    
    return Div(cls="blog-post fbt-index-post card radius-10")(
        Div(cls="fbt-post-thumbnail")(
            A(href=f"/post/{post['id']}")(
                Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
            ),
            video_icon
        ),
        Div(cls="fbt-post-caption card-body")(
            H3(cls="post-title h4 card-title")(
                A(href=f"/post/{post['id']}")(post['title'])
            ),
            Div(cls="post-meta")(
                Span(cls="post-author")(A(href="#")(post['author'])),
                Span(cls="post-date published")(post['date'])
            ),
            P(cls="post-excerpt card-text")(post['excerpt'])
        )
    )

def sidebar(categories=None):
    """Sidebar component with dynamic categories"""
    if not categories:
        categories = []
    
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
                            Li(cls="list-group-item")(A(href="/blog")("BLOG")),
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
                        *[A(href=f"/category/{cat['slug']}")(
                            Span(cls="badge badge-success py-1 px-2 mb-1", style=f"background-color: {cat.get('color', '#28a745')}")(cat['name'])
                        ) for cat in categories]
                    )
                )
            )
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
                                        H2(cls="title h1 mb-4 mb-lg-0 text-center text-lg-left")("Subscribe to our Newsletter")
                                    ),
                                    Div(cls="col-lg-8 pl-lg-4")(
                                        Form(action="/newsletter", cls="fbt-email-form", method="post")(
                                            Input(autocomplete="off", cls="follow-by-email-address", name="email", placeholder="Enter your Email", type="email", required=True),
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
                                Img(alt="", src="./images/logo-light.png")
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
                                    Li(A(cls="label-name", href="/blog")("Blog")),
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

# =====================================================
# ROUTES WITH DATABASE INTEGRATION
# =====================================================

@rt("/")
async def homepage():
    """Homepage route with database integration"""
    try:
        # Get data from database
        data = await get_homepage_data()
        featured_post = data.get("featured_post")
        regular_posts = data.get("regular_posts", [])
        categories = data.get("categories", [])
        
        return (
            Title("Nemesis | Minimal Blog HTML Template"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            search_overlay(),
            search_form(),
            Div(id="page-wrapper", cls="feed-view")(
                navbar(),
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
                                                A(cls="blog-pager-older-link list-inline-item", href="/blog", title="More posts")(
                                                    Div(cls="fbt-bp-message text-uppercase font-weight-bold")("More posts"),
                                                    Span(aria_hidden="true", cls="fa fa-angle-down")
                                                )
                                            )
                                        )
                                    )
                                )
                            ),
                            sidebar(categories)
                        )
                    )
                ),
                newsletter_section(),
                Div(cls="fbt-bottom-shape")(
                    NotStr('''<svg class="fbt-footer-wave-big" preserveAspectRatio="none" version="1.1" viewBox="5 0 1366 222" width="100%">
                        <path d="M-2.19,238H1366v-4.27c-67.87-24-146.44-43.08-230.75-53.19-253.33-27.78-293.94,51.64-541.13,29.89C318.08,186.31,289.49,32.92,6.9,11.73c-5.21-.42-10.56-.7-15.9-1V238Z" transform="translate(9.5 -10.22)"></path>
                    </svg>''')
                ),
                footer()
            )
        )
    except Exception as e:
        print(f"Error in homepage route: {e}")
        # Return fallback page
        return (
            Title("Nemesis Blog - Loading..."),
            Div(cls="container mt-5")(
                H1("Welcome to Nemesis Blog"),
                P("Loading content... Please check your database connection."),
                A(href="/blog", cls="btn btn-primary")("View Blog")
            )
        )

# =====================================================
# BLOG LISTING ROUTE
# =====================================================

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
                    Img(alt="Nemesis", src="./images/logo_nemesis.png")
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
    if not featured_posts:
        return Div()
    
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
                A(href=f"/post/{post['id']}")(
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
                        A(href=f"/post/{post['id']}")(post['title'])
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
                A(href=f"/post/{post['id']}")(
                    Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
                ),
                video_icon
            )
        ),
        Div(cls="col-xl-6 col-md-7")(
            Div(cls="fbt-post-caption mt-3 mt-md-0")(
                Span(cls="post-tag index-post-tag")(post.get('category', 'General')),
                H3(cls="post-title")(
                    A(href=f"/post/{post['id']}")(post['title'])
                ),
                Div(cls="post-meta mb-2")(
                    Span(cls="post-author")(A(href="#")(post['author'])),
                    Span(cls="post-date published")(post['date'])
                ),
                P(cls="post-excerpt")(post['excerpt'])
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
                            A(cls="post-image-link", href=f"/post/{featured_post['id']}" if featured_post else "#")(
                                Img(alt="", cls="post-thumbnail lazyloaded", 
                                    src=featured_post['image'] if featured_post else "./images/default-post.jpg")
                            )
                        ) if featured_post else Div(),
                        Div(cls="fbt-title-section mt-3")(
                            Div(cls="post-meta mb-2")(
                                Span(cls="post-author")(featured_post['author'] if featured_post else "Author"),
                                Span(cls="post-date published")(featured_post['date'] if featured_post else "Date")
                            ),
                            H3(cls="post-title")(
                                A(href=f"/post/{featured_post['id']}" if featured_post else "#")(
                                    featured_post['title'] if featured_post else "Featured Post Title"
                                )
                            ),
                            P(cls="post-excerpt")(featured_post['excerpt'] if featured_post else "Post excerpt...")
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
                    *[popular_post_item(post) for post in popular_posts[:4]]
                )
            )
        )
    )

def popular_post_item(post):
    """Individual popular post item"""
    return Article(cls="post mb-3")(
        Div(cls="post-content media align-items-center")(
            Div(cls="fbt-item-thumbnail clearfix")(
                A(href=f"/post/{post['id']}")(
                    Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
                )
            ),
            Div(cls="ml-3 fbt-title-caption media-body")(
                Span(cls="pp-post-tag")(post.get('category', 'General')),
                H3(cls="post-title")(
                    A(href=f"/post/{post['id']}")(post['title'])
                ),
                Div(cls="post-meta")(
                    Span(cls="post-date published")(post['date'])
                )
            )
        )
    )

def pagination_nav(current_page=1, has_more=False):
    """Pagination navigation"""
    return Div(cls="pagenav", id="blog-pager")(
        Span(cls="showpageOf")(f"Page {current_page}"),
        Span(cls="showpage firstpage")(
            A(href=f"/blog?page=1" if current_page > 1 else "#")(I(cls="fa fa-angle-double-left"))
        ) if current_page > 1 else Span(),
        Span(cls="showpage")(
            A(href=f"/blog?page={current_page-1}" if current_page > 1 else "#")(I(cls="fa fa-angle-left"))
        ) if current_page > 1 else Span(),
        Span(cls="page current")(str(current_page)),
        Span(cls="displaypageNum")(
            A(href=f"/blog?page={current_page+1}" if has_more else "#")(I(cls="fa fa-angle-right"))
        ) if has_more else Span()
    )

@rt("/blog")
async def blog_listing(page: int = 1):
    """Blog listing page with magazine layout"""
    try:
        # Get data from database
        data = await get_blog_listing_data(page)
        posts = data.get("posts", [])
        gallery_posts = data.get("gallery_posts", [])
        sidebar_featured = data.get("sidebar_featured")
        popular_posts = data.get("popular_posts", [])
        current_page = data.get("current_page", 1)
        has_more = data.get("has_more", False)
        
        return (
            Title("Nemesis | Magazine Blog HTML Template"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            search_overlay(),
            search_form(),
            Div(id="page-wrapper", cls="magazine-view feed-view")(
                headline_section(),
                magazine_navbar(),
                Div(cls="outer-wrapper my-5", id="outer-wrapper")(
                    gallery_section(gallery_posts),
                    # Ad Block
                    Div(cls="container fbt-elastic-container mb-5")(
                        Div(cls="widget fbt-ad-block")(
                            Div(cls="fbt_ad text-center")(
                                Div(cls="widget-content")(
                                    A(href="#")(
                                        Img(alt="", cls="img-fluid lazyloaded", src="./images/horizontal_ad.jpg")
                                    )
                                )
                            )
                        )
                    ),
                    # Main Content Area
                    Div(cls="container fbt-elastic-container")(
                        Div(cls="row justify-content-center")(
                            # Main Content
                            Div(cls="fbt-main-wrapper col-lg-8 mb-5 mb-lg-0")(
                                Div(id="main-wrapper")(
                                    Div(cls="main-section", id="main_content")(
                                        Div(cls="fbt-sep-title")(
                                            H4(cls="title title-heading-left")("Recent posts"),
                                            Div(cls="title-sep-container")(
                                                Div(cls="title-sep sep-double")
                                            )
                                        ),
                                        Div(cls="blog-posts fbt-index-post-wrap")(
                                            *[magazine_post_card(post) for post in posts]
                                        ),
                                        pagination_nav(current_page, has_more)
                                    )
                                )
                            ),
                            # Sidebar
                            blog_sidebar(sidebar_featured, popular_posts)
                        )
                    )
                ),
                newsletter_section(),
                Div(cls="fbt-bottom-shape")(
                    NotStr('''<svg class="fbt-footer-wave-big" preserveAspectRatio="none" version="1.1" viewBox="5 0 1366 222" width="100%">
                        <path d="M-2.19,238H1366v-4.27c-67.87-24-146.44-43.08-230.75-53.19-253.33-27.78-293.94,51.64-541.13,29.89C318.08,186.31,289.49,32.92,6.9,11.73c-5.21-.42-10.56-.7-15.9-1V238Z" transform="translate(9.5 -10.22)"></path>
                    </svg>''')
                ),
                footer()
            )
        )
    except Exception as e:
        print(f"Error in blog listing route: {e}")
        return (
            Title("Blog - Nemesis"),
            Div(cls="container mt-5")(
                H1("Blog Posts"),
                P("Loading blog posts... Please check your database connection."),
                A(href="/", cls="btn btn-primary")("← Back to Home")
            )
        )

@rt("/newsletter", methods=["POST"])
async def newsletter_signup(email: str):
    """Handle newsletter subscription"""
    try:
        success = await subscribe_newsletter(email)
        if success:
            return (
                Title("Newsletter Subscription - Nemesis Blog"),
                Div(cls="container mt-5")(
                    Div(cls="alert alert-success")(
                        H4("Successfully Subscribed!"),
                        P(f"Thank you! {email} has been added to our newsletter."),
                        A(href="/", cls="btn btn-primary")("← Back to Home")
                    )
                )
            )
        else:
            raise Exception("Subscription failed")
    except Exception as e:
        print(f"Newsletter subscription error: {e}")
        return (
            Title("Newsletter Subscription Error - Nemesis Blog"),
            Div(cls="container mt-5")(
                Div(cls="alert alert-danger")(
                    H4("Subscription Failed"),
                    P("There was an error subscribing to our newsletter. Please try again."),
                    A(href="/", cls="btn btn-primary")("← Back to Home")
                )
            )
        )

# =====================================================
# CONTACT PAGE ROUTE
# =====================================================

def contact_hero_section():
    """Contact page hero section with background image"""
    return Div(cls="slider-container")(
        Div(cls="row align-items-center")(
            Div(cls="col-lg-12")(
                Div(cls="fbt-shape-container card shadow-none")(
                    Div(cls="fbt-item-thumbnail radius-10")(
                        Img(alt="Contact Us", cls="post-thumbnail", src="./images/page-img-1.jpg")
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

@rt("/contact")
async def contact_page():
    """Contact page with form and information"""
    try:
        # Get categories for sidebar
        data = await get_homepage_data()
        categories = data.get("categories", [])
        
        return (
            Title("Contact Us - Nemesis Blog"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            search_overlay(),
            search_form(),
            Div(id="page-wrapper", cls="page-view")(
                navbar(),
                Div(cls="outer-wrapper clearfix", id="outer-wrapper")(
                    Div(cls="container fbt-elastic-container")(
                        Div(cls="row justify-content-center")(
                            Div(cls="fbt-main-wrapper col-xl-12")(
                                Div(id="main-wrapper")(
                                    Div(cls="main-section", id="main_content")(
                                        Div(cls="blog-posts fbt-item-post-wrap")(
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
                                    )
                                )
                            ),
                            sidebar(categories)
                        )
                    )
                ),
                Div(cls="fbt-bottom-shape")(
                    NotStr('''<svg class="fbt-footer-wave-big" preserveAspectRatio="none" version="1.1" viewBox="5 0 1366 222" width="100%">
                        <path d="M-2.19,238H1366v-4.27c-67.87-24-146.44-43.08-230.75-53.19-253.33-27.78-293.94,51.64-541.13,29.89C318.08,186.31,289.49,32.92,6.9,11.73c-5.21-.42-10.56-.7-15.9-1V238Z" transform="translate(9.5 -10.22)"></path>
                    </svg>''')
                ),
                footer()
            )
        )
    except Exception as e:
        print(f"Error in contact page route: {e}")
        return (
            Title("Contact - Nemesis Blog"),
            Div(cls="container mt-5")(
                H1("Contact Us"),
                P("Loading contact page... Please check your database connection."),
                A(href="/", cls="btn btn-primary")("← Back to Home")
            )
        )

@rt("/contact", methods=["POST"])
async def contact_form_submit(name: str, email: str, website: str = "", message: str = ""):
    """Handle contact form submission"""
    try:
        success = await submit_contact_form(name, email, website, message)
        if success:
            return (
                Title("Message Sent - Nemesis Blog"),
                Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
                Div(cls="container mt-5")(
                    Div(cls="alert alert-success", role="alert")(
                        H4(cls="alert-heading")("Message Sent Successfully!"),
                        P(f"Thank you {name}, your message has been received. We'll get back to you at {email} soon."),
                        Hr(),
                        P(cls="mb-0")("Your message: ", Em(message[:100] + "..." if len(message) > 100 else message))
                    ),
                    A(href="/contact", cls="btn btn-primary mt-3")("← Back to Contact"),
                    A(href="/", cls="btn btn-secondary mt-3 ml-2")("← Back to Home")
                )
            )
        else:
            raise Exception("Contact form submission failed")
    except Exception as e:
        print(f"Contact form submission error: {e}")
        return (
            Title("Contact Form Error - Nemesis Blog"),
            Div(cls="container mt-5")(
                Div(cls="alert alert-danger")(
                    H4("Message Failed to Send"),
                    P("There was an error sending your message. Please try again."),
                    A(href="/contact", cls="btn btn-primary")("← Back to Contact")
                )
            )
        )

# =====================================================
# SINGLE POST ROUTE
# =====================================================

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

def related_posts_section(related_posts):
    """Related posts section"""
    if not related_posts:
        return Div()
    
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
                        *[related_post_card(post) for post in related_posts[:3]]
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
                A(href=f"/post/{post['id']}")(
                    Div(cls="fbt-resize lazyloaded", style=f"background-image: url({post['image']})")
                ),
                video_icon
            ),
            Div(cls="fbt-post-caption card-body")(
                H5(
                    A(href=f"/post/{post['id']}")(
                        post['title'][:40] + "..." if len(post['title']) > 40 else post['title']
                    )
                )
            )
        )
    )

def comments_section(post_id, comments):
    """Comments section with existing comments and comment form"""
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
        Form(cls="comment-form", method="POST", action=f"/post/{post_id}/comment")(
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

@rt("/post/{post_id}")
async def post_detail(post_id: str):
    """Individual post page with full template"""
    try:
        # Get post data from database
        data = await get_post_data(post_id)
        if not data:
            return (
                Title("Post Not Found - Nemesis Blog"),
                Div(cls="container mt-5")(
                    H1("Post Not Found"),
                    P("The requested post could not be found."),
                    A(href="/blog", cls="btn btn-primary")("← Back to Blog")
                )
            )
        
        post = data["post"]
        comments = data["comments"]
        related_posts = data["related_posts"]
        content_data = data["content_data"]
        
        # Get categories for sidebar
        homepage_data = await get_homepage_data()
        categories = homepage_data.get("categories", [])
        
        return (
            Title(f"{post['title']} - Nemesis Blog"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            search_overlay(),
            search_form(),
            Div(id="page-wrapper", cls="item-view")(
                navbar(),
                Div(cls="outer-wrapper clearfix", id="outer-wrapper")(
                    Div(cls="container fbt-elastic-container")(
                        Div(cls="row justify-content-center")(
                            Div(cls="fbt-main-wrapper col-xl-12")(
                                Div(id="main-wrapper")(
                                    Div(cls="main-section", id="main_content")(
                                        Div(cls="blog-posts fbt-item-post-wrap")(
                                            Div(cls="blog-post fbt-item-post")(
                                                # Hero section
                                                single_post_hero(post),
                                                # Post content
                                                Div(cls="row justify-content-center")(
                                                    Div(cls="col-xl-8 col-lg-9")(
                                                        Div(cls="mt-n5")(
                                                            post_content_body(content_data)
                                                        )
                                                    )
                                                ),
                                                # Post footer with categories and sharing
                                                post_footer_section(post, content_data),
                                                # Related posts
                                                related_posts_section(related_posts)
                                            )
                                        ),
                                        # Comments section
                                        Div(cls="row justify-content-center")(
                                            Div(cls="col-xl-8 col-lg-9")(
                                                comments_section(post_id, comments)
                                            )
                                        )
                                    )
                                )
                            ),
                            sidebar(categories)
                        )
                    )
                ),
                Div(cls="fbt-bottom-shape")(
                    NotStr('''<svg class="fbt-footer-wave-big" preserveAspectRatio="none" version="1.1" viewBox="5 0 1366 222" width="100%">
                        <path d="M-2.19,238H1366v-4.27c-67.87-24-146.44-43.08-230.75-53.19-253.33-27.78-293.94,51.64-541.13,29.89C318.08,186.31,289.49,32.92,6.9,11.73c-5.21-.42-10.56-.7-15.9-1V238Z" transform="translate(9.5 -10.22)"></path>
                    </svg>''')
                ),
                footer()
            )
        )
    except Exception as e:
        print(f"Error in post detail route: {e}")
        return (
            Title("Error - Nemesis Blog"),
            Div(cls="container mt-5")(
                H1("Error Loading Post"),
                P("There was an error loading this post. Please try again."),
                A(href="/blog", cls="btn btn-primary")("← Back to Blog")
            )
        )

@rt("/post/{post_id}/comment", methods=["POST"])
async def post_comment_submit(post_id: str, name: str, email: str, website: str = "", comment: str = ""):
    """Handle comment submission for a post"""
    try:
        success = await submit_comment(post_id, name, email, website, comment)
        if success:
            return (
                Title("Comment Submitted - Nemesis Blog"),
                Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
                Div(cls="container mt-5")(
                    Div(cls="alert alert-success", role="alert")(
                        H4(cls="alert-heading")("Comment Submitted Successfully!"),
                        P(f"Thank you {name}, your comment has been submitted for review."),
                        Hr(),
                        P(cls="mb-0")("Your comment: ", Em(comment[:100] + "..." if len(comment) > 100 else comment))
                    ),
                    A(href=f"/post/{post_id}", cls="btn btn-primary mt-3")("← Back to Post"),
                    A(href="/blog", cls="btn btn-secondary mt-3 ml-2")("← Back to Blog")
                )
            )
        else:
            raise Exception("Comment submission failed")
    except Exception as e:
        print(f"Comment submission error: {e}")
        return (
            Title("Comment Error - Nemesis Blog"),
            Div(cls="container mt-5")(
                Div(cls="alert alert-danger")(
                    H4("Comment Failed to Submit"),
                    P("There was an error submitting your comment. Please try again."),
                    A(href=f"/post/{post_id}", cls="btn btn-primary")("← Back to Post")
                )
            )
        )

# =====================================================
# SEARCH ROUTE
# =====================================================

@rt("/search")
async def search_results(q: str = ""):
    """Search results page"""
    try:
        if not q or len(q.strip()) < 2:
            return (
                Title("Search - Nemesis Blog"),
                Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
                search_overlay(),
                search_form(),
                Div(id="page-wrapper", cls="feed-view")(
                    navbar(),
                    Div(cls="container mt-5")(
                        H1("Search"),
                        P("Please enter a search term with at least 2 characters."),
                        A(href="/", cls="btn btn-primary")("← Back to Home")
                    ),
                    footer()
                )
            )
        
        # Get search results from database
        data = await search_posts(q)
        posts = data.get("posts", [])
        total = data.get("total", 0)
        
        # Get categories for sidebar
        homepage_data = await get_homepage_data()
        categories = homepage_data.get("categories", [])
        
        return (
            Title(f"Search Results for '{q}' - Nemesis Blog"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            search_overlay(),
            search_form(),
            Div(id="page-wrapper", cls="feed-view")(
                navbar(),
                Div(cls="outer-wrapper clearfix", id="outer-wrapper")(
                    Div(cls="container fbt-elastic-container")(
                        Div(cls="row justify-content-center")(
                            Div(cls="fbt-main-wrapper col-xl-12")(
                                Div(id="main-wrapper")(
                                    Div(cls="main-section", id="main_content")(
                                        Div(cls="fbt-sep-title")(
                                            H4(cls="title title-heading-left")(f"Search Results for '{q}'"),
                                            Div(cls="title-sep-container")(
                                                Div(cls="title-sep sep-double")
                                            )
                                        ),
                                        P(f"Found {total} result{'s' if total != 1 else ''} for your search."),
                                        Div(cls="blog-posts fbt-index-post-wrap card-columns")(
                                            *[blog_post_card(post) for post in posts]
                                        ) if posts else Div(cls="alert alert-info")(
                                            H5("No Results Found"),
                                            P(f"No posts found matching '{q}'. Try different keywords or browse our categories."),
                                            A(href="/blog", cls="btn btn-primary")("Browse All Posts")
                                        )
                                    )
                                )
                            ),
                            sidebar(categories)
                        )
                    )
                ),
                newsletter_section(),
                footer()
            )
        )
    except Exception as e:
        print(f"Error in search route: {e}")
        return (
            Title("Search Error - Nemesis Blog"),
            Div(cls="container mt-5")(
                H1("Search Error"),
                P("There was an error performing your search. Please try again."),
                A(href="/", cls="btn btn-primary")("← Back to Home")
            )
        )

# =====================================================
# ERROR HANDLING
# =====================================================

@rt("/test-db")
async def test_database():
    """Test database connection"""
    try:
        data = await get_homepage_data()
        return {
            "status": "success",
            "message": "Database connection working",
            "data_preview": {
                "featured_post": bool(data.get("featured_post")),
                "regular_posts_count": len(data.get("regular_posts", [])),
                "categories_count": len(data.get("categories", []))
            }
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Database connection failed: {str(e)}",
            "suggestion": "Check your .env file and Supabase configuration"
        }

if __name__ == "__main__":
    serve()