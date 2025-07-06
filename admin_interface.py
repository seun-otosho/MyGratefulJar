"""
Admin Interface Components for Nemesis Blog Platform
Phase 4.2: Complete admin dashboard with content management
"""

from fasthtml.common import *
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio

# Import authentication system
try:
    from auth_system import UserRole, AuthSession
    from auth_system_minimal import UserRole, AuthSession
except ImportError:
    from auth_system_minimal import UserRole, AuthSession

from middleware import AuthContext, get_auth_context, handle_auth_error

# =====================================================
# ADMIN LAYOUT COMPONENTS
# =====================================================

def admin_layout(title: str, content, auth_ctx: AuthContext, active_section: str = "dashboard"):
    """Admin layout with sidebar navigation"""
    return (
        Title(f"{title} - Admin - Nemesis Blog"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Link(href="./css/bootstrap.min.css", rel="stylesheet"),
        Link(href="./css/style.css", rel="stylesheet"),
        Link(href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css", rel="stylesheet"),
        Style(admin_custom_css()),
        Div(cls="admin-wrapper")(
            admin_header(auth_ctx),
            Div(cls="admin-container")(
                admin_sidebar(auth_ctx, active_section),
                Div(cls="admin-main")(
                    content
                )
            )
        ),
        Script(src="./js/jquery.min.js"),
        Script(src="./js/bootstrap.bundle.min.js"),
        Script(admin_custom_js())
    )

def admin_custom_css():
    """Custom CSS for admin interface"""
    return """
    .admin-wrapper {
        min-height: 100vh;
        background-color: #f8f9fa;
    }
    .admin-header {
        background: #343a40;
        color: white;
        padding: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .admin-container {
        display: flex;
        min-height: calc(100vh - 80px);
    }
    .admin-sidebar {
        width: 250px;
        background: white;
        border-right: 1px solid #dee2e6;
        padding: 0;
    }
    .admin-main {
        flex: 1;
        padding: 2rem;
        overflow-y: auto;
    }
    .admin-nav-item {
        display: block;
        padding: 0.75rem 1.5rem;
        color: #495057;
        text-decoration: none;
        border-bottom: 1px solid #f8f9fa;
        transition: all 0.2s;
    }
    .admin-nav-item:hover {
        background-color: #f8f9fa;
        color: #007bff;
        text-decoration: none;
    }
    .admin-nav-item.active {
        background-color: #007bff;
        color: white;
    }
    .admin-nav-section {
        padding: 1rem 1.5rem 0.5rem;
        font-weight: 600;
        color: #6c757d;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .admin-card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .admin-stats-card {
        text-align: center;
        padding: 2rem;
        border-radius: 8px;
        color: white;
        margin-bottom: 1rem;
    }
    .admin-table {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .btn-admin {
        border-radius: 6px;
        font-weight: 500;
        padding: 0.5rem 1rem;
    }
    """

def admin_custom_js():
    """Custom JavaScript for admin interface"""
    return """
    // Admin interface JavaScript
    $(document).ready(function() {
        // Auto-hide alerts after 5 seconds
        setTimeout(function() {
            $('.alert').fadeOut();
        }, 5000);
        
        // Confirm delete actions
        $('.btn-delete').click(function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
        
        // Toggle sidebar on mobile
        $('.sidebar-toggle').click(function() {
            $('.admin-sidebar').toggleClass('show');
        });
    });
    """

def admin_header(auth_ctx: AuthContext):
    """Admin header with user info and navigation"""
    return Div(cls="admin-header")(
        Div(cls="container-fluid")(
            Div(cls="d-flex justify-content-between align-items-center")(
                Div(cls="d-flex align-items-center")(
                    Button(cls="btn btn-link text-white d-md-none sidebar-toggle")(
                        I(cls="fas fa-bars")
                    ),
                    H4(cls="mb-0 ml-2")("Nemesis Admin")
                ),
                Div(cls="d-flex align-items-center")(
                    Span(cls="mr-3")(f"Welcome, {auth_ctx.session.display_name}"),
                    Div(cls="dropdown")(
                        Button(
                            cls="btn btn-secondary dropdown-toggle",
                            type="button",
                            id="userDropdown",
                            data_toggle="dropdown"
                        )(
                            I(cls="fas fa-user mr-2"),
                            auth_ctx.session.display_name or "User"
                        ),
                        Div(cls="dropdown-menu dropdown-menu-right")(
                            A(cls="dropdown-item", href="/profile")(
                                I(cls="fas fa-user mr-2"), "Profile"
                            ),
                            A(cls="dropdown-item", href="/")(
                                I(cls="fas fa-home mr-2"), "View Site"
                            ),
                            Div(cls="dropdown-divider"),
                            A(cls="dropdown-item", href="/logout")(
                                I(cls="fas fa-sign-out-alt mr-2"), "Logout"
                            )
                        )
                    )
                )
            )
        )
    )

def admin_sidebar(auth_ctx: AuthContext, active_section: str = "dashboard"):
    """Admin sidebar navigation"""
    nav_items = get_admin_nav_items(auth_ctx)
    
    return Div(cls="admin-sidebar")(
        Div(cls="py-3")(
            *[render_nav_section(section, active_section) for section in nav_items]
        )
    )

def get_admin_nav_items(auth_ctx: AuthContext) -> List[Dict]:
    """Get navigation items based on user role"""
    items = [
        {
            "section": "Overview",
            "items": [
                {"name": "Dashboard", "url": "/admin", "icon": "fas fa-tachometer-alt", "key": "dashboard"}
            ]
        }
    ]
    
    if auth_ctx.is_author():
        items.append({
            "section": "Content",
            "items": [
                {"name": "New Post", "url": "/admin/posts/new", "icon": "fas fa-plus", "key": "posts-new"},
                {"name": "My Posts", "url": "/admin/my-posts", "icon": "fas fa-edit", "key": "my-posts"},
                {"name": "Drafts", "url": "/admin/drafts", "icon": "fas fa-file-alt", "key": "drafts"}
            ]
        })
    
    if auth_ctx.is_editor():
        items.append({
            "section": "Management",
            "items": [
                {"name": "All Posts", "url": "/admin/posts", "icon": "fas fa-newspaper", "key": "posts"},
                {"name": "Comments", "url": "/admin/comments", "icon": "fas fa-comments", "key": "comments"},
                {"name": "Categories", "url": "/admin/categories", "icon": "fas fa-tags", "key": "categories"},
                {"name": "Media", "url": "/admin/media", "icon": "fas fa-images", "key": "media"}
            ]
        })
    
    if auth_ctx.is_admin():
        items.append({
            "section": "Administration",
            "items": [
                {"name": "Users", "url": "/admin/users", "icon": "fas fa-users", "key": "users"},
                {"name": "Settings", "url": "/admin/settings", "icon": "fas fa-cog", "key": "settings"},
                {"name": "Analytics", "url": "/admin/analytics", "icon": "fas fa-chart-bar", "key": "analytics"}
            ]
        })
    
    return items

def render_nav_section(section: Dict, active_section: str):
    """Render a navigation section"""
    return Fragment(
        Div(cls="admin-nav-section")(section["section"]),
        *[A(
            cls=f"admin-nav-item {'active' if item['key'] == active_section else ''}",
            href=item["url"]
        )(
            I(cls=f"{item['icon']} mr-2"),
            item["name"]
        ) for item in section["items"]]
    )

# =====================================================
# DASHBOARD COMPONENTS
# =====================================================

def admin_dashboard_content(auth_ctx: AuthContext):
    """Main dashboard content"""
    return Div(
        # Page header
        Div(cls="d-flex justify-content-between align-items-center mb-4")(
            H1("Dashboard"),
            Div(
                A(href="/admin/posts/new", cls="btn btn-primary btn-admin")(
                    I(cls="fas fa-plus mr-2"), "New Post"
                ) if auth_ctx.is_author() else ""
            )
        ),
        
        # Stats cards
        dashboard_stats_cards(auth_ctx),
        
        # Recent activity and quick actions
        Div(cls="row")(
            Div(cls="col-lg-8")(
                recent_activity_card(auth_ctx)
            ),
            Div(cls="col-lg-4")(
                quick_actions_card(auth_ctx)
            )
        )
    )

def dashboard_stats_cards(auth_ctx: AuthContext):
    """Dashboard statistics cards"""
    # TODO: Get real stats from database
    stats = [
        {"title": "Total Posts", "value": "12", "icon": "fas fa-newspaper", "color": "bg-primary"},
        {"title": "Comments", "value": "48", "icon": "fas fa-comments", "color": "bg-success"},
        {"title": "Views", "value": "1,234", "icon": "fas fa-eye", "color": "bg-info"},
    ]
    
    if auth_ctx.is_admin():
        stats.append({"title": "Users", "value": "8", "icon": "fas fa-users", "color": "bg-warning"})
    
    return Div(cls="row mb-4")(
        *[Div(cls="col-md-3")(
            Div(cls=f"admin-stats-card {stat['color']}")(
                I(cls=f"{stat['icon']} fa-2x mb-2"),
                H3(stat["value"]),
                P(stat["title"])
            )
        ) for stat in stats]
    )

def recent_activity_card(auth_ctx: AuthContext):
    """Recent activity card"""
    # TODO: Get real activity from database
    activities = [
        {"action": "New post published", "item": "Getting Started with FastHTML", "time": "2 hours ago"},
        {"action": "Comment approved", "item": "Welcome to our blog", "time": "4 hours ago"},
        {"action": "User registered", "item": "john@example.com", "time": "1 day ago"},
    ]
    
    return Div(cls="admin-card")(
        Div(cls="card-header")(
            H5("Recent Activity")
        ),
        Div(cls="card-body")(
            Div(cls="list-group list-group-flush")(
                *[Div(cls="list-group-item d-flex justify-content-between align-items-center")(
                    Div(
                        Strong(activity["action"]),
                        Br(),
                        Small(cls="text-muted")(activity["item"])
                    ),
                    Small(cls="text-muted")(activity["time"])
                ) for activity in activities]
            ) if activities else P(cls="text-muted")("No recent activity")
        )
    )

def quick_actions_card(auth_ctx: AuthContext):
    """Quick actions card"""
    actions = []
    
    if auth_ctx.is_author():
        actions.extend([
            {"name": "Write New Post", "url": "/admin/posts/new", "icon": "fas fa-plus", "color": "btn-primary"},
            {"name": "View Drafts", "url": "/admin/drafts", "icon": "fas fa-file-alt", "color": "btn-secondary"}
        ])
    
    if auth_ctx.is_editor():
        actions.extend([
            {"name": "Moderate Comments", "url": "/admin/comments", "icon": "fas fa-comments", "color": "btn-warning"},
            {"name": "Manage Categories", "url": "/admin/categories", "icon": "fas fa-tags", "color": "btn-info"}
        ])
    
    if auth_ctx.is_admin():
        actions.extend([
            {"name": "User Management", "url": "/admin/users", "icon": "fas fa-users", "color": "btn-danger"},
            {"name": "Site Settings", "url": "/admin/settings", "icon": "fas fa-cog", "color": "btn-dark"}
        ])
    
    return Div(cls="admin-card")(
        Div(cls="card-header")(
            H5("Quick Actions")
        ),
        Div(cls="card-body")(
            Div(cls="d-grid gap-2")(
                *[A(
                    href=action["url"],
                    cls=f"btn {action['color']} btn-admin mb-2"
                )(
                    I(cls=f"{action['icon']} mr-2"),
                    action["name"]
                ) for action in actions]
            ) if actions else P(cls="text-muted")("No actions available")
        )
    )

# =====================================================
# POST MANAGEMENT COMPONENTS
# =====================================================

def post_list_content(auth_ctx: AuthContext, posts: List[Dict] = None):
    """Post management list"""
    if not posts:
        posts = get_sample_posts()  # TODO: Get from database
    
    return Div(
        # Page header
        Div(cls="d-flex justify-content-between align-items-center mb-4")(
            H1("Manage Posts"),
            A(href="/admin/posts/new", cls="btn btn-primary btn-admin")(
                I(cls="fas fa-plus mr-2"), "New Post"
            )
        ),
        
        # Filters and search
        post_filters(),
        
        # Posts table
        posts_table(posts, auth_ctx)
    )

def post_filters():
    """Post filtering controls"""
    return Div(cls="admin-card mb-4")(
        Div(cls="card-body")(
            Form(cls="row g-3")(
                Div(cls="col-md-4")(
                    Input(type="text", cls="form-control", placeholder="Search posts...")
                ),
                Div(cls="col-md-3")(
                    Select(cls="form-control")(
                        Option(value="")("All Status"),
                        Option(value="published")("Published"),
                        Option(value="draft")("Draft"),
                        Option(value="archived")("Archived")
                    )
                ),
                Div(cls="col-md-3")(
                    Select(cls="form-control")(
                        Option(value="")("All Categories"),
                        Option(value="technology")("Technology"),
                        Option(value="design")("Design"),
                        Option(value="lifestyle")("Lifestyle")
                    )
                ),
                Div(cls="col-md-2")(
                    Button(type="submit", cls="btn btn-primary w-100")("Filter")
                )
            )
        )
    )

def posts_table(posts: List[Dict], auth_ctx: AuthContext):
    """Posts management table"""
    return Div(cls="admin-table")(
        Table(cls="table table-hover mb-0")(
            Thead(cls="table-light")(
                Tr(
                    Th("Title"),
                    Th("Author"),
                    Th("Category"),
                    Th("Status"),
                    Th("Date"),
                    Th("Actions", cls="text-center")
                )
            ),
            Tbody(
                *[Tr(
                    Td(
                        A(href=f"/admin/posts/{post['id']}/edit", cls="text-decoration-none")(
                            Strong(post["title"][:50] + "..." if len(post["title"]) > 50 else post["title"])
                        ),
                        Br(),
                        Small(cls="text-muted")(f"{post.get('view_count', 0)} views")
                    ),
                    Td(post["author"]),
                    Td(
                        Span(cls="badge badge-secondary")(post["category"])
                    ),
                    Td(
                        Span(cls=f"badge badge-{get_status_color(post['status'])}")(
                            post["status"].title()
                        )
                    ),
                    Td(post["date"]),
                    Td(cls="text-center")(
                        Div(cls="btn-group btn-group-sm")(
                            A(href=f"/post/{post['id']}", cls="btn btn-outline-primary", title="View")(
                                I(cls="fas fa-eye")
                            ),
                            A(href=f"/admin/posts/{post['id']}/edit", cls="btn btn-outline-secondary", title="Edit")(
                                I(cls="fas fa-edit")
                            ),
                            Button(cls="btn btn-outline-danger btn-delete", title="Delete")(
                                I(cls="fas fa-trash")
                            ) if auth_ctx.can_edit_post(post.get('author_id', '')) else ""
                        )
                    )
                ) for post in posts]
            )
        )
    )

def get_status_color(status: str) -> str:
    """Get badge color for post status"""
    colors = {
        "published": "success",
        "draft": "warning", 
        "archived": "secondary",
        "scheduled": "info"
    }
    return colors.get(status, "secondary")

def get_sample_posts() -> List[Dict]:
    """Sample posts for testing"""
    return [
        {
            "id": "1",
            "title": "Getting Started with FastHTML",
            "author": "Admin User",
            "category": "Technology",
            "status": "published",
            "date": "2024-01-15",
            "view_count": 245,
            "author_id": "admin-1"
        },
        {
            "id": "2", 
            "title": "Building Modern Web Applications",
            "author": "Author User",
            "category": "Development",
            "status": "draft",
            "date": "2024-01-14",
            "view_count": 0,
            "author_id": "author-1"
        },
        {
            "id": "3",
            "title": "Design Principles for 2024",
            "author": "Editor User", 
            "category": "Design",
            "status": "published",
            "date": "2024-01-13",
            "view_count": 189,
            "author_id": "editor-1"
        }
    ]

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def create_admin_routes(app, rt):
    """Create admin routes"""
    
    @rt("/admin")
    async def admin_dashboard(request):
        """Admin dashboard"""
        auth_ctx = get_auth_context(request)
        
        if not auth_ctx.is_authenticated:
            return handle_auth_error("unauthenticated")
        
        if not auth_ctx.is_author():
            return handle_auth_error("unauthorized", "Author access or higher required")
        
        return admin_layout(
            "Dashboard",
            admin_dashboard_content(auth_ctx),
            auth_ctx,
            "dashboard"
        )
    
    @rt("/admin/posts")
    async def admin_posts(request):
        """Posts management"""
        auth_ctx = get_auth_context(request)
        
        if not auth_ctx.is_authenticated:
            return handle_auth_error("unauthenticated")
        
        if not auth_ctx.is_editor():
            return handle_auth_error("unauthorized", "Editor access required")
        
        return admin_layout(
            "Manage Posts",
            post_list_content(auth_ctx),
            auth_ctx,
            "posts"
        )

def add_admin_routes_to_app(app, rt):
    """Add admin routes to FastHTML app"""
    create_admin_routes(app, rt)
    print("✅ Admin interface routes added to FastHTML app")

if __name__ == "__main__":
    print("✅ Admin interface module loaded successfully!")
    print("Use add_admin_routes_to_app(app, rt) to add admin routes to your FastHTML app.")