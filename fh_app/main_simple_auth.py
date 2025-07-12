"""
Simplified FastHTML Nemesis Blog with Basic Authentication
Works without external dependencies for testing
"""

from fasthtml.common import *
from datetime import datetime
import os
from typing import Optional, Dict, Any

# Simple in-memory session storage for testing
sessions = {}
users = {
    "admin@example.com": {
        "id": "1",
        "email": "admin@example.com", 
        "password": "admin123",  # In production, this would be hashed
        "display_name": "Admin User",
        "role": "admin",
        "avatar_url": "./images/default-avatar.jpg"
    },
    "author@example.com": {
        "id": "2", 
        "email": "author@example.com",
        "password": "author123",
        "display_name": "Author User", 
        "role": "author",
        "avatar_url": "./images/default-avatar.jpg"
    }
}

# Custom CSS and JS headers
custom_hdrs = [
    Link(rel="shortcut icon", href="favicon.ico", type="image/x-icon"),
    Link(href="https://fonts.googleapis.com/css?family=Montserrat:900%7CNunito:400,700%7COswald%7CRoboto", rel="stylesheet"),
    Link(href="./css/animate.min.css", rel="stylesheet", media="screen"),
    Link(href="./css/fonts.css", rel="stylesheet", media="screen"),
    Link(href="./css/bootstrap.min.css", rel="stylesheet", media="screen"),
    Link(href="./css/style.css", rel="stylesheet", media="screen"),
    Script(src="../js/jquery.min.js"),
    Script(src="../js/bootstrap.bundle.min.js"),
    Script(src="../js/plugins.js"),
    Script(src="../js/main.js"),
]

app, rt = fast_app(hdrs=custom_hdrs)

# =====================================================
# SIMPLE AUTHENTICATION HELPERS
# =====================================================

def get_session_user(request) -> Optional[Dict]:
    """Get user from session cookie"""
    try:
        if hasattr(request, 'cookies'):
            session_id = request.cookies.get('session_id')
            if session_id and session_id in sessions:
                return sessions[session_id]
    except:
        pass
    return None

def create_session(user: Dict) -> str:
    """Create a simple session"""
    import uuid
    session_id = str(uuid.uuid4())
    sessions[session_id] = user
    return session_id

def is_admin(user: Optional[Dict]) -> bool:
    """Check if user is admin"""
    return user and user.get('role') == 'admin'

def is_author(user: Optional[Dict]) -> bool:
    """Check if user is author or admin"""
    return user and user.get('role') in ['author', 'admin']

# =====================================================
# SIMPLE UI COMPONENTS
# =====================================================

def simple_navbar(user: Optional[Dict] = None):
    """Simple navigation with auth"""
    return Nav(cls="navbar navbar-expand-lg navbar-light bg-light")(
        Div(cls="container")(
            A(cls="navbar-brand", href="/")(
                Img(src="../images/logo_nemesis.png", height="40", alt="Nemesis")
            ),
            Div(cls="navbar-nav ml-auto")(
                A(cls="nav-link", href="/")("Home"),
                A(cls="nav-link", href="/blog")("Blog"),
                A(cls="nav-link", href="/contact")("Contact"),
                # Auth-specific navigation
                user_nav(user) if user else guest_nav()
            )
        )
    )

def user_nav(user: Dict):
    """Navigation for authenticated users"""
    return Fragment(
        A(cls="nav-link", href="/profile")(f"Welcome, {user['display_name']}"),
        A(cls="nav-link", href="/admin")("Admin") if is_admin(user) else "",
        A(cls="nav-link", href="/logout")("Logout")
    )

def guest_nav():
    """Navigation for guests"""
    return Fragment(
        A(cls="nav-link", href="/login")("Login"),
        A(cls="nav-link", href="/register")("Register")
    )

def login_form(error: str = ""):
    """Simple login form"""
    return Div(cls="container mt-5")(
        Div(cls="row justify-content-center")(
            Div(cls="col-md-4")(
                Div(cls="card")(
                    Div(cls="card-header")(
                        H3("Login")
                    ),
                    Div(cls="card-body")(
                        Div(cls="alert alert-danger")(error) if error else "",
                        Form(method="POST", action="/login")(
                            Div(cls="form-group mb-3")(
                                Label(**{"for": "email"})("Email"),
                                Input(type="email", cls="form-control", name="email", required=True)
                            ),
                            Div(cls="form-group mb-3")(
                                Label(**{"for": "password"})("Password"),
                                Input(type="password", cls="form-control", name="password", required=True)
                            ),
                            Button(type="submit", cls="btn btn-primary")("Login")
                        ),
                        Hr(),
                        P("Demo accounts:"),
                        Small("admin@example.com / admin123 (Admin)"), Br(),
                        Small("author@example.com / author123 (Author)")
                    )
                )
            )
        )
    )

