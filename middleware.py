"""
FastHTML Middleware for Authentication and Authorization
Handles session validation, route protection, and user context
"""

from typing import Optional, Callable, Any, Dict
from functools import wraps
from fasthtml.common import *
import asyncio
from datetime import datetime

# Import our auth system
from auth_system import (
    auth_service, 
    AuthSession, 
    UserRole, 
    validate_session,
    check_permission
)

# =====================================================
# SESSION MANAGEMENT
# =====================================================

class SessionManager:
    """Manages user sessions in FastHTML"""
    
    def __init__(self):
        self.session_cookie_name = "nemesis_session"
        self.session_duration = 24 * 60 * 60  # 24 hours in seconds
    
    def get_session_from_request(self, request) -> Optional[AuthSession]:
        """Extract session from request cookies"""
        try:
            # Get session token from cookie
            if hasattr(request, 'cookies'):
                token = request.cookies.get(self.session_cookie_name)
                if token:
                    return validate_session(token)
            return None
        except Exception as e:
            print(f"Error getting session from request: {e}")
            return None
    
    def create_session_cookie(self, token: str, remember_me: bool = False) -> str:
        """Create session cookie string"""
        max_age = 30 * 24 * 60 * 60 if remember_me else self.session_duration  # 30 days or 24 hours
        
        return f"{self.session_cookie_name}={token}; Max-Age={max_age}; Path=/; HttpOnly; SameSite=Lax"
    
    def clear_session_cookie(self) -> str:
        """Create cookie string to clear session"""
        return f"{self.session_cookie_name}=; Max-Age=0; Path=/; HttpOnly"

# Global session manager
session_manager = SessionManager()

# =====================================================
# AUTHENTICATION MIDDLEWARE
# =====================================================

def auth_middleware():
    """FastHTML middleware for authentication"""
    
    def middleware(request, call_next):
        """Process request with authentication context"""
        try:
            # Get session from request
            session = session_manager.get_session_from_request(request)
            
            # Add session to request context
            request.session = session
            request.user = session if session else None
            request.is_authenticated = session is not None
            
            # Add helper functions to request
            request.has_role = lambda role: session and check_permission(session.role, role)
            request.is_admin = lambda: session and session.role == UserRole.ADMIN
            request.is_editor = lambda: session and check_permission(session.role, UserRole.EDITOR)
            request.is_author = lambda: session and check_permission(session.role, UserRole.AUTHOR)
            
            # Continue with request
            response = call_next(request)
            
            return response
            
        except Exception as e:
            print(f"Auth middleware error: {e}")
            # Continue without authentication on error
            request.session = None
            request.user = None
            request.is_authenticated = False
            return call_next(request)
    
    return middleware

# =====================================================
# ROUTE PROTECTION DECORATORS
# =====================================================

def require_auth(redirect_to: str = "/login"):
    """Decorator to require authentication for a route"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # In FastHTML, we'll need to check session differently
            # This is a placeholder for the actual implementation
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(required_role: UserRole, redirect_to: str = "/login"):
    """Decorator to require specific role for a route"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This will be implemented with FastHTML request context
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(redirect_to: str = "/login"):
    """Decorator to require admin role"""
    return require_role(UserRole.ADMIN, redirect_to)

def editor_required(redirect_to: str = "/login"):
    """Decorator to require editor role or higher"""
    return require_role(UserRole.EDITOR, redirect_to)

def author_required(redirect_to: str = "/login"):
    """Decorator to require author role or higher"""
    return require_role(UserRole.AUTHOR, redirect_to)

# =====================================================
# FASTHTML INTEGRATION HELPERS
# =====================================================

