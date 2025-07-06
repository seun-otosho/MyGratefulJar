"""
FastHTML Nemesis Blog with Complete Authentication System
Integrates Supabase database, authentication, and all blog functionality
"""

from fasthtml.common import *
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv

from main import footer, newsletter_section, hero_slider

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

# Import authentication system
try:
    from auth_system import (
        auth_service,
        UserRole,
        AuthSession
    )
    AUTH_AVAILABLE = True
except ImportError:
    # Fallback to minimal auth system
    from auth_system_minimal import (
        auth_service,
        UserRole,
        AuthSession
    )
    AUTH_AVAILABLE = False
    print("Using minimal authentication system")

from middleware import (
    session_manager,
    get_auth_context,
    handle_auth_error,
    get_user_navigation,
    get_admin_sidebar,
    AuthContext
)

from auth_routes import add_auth_routes_to_app
from admin_interface import add_admin_routes_to_app

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
# ENHANCED TEMPLATE COMPONENTS WITH AUTH
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

def navbar_with_auth(auth_ctx: AuthContext = None):
    """Main navigation component with authentication"""
    if not auth_ctx:
        auth_ctx = AuthContext()
    
    # Get user navigation items
    nav_items = get_user_navigation(auth_ctx)
    
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
                Span(cls="fbt-sidenav ml-1 active", onclick="openNav()")("☰"),
                # User avatar/login button
                user_nav_button(auth_ctx) if auth_ctx.is_authenticated else login_nav_button()
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
                    # Admin menu for authorized users
                    admin_nav_menu(auth_ctx) if auth_ctx.is_author() else Li(),
                    # User menu
                    user_nav_menu(auth_ctx) if auth_ctx.is_authenticated else guest_nav_menu()
                )
            )
        )
    )

def user_nav_button(auth_ctx: AuthContext):
    """User navigation button with avatar"""
    avatar_url = auth_ctx.session.avatar_url or "./images/default-avatar.jpg"
    display_name = auth_ctx.session.display_name or "User"
    
    return Div(cls="dropdown")(
        A(
            cls="nav-link dropdown-toggle d-flex align-items-center",
            href="#",
            id="userDropdown",
            role="button",
            data_toggle="dropdown",
            aria_haspopup="true",
            aria_expanded="false"
        )(
            Img(src=avatar_url, cls="rounded-circle mr-2", width="30", height="30"),
            Span(display_name)
        ),
        Div(cls="dropdown-menu dropdown-menu-right", aria_labelledby="userDropdown")(
            A(cls="dropdown-item", href="/profile")(I(cls="fa fa-user mr-2"), "Profile"),
            A(cls="dropdown-item", href="/my-posts")(I(cls="fa fa-edit mr-2"), "My Posts") if auth_ctx.is_author() else "",
            A(cls="dropdown-item", href="/admin")(I(cls="fa fa-cog mr-2"), "Admin") if auth_ctx.is_editor() else "",
            Div(cls="dropdown-divider"),
            A(cls="dropdown-item", href="/logout")(I(cls="fa fa-sign-out mr-2"), "Logout")
        )
    )

def login_nav_button():
    """Login button for guests"""
    return Div(cls="ml-2")(
        A(href="/login", cls="btn btn-outline-primary btn-sm mr-2")("Login"),
        A(href="/register", cls="btn btn-primary btn-sm")("Register")
    )

def admin_nav_menu(auth_ctx: AuthContext):
    """Admin navigation menu"""
    if not auth_ctx.is_author():
        return Li()
    
    return Li(cls="nav-item dropdown")(
        A(href="#", cls="nav-link dropdown-toggle", aria_haspopup="true", aria_expanded="false", data_toggle="dropdown")("Admin"),
        Div(cls="dropdown-menu")(
            A(href="/admin/posts/new", cls="dropdown-item")("New Post") if auth_ctx.is_author() else "",
            A(href="/admin/posts", cls="dropdown-item")("Manage Posts") if auth_ctx.is_editor() else "",
            A(href="/admin/comments", cls="dropdown-item")("Comments") if auth_ctx.is_editor() else "",
            A(href="/admin/users", cls="dropdown-item")("Users") if auth_ctx.is_admin() else "",
            A(href="/admin/settings", cls="dropdown-item")("Settings") if auth_ctx.is_admin() else ""
        )
    )