def admin_dashboard(user: Dict):
    """Simple admin dashboard"""
    return Div(cls="container mt-5")(
        H1(f"Welcome to Admin Dashboard, {user['display_name']}!"),
        P(f"Role: {user['role'].title()}"),
        
        Div(cls="row")(
            Div(cls="col-md-4")(
                Div(cls="card")(
                    Div(cls="card-body")(
                        H5("Content Management"),
                        P("Manage your blog posts and content."),
                        A(href="/admin/posts", cls="btn btn-primary")("Manage Posts")
                    )
                )
            ),
            Div(cls="col-md-4")(
                Div(cls="card")(
                    Div(cls="card-body")(
                        H5("User Management"),
                        P("Manage users and permissions.") if is_admin(user) else P("View user information."),
                        A(href="/admin/users", cls="btn btn-primary")("Manage Users") if is_admin(user) else ""
                    )
                )
            ),
            Div(cls="col-md-4")(
                Div(cls="card")(
                    Div(cls="card-body")(
                        H5("Settings"),
                        P("Configure site settings."),
                        A(href="/admin/settings", cls="btn btn-primary")("Settings") if is_admin(user) else ""
                    )
                )
            )
        )
    )

# =====================================================
# ROUTES
# =====================================================

@rt("/")
def homepage(request):
    """Homepage with auth context"""
    user = get_session_user(request)
    
    return (
        Title("Nemesis Blog - Home"),
        simple_navbar(user),
        Div(cls="container mt-5")(
            H1("Welcome to Nemesis Blog"),
            P("A modern blog platform with authentication."),
            
            Div(cls="alert alert-info")(
                H4("Authentication Demo"),
                P("This is a simplified version to test authentication functionality."),
                P("Try logging in with the demo accounts provided on the login page.")
            ) if not user else Div(cls="alert alert-success")(
                H4(f"Welcome back, {user['display_name']}!"),
                P(f"You are logged in as: {user['role'].title()}"),
                A(href="/admin", cls="btn btn-primary")("Go to Admin") if is_author(user) else ""
            )
        )
    )

@rt("/login")
def login_page(request):
    """Login page"""
    user = get_session_user(request)
    if user:
        return RedirectResponse("/")
    
    return (
        Title("Login - Nemesis Blog"),
        simple_navbar(),
        login_form()
    )

@rt("/login", methods=["POST"])
async def login_submit(request):
    """Handle login"""
    form = await request.form()
    email = form.get('email', '').strip()
    password = form.get('password', '')
    
    # Simple authentication check
    if email in users and users[email]['password'] == password:
        user = users[email]
        session_id = create_session(user)
        
        response = RedirectResponse("/")
        response.set_cookie("session_id", session_id, max_age=86400)  # 24 hours
        return response
    else:
        return (
            Title("Login - Nemesis Blog"),
            simple_navbar(),
            login_form("Invalid email or password")
        )

@rt("/logout")
def logout(request):
    """Logout user"""
    session_id = request.cookies.get('session_id')
    if session_id and session_id in sessions:
        del sessions[session_id]
    
    response = RedirectResponse("/")
    response.delete_cookie("session_id")
    return response

@rt("/admin")
def admin_page(request):
    """Admin dashboard"""
    user = get_session_user(request)
    
    if not user:
        return RedirectResponse("/login")
    
    if not is_author(user):
        return (
            Title("Access Denied"),
            simple_navbar(user),
            Div(cls="container mt-5")(
                Div(cls="alert alert-danger")(
                    H4("Access Denied"),
                    P("You need author or admin privileges to access this page."),
                    A(href="/", cls="btn btn-primary")("← Back to Home")
                )
            )
        )
    
    return (
        Title("Admin Dashboard - Nemesis Blog"),
        simple_navbar(user),
        admin_dashboard(user)
    )

@rt("/profile")
def profile_page(request):
    """User profile page"""
    user = get_session_user(request)
    
    if not user:
        return RedirectResponse("/login")
    
    return (
        Title("Profile - Nemesis Blog"),
        simple_navbar(user),
        Div(cls="container mt-5")(
            H1("User Profile"),
            Div(cls="card")(
                Div(cls="card-body")(
                    H5(f"Display Name: {user['display_name']}"),
                    P(f"Email: {user['email']}"),
                    P(f"Role: {user['role'].title()}"),
                    P(f"User ID: {user['id']}")
                )
            )
        )
    )

@rt("/test-auth")
def test_auth(request):
    """Test authentication status"""
    user = get_session_user(request)
    
    return {
        "authenticated": user is not None,
        "user": user,
        "is_admin": is_admin(user),
        "is_author": is_author(user),
        "sessions_count": len(sessions)
    }

if __name__ == "__main__":
    print("🚀 Starting Nemesis Blog with Simple Authentication")
    print("📝 Demo accounts:")
    print("   Admin: admin@example.com / admin123")
    print("   Author: author@example.com / author123")
    print("🌐 Visit: http://localhost:5001")
    serve()