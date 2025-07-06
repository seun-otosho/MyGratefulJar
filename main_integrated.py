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