def user_nav_menu(auth_ctx: AuthContext):
    """User navigation menu for authenticated users"""
    return Li(cls="nav-item dropdown")(
        A(href="#", cls="nav-link dropdown-toggle", aria_haspopup="true", aria_expanded="false", data_toggle="dropdown")(
            auth_ctx.session.display_name or "User"
        ),
        Div(cls="dropdown-menu")(
            A(href="/profile", cls="dropdown-item")("Profile"),
            A(href="/my-posts", cls="dropdown-item")("My Posts") if auth_ctx.is_author() else "",
            Div(cls="dropdown-divider"),
            A(href="/logout", cls="dropdown-item")("Logout")
        )
    )

def guest_nav_menu():
    """Navigation menu for guests"""
    return Fragment(
        Li(cls="nav-item")(
            A(href="/login", cls="nav-link")("Login")
        ),
        Li(cls="nav-item")(
            A(href="/register", cls="nav-link")("Register")
        )
    )

def enhanced_sidebar(categories=None, auth_ctx: AuthContext = None):
    """Enhanced sidebar with authentication context"""
    if not categories:
        categories = []
    if not auth_ctx:
        auth_ctx = AuthContext()
    
    return Div(cls="sidebar-wrapper", id="sidebar-wrapper")(
        Div(cls="sidebar-wrapper__content")(
            Div(cls="navigation-container clearfix")(
                Span(cls="closebtn", onclick="closeNav()")("×")
            ),
            
            # User info section
            user_sidebar_section(auth_ctx) if auth_ctx.is_authenticated else guest_sidebar_section(),
            
            # Main navigation
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
            
            # Categories
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
            ),
            
            # Admin quick actions
            admin_sidebar_section(auth_ctx) if auth_ctx.is_author() else Div()
        )
    )

def user_sidebar_section(auth_ctx: AuthContext):
    """User info section in sidebar"""
    avatar_url = auth_ctx.session.avatar_url or "./images/default-avatar.jpg"
    display_name = auth_ctx.session.display_name or "User"
    role_badge_color = {
        UserRole.ADMIN: "danger",
        UserRole.EDITOR: "warning", 
        UserRole.AUTHOR: "info",
        UserRole.USER: "secondary"
    }.get(auth_ctx.session.role, "secondary")
    
    return Div(cls="sidebar-user-info p-3 border-bottom")(
        Div(cls="d-flex align-items-center")(
            Img(src=avatar_url, cls="rounded-circle mr-3", width="50", height="50"),
            Div(
                H6(cls="mb-1")(display_name),
                Span(cls=f"badge badge-{role_badge_color}")(auth_ctx.session.role.value.title())
            )
        ),
        Div(cls="mt-2")(
            A(href="/profile", cls="btn btn-sm btn-outline-primary mr-2")("Profile"),
            A(href="/logout", cls="btn btn-sm btn-outline-secondary")("Logout")
        )
    )

def guest_sidebar_section():
    """Guest section in sidebar"""
    return Div(cls="sidebar-guest-info p-3 border-bottom text-center")(
        H6("Welcome to Nemesis Blog"),
        P(cls="text-muted small")("Join our community to create and share content"),
        A(href="/register", cls="btn btn-primary btn-sm mr-2")("Sign Up"),
        A(href="/login", cls="btn btn-outline-primary btn-sm")("Login")
    )

def admin_sidebar_section(auth_ctx: AuthContext):
    """Admin quick actions in sidebar"""
    if not auth_ctx.is_author():
        return Div()
    
    admin_items = get_admin_sidebar(auth_ctx)
    
    return Div(cls="sidebar section")(
        Div(cls="widget")(
            Div(cls="fbt-sep-title")(
                H4(cls="title title-heading-left")("Quick Actions"),
                Div(cls="title-sep-container")(
                    Div(cls="title-sep sep-double")
                )
            ),
            Div(cls="widget-content")(
                *[Div(cls="mb-3")(
                    H6(section["section"]),
                    Ul(cls="list-unstyled")(
                        *[Li(
                            A(href=item["url"], cls="text-decoration-none")(
                                I(cls=f"fa {item['icon']} mr-2"),
                                item["name"]
                            )
                        ) for item in section["items"]]
                    )
                ) for section in admin_items]
            )
        )
    )

# =====================================================
# ENHANCED ROUTES WITH AUTHENTICATION
# =====================================================