class AuthContext:
    """Authentication context for FastHTML routes"""
    
    def __init__(self, session: Optional[AuthSession] = None):
        self.session = session
        self.user = session
        self.is_authenticated = session is not None
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has required role"""
        return self.session and check_permission(self.session.role, role)
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.session and self.session.role == UserRole.ADMIN
    
    def is_editor(self) -> bool:
        """Check if user is editor or higher"""
        return self.session and check_permission(self.session.role, UserRole.EDITOR)
    
    def is_author(self) -> bool:
        """Check if user is author or higher"""
        return self.session and check_permission(self.session.role, UserRole.AUTHOR)
    
    def can_edit_post(self, post_author_id: str) -> bool:
        """Check if user can edit a specific post"""
        if not self.session:
            return False
        
        # Admins and editors can edit any post
        if self.is_admin() or self.is_editor():
            return True
        
        # Authors can edit their own posts
        if self.is_author() and self.session.user_id == post_author_id:
            return True
        
        return False
    
    def can_moderate_comments(self) -> bool:
        """Check if user can moderate comments"""
        return self.is_editor()
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users"""
        return self.is_admin()

def get_auth_context(request) -> AuthContext:
    """Get authentication context from request"""
    session = getattr(request, 'session', None)
    return AuthContext(session)

# =====================================================
# ROUTE HELPERS FOR FASTHTML
# =====================================================

def protected_route(required_role: Optional[UserRole] = None):
    """Helper for creating protected routes in FastHTML"""
    
    def check_access(session: Optional[AuthSession]) -> tuple[bool, str]:
        """Check if session has access"""
        if not session:
            return False, "Authentication required"
        
        if required_role and not check_permission(session.role, required_role):
            return False, f"Role {required_role.value} or higher required"
        
        return True, "Access granted"
    
    return check_access

def render_with_auth(template_func: Callable, **template_kwargs):
    """Render template with authentication context"""
    
    def renderer(request):
        """Render with auth context"""
        auth_ctx = get_auth_context(request)
        
        # Add auth context to template kwargs
        template_kwargs['auth'] = auth_ctx
        template_kwargs['user'] = auth_ctx.user
        template_kwargs['is_authenticated'] = auth_ctx.is_authenticated
        
        return template_func(**template_kwargs)
    
    return renderer

# =====================================================
# NAVIGATION HELPERS
# =====================================================

def get_user_navigation(auth_ctx: AuthContext) -> List[Dict[str, str]]:
    """Get navigation items based on user role"""
    nav_items = [
        {"name": "Home", "url": "/", "icon": "fa-home"},
        {"name": "Blog", "url": "/blog", "icon": "fa-newspaper"}
    ]
    
    if auth_ctx.is_authenticated:
        nav_items.extend([
            {"name": "Profile", "url": "/profile", "icon": "fa-user"},
        ])
        
        if auth_ctx.is_author():
            nav_items.append({"name": "My Posts", "url": "/my-posts", "icon": "fa-edit"})
        
        if auth_ctx.is_editor():
            nav_items.extend([
                {"name": "Manage Posts", "url": "/admin/posts", "icon": "fa-newspaper"},
                {"name": "Comments", "url": "/admin/comments", "icon": "fa-comments"}
            ])
        
        if auth_ctx.is_admin():
            nav_items.extend([
                {"name": "Users", "url": "/admin/users", "icon": "fa-users"},
                {"name": "Settings", "url": "/admin/settings", "icon": "fa-cog"}
            ])
        
        nav_items.append({"name": "Logout", "url": "/logout", "icon": "fa-sign-out"})
    else:
        nav_items.extend([
            {"name": "Login", "url": "/login", "icon": "fa-sign-in"},
            {"name": "Register", "url": "/register", "icon": "fa-user-plus"}
        ])
    
    return nav_items