@rt("/")
async def homepage(request):
    """Homepage route with authentication context"""
    try:
        # Get authentication context
        auth_ctx = get_auth_context(request)
        
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
                navbar_with_auth(auth_ctx),
                hero_slider(featured_post),
                Div(cls="outer-wrapper clearfix", id="outer-wrapper")(
                    Div(cls="container fbt-elastic-container")(
                        Div(cls="row justify-content-center")(
                            Div(cls="fbt-main-wrapper col-xl-12")(
                                Div(id="main-wrapper")(
                                    Div(cls="main-section", id="main_content")(
                                        # Welcome message for authenticated users
                                        welcome_message(auth_ctx) if auth_ctx.is_authenticated else Div(),
                                        Div(cls="blog-posts fbt-index-post-wrap card-columns")(
                                            *[blog_post_card(post, auth_ctx) for post in regular_posts]
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
                            enhanced_sidebar(categories, auth_ctx)
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
        return (
            Title("Nemesis Blog - Loading..."),
            Div(cls="container mt-5")(
                H1("Welcome to Nemesis Blog"),
                P("Loading content... Please check your database connection."),
                A(href="/blog", cls="btn btn-primary")("View Blog")
            )
        )

def welcome_message(auth_ctx: AuthContext):
    """Welcome message for authenticated users"""
    return Div(cls="alert alert-info mb-4")(
        H5(f"Welcome back, {auth_ctx.session.display_name}!"),
        P(cls="mb-0")(
            "Ready to create something amazing? ",
            A(href="/admin/posts/new", cls="alert-link")("Write a new post") if auth_ctx.is_author() else "",
            A(href="/profile", cls="alert-link")("Update your profile") if not auth_ctx.is_author() else ""
        )
    )

def blog_post_card(post, auth_ctx: AuthContext = None):
    """Enhanced blog post card with edit options"""
    video_icon = Span(cls="video-icon")(I(cls="fa fa-play")) if post.get('is_video') else ""
    
    # Check if user can edit this post
    can_edit = auth_ctx and auth_ctx.can_edit_post(post.get('author_id', ''))
    
    return Div(cls="blog-post fbt-index-post card radius-10")(
        Div(cls="fbt-post-thumbnail")(
            A(href=f"/post/{post['id']}")(
                Img(alt="", cls="post-thumbnail lazyloaded", src=post['image'])
            ),
            video_icon,
            # Edit button for authorized users
            Div(cls="post-edit-overlay")(
                A(href=f"/admin/posts/{post['id']}/edit", cls="btn btn-sm btn-warning")(
                    I(cls="fa fa-edit")
                )
            ) if can_edit else Div()
        ),
        Div(cls="fbt-post-caption card-body")(
            H3(cls="post-title h4 card-title")(
                A(href=f"/post/{post['id']}")(post['title'])
            ),
            Div(cls="post-meta")(
                Span(cls="post-author")(A(href="#")(post['author'])),
                Span(cls="post-date published")(post['date']),
                Span(cls="post-category badge badge-primary ml-2")(post.get('category', 'General'))
            ),
            P(cls="post-excerpt card-text")(post['excerpt'])
        )
    )

# # Import and reuse existing components from main_integrated.py
# from main_integrated import (
#     hero_slider,
#     newsletter_section,
#     footer,
#     # Blog listing components
#     headline_section,
#     magazine_navbar,
#     gallery_section,
#     magazine_post_card,
#     blog_sidebar,
#     pagination_nav,
#     # Contact components
#     contact_hero_section,
#     contact_form,
#     contact_info_sidebar,
#     # Single post components
#     single_post_hero,
#     post_content_body,
#     post_footer_section,
#     related_posts_section,
#     comments_section
# )

# =====================================================
# PROTECTED ADMIN ROUTES
# =====================================================

# Admin routes are now handled by admin_interface.py

# Admin components moved to admin_interface.py

# Add authentication routes to the app
add_auth_routes_to_app(app, rt)

# Add admin interface routes to the app
add_admin_routes_to_app(app, rt)

# Add existing routes from main_integrated.py (blog, contact, search, etc.)
# These will be imported and enhanced with authentication context

@rt("/test-auth")
async def test_auth(request):
    """Test authentication system"""
    auth_ctx = get_auth_context(request)
    
    return {
        "authenticated": auth_ctx.is_authenticated,
        "user": auth_ctx.session.dict() if auth_ctx.session else None,
        "is_admin": auth_ctx.is_admin(),
        "is_editor": auth_ctx.is_editor(),
        "is_author": auth_ctx.is_author(),
        "navigation": get_user_navigation(auth_ctx),
        "admin_sidebar": get_admin_sidebar(auth_ctx)
    }

if __name__ == "__main__":
    serve()