def get_admin_sidebar(auth_ctx: AuthContext) -> List[Dict[str, Any]]:
    """Get admin sidebar items based on user role"""
    if not auth_ctx.is_authenticated:
        return []
    
    sidebar_items = []
    
    if auth_ctx.is_author():
        sidebar_items.append({
            "section": "Content",
            "items": [
                {"name": "New Post", "url": "/admin/posts/new", "icon": "fa-plus"},
                {"name": "My Posts", "url": "/admin/my-posts", "icon": "fa-edit"},
                {"name": "Drafts", "url": "/admin/drafts", "icon": "fa-file-text"}
            ]
        })
    
    if auth_ctx.is_editor():
        sidebar_items.extend([
            {
                "section": "Management",
                "items": [
                    {"name": "All Posts", "url": "/admin/posts", "icon": "fa-newspaper"},
                    {"name": "Comments", "url": "/admin/comments", "icon": "fa-comments"},
                    {"name": "Categories", "url": "/admin/categories", "icon": "fa-tags"},
                    {"name": "Media", "url": "/admin/media", "icon": "fa-image"}
                ]
            }
        ])
    
    if auth_ctx.is_admin():
        sidebar_items.extend([
            {
                "section": "Administration",
                "items": [
                    {"name": "Users", "url": "/admin/users", "icon": "fa-users"},
                    {"name": "Roles", "url": "/admin/roles", "icon": "fa-shield"},
                    {"name": "Settings", "url": "/admin/settings", "icon": "fa-cog"},
                    {"name": "Analytics", "url": "/admin/analytics", "icon": "fa-chart-bar"}
                ]
            }
        ])
    
    return sidebar_items

# =====================================================
# ERROR HANDLING
# =====================================================

def handle_auth_error(error_type: str, message: str = "") -> tuple:
    """Handle authentication errors"""
    error_responses = {
        "unauthenticated": (
            Title("Login Required - Nemesis Blog"),
            Div(cls="container mt-5")(
                Div(cls="alert alert-warning")(
                    H4("Authentication Required"),
                    P("Please log in to access this page."),
                    A(href="/login", cls="btn btn-primary")("Login"),
                    A(href="/register", cls="btn btn-secondary ml-2")("Register")
                )
            )
        ),
        "unauthorized": (
            Title("Access Denied - Nemesis Blog"),
            Div(cls="container mt-5")(
                Div(cls="alert alert-danger")(
                    H4("Access Denied"),
                    P(message or "You don't have permission to access this page."),
                    A(href="/", cls="btn btn-primary")("← Back to Home")
                )
            )
        ),
        "session_expired": (
            Title("Session Expired - Nemesis Blog"),
            Div(cls="container mt-5")(
                Div(cls="alert alert-info")(
                    H4("Session Expired"),
                    P("Your session has expired. Please log in again."),
                    A(href="/login", cls="btn btn-primary")("Login")
                )
            )
        )
    }
    
    return error_responses.get(error_type, error_responses["unauthenticated"])

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def is_safe_redirect_url(url: str) -> bool:
    """Check if redirect URL is safe (prevents open redirects)"""
    if not url:
        return False
    
    # Only allow relative URLs or URLs to the same domain
    if url.startswith('/') and not url.startswith('//'):
        return True
    
    # Add more sophisticated checks as needed
    return False

def get_redirect_url(request, default: str = "/") -> str:
    """Get safe redirect URL from request"""
    redirect_url = request.query_params.get('redirect', default)
    
    if is_safe_redirect_url(redirect_url):
        return redirect_url
    
    return default

# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    """
    Example usage in FastHTML routes:
    
    # Protected route
    @rt("/admin/dashboard")
    async def admin_dashboard(request):
        auth_ctx = get_auth_context(request)
        
        if not auth_ctx.is_admin():
            return handle_auth_error("unauthorized", "Admin access required")
        
        return render_admin_dashboard(auth_ctx)
    
    # Route with auth context
    @rt("/profile")
    async def user_profile(request):
        auth_ctx = get_auth_context(request)
        
        if not auth_ctx.is_authenticated:
            return handle_auth_error("unauthenticated")
        
        return render_profile(auth_ctx.user)
    """
    print("Authentication middleware loaded successfully!")
    print("Use get_auth_context(request) in your FastHTML routes for authentication.")