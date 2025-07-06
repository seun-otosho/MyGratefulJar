"""
Authentication Routes for FastHTML Nemesis Blog
Handles login, register, logout, profile, and password reset routes
"""

from fasthtml.common import *
from typing import Optional, Dict, Any
import asyncio

# Import our auth system and middleware
from auth_system import (
    auth_service,
    register_user,
    login_user,
    get_user_profile,
    UserRole,
    AuthSession
)
from middleware import (
    session_manager,
    get_auth_context,
    handle_auth_error,
    get_redirect_url,
    AuthContext
)

# =====================================================
# AUTHENTICATION UI COMPONENTS
# =====================================================

def auth_layout(title: str, content, show_navbar: bool = True):
    """Layout for authentication pages"""
    return (
        Title(f"{title} - Nemesis Blog"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Link(href="./css/bootstrap.min.css", rel="stylesheet"),
        Link(href="./css/style.css", rel="stylesheet"),
        Link(href="https://fonts.googleapis.com/css?family=Montserrat:900%7CNunito:400,700%7COswald%7CRoboto", rel="stylesheet"),
        Div(cls="auth-page")(
            navbar() if show_navbar else Div(),
            Div(cls="container mt-5")(
                Div(cls="row justify-content-center")(
                    Div(cls="col-md-6 col-lg-5")(
                        content
                    )
                )
            )
        )
    )

def navbar():
    """Simple navbar for auth pages"""
    return Nav(cls="navbar navbar-expand-lg navbar-light bg-light")(
        Div(cls="container")(
            A(cls="navbar-brand", href="/")(
                Img(src="./images/logo_nemesis.png", height="40", alt="Nemesis")
            ),
            Ul(cls="navbar-nav ml-auto")(
                Li(cls="nav-item")(A(cls="nav-link", href="/")("Home")),
                Li(cls="nav-item")(A(cls="nav-link", href="/blog")("Blog")),
                Li(cls="nav-item")(A(cls="nav-link", href="/contact")("Contact"))
            )
        )
    )

def login_form(error_message: str = "", redirect_url: str = ""):
    """Login form component"""
    return Div(cls="card shadow")(
        Div(cls="card-header text-center")(
            H3("Login to Your Account"),
            P(cls="text-muted")("Welcome back! Please sign in to continue.")
        ),
        Div(cls="card-body")(
            # Error message
            Div(cls="alert alert-danger", style="display: none;" if not error_message else "")(
                error_message
            ) if error_message else "",
            
            # Login form
            Form(method="POST", action="/login")(
                Input(type="hidden", name="redirect", value=redirect_url),
                
                Div(cls="form-group mb-3")(
                    Label(**{"for": "email"})("Email Address"),
                    Input(
                        type="email", 
                        cls="form-control", 
                        id="email", 
                        name="email", 
                        placeholder="Enter your email",
                        required=True
                    )
                ),
                
                Div(cls="form-group mb-3")(
                    Label(**{"for": "password"})("Password"),
                    Input(
                        type="password", 
                        cls="form-control", 
                        id="password", 
                        name="password", 
                        placeholder="Enter your password",
                        required=True
                    )
                ),
                
                Div(cls="form-group mb-3")(
                    Div(cls="form-check")(
                        Input(type="checkbox", cls="form-check-input", id="remember_me", name="remember_me"),
                        Label(cls="form-check-label", **{"for": "remember_me"})("Remember me")
                    )
                ),
                
                Button(type="submit", cls="btn btn-primary btn-block w-100")(
                    I(cls="fa fa-sign-in mr-2"),
                    "Sign In"
                ),
                
                Hr(),
                
                Div(cls="text-center")(
                    A(href="/forgot-password", cls="text-muted")("Forgot your password?")
                )
            )
        ),
        Div(cls="card-footer text-center")(
            P(cls="mb-0")(
                "Don't have an account? ",
                A(href=f"/register?redirect={redirect_url}")("Sign up here")
            )
        )
    )

def register_form(error_message: str = "", redirect_url: str = ""):
    """Registration form component"""
    return Div(cls="card shadow")(
        Div(cls="card-header text-center")(
            H3("Create Your Account"),
            P(cls="text-muted")("Join our community and start blogging!")
        ),
        Div(cls="card-body")(
            # Error message
            Div(cls="alert alert-danger", style="display: none;" if not error_message else "")(
                error_message
            ) if error_message else "",
            
            # Registration form
            Form(method="POST", action="/register")(
                Input(type="hidden", name="redirect", value=redirect_url),
                
                Div(cls="form-group mb-3")(
                    Label(**{"for": "display_name"})("Display Name"),
                    Input(
                        type="text", 
                        cls="form-control", 
                        id="display_name", 
                        name="display_name", 
                        placeholder="Your display name",
                        required=True
                    )
                ),
                
                Div(cls="form-group mb-3")(
                    Label(**{"for": "email"})("Email Address"),
                    Input(
                        type="email", 
                        cls="form-control", 
                        id="email", 
                        name="email", 
                        placeholder="Enter your email",
                        required=True
                    )
                ),
                
                Div(cls="form-group mb-3")(
                    Label(**{"for": "password"})("Password"),
                    Input(
                        type="password", 
                        cls="form-control", 
                        id="password", 
                        name="password", 
                        placeholder="Create a strong password",
                        required=True
                    ),
                    Small(cls="form-text text-muted")(
                        "Password must be at least 8 characters with uppercase, lowercase, and number."
                    )
                ),
                
                Div(cls="form-group mb-3")(
                    Label(**{"for": "confirm_password"})("Confirm Password"),
                    Input(
                        type="password", 
                        cls="form-control", 
                        id="confirm_password", 
                        name="confirm_password", 
                        placeholder="Confirm your password",
                        required=True
                    )
                ),
                
                Div(cls="form-group mb-3")(
                    Div(cls="form-check")(
                        Input(type="checkbox", cls="form-check-input", id="terms", name="terms", required=True),
                        Label(cls="form-check-label", **{"for": "terms"})(
                            "I agree to the ",
                            A(href="/terms", target="_blank")("Terms of Service"),
                            " and ",
                            A(href="/privacy", target="_blank")("Privacy Policy")
                        )
                    )
                ),
                
                Button(type="submit", cls="btn btn-success btn-block w-100")(
                    I(cls="fa fa-user-plus mr-2"),
                    "Create Account"
                )
            )
        ),
        Div(cls="card-footer text-center")(
            P(cls="mb-0")(
                "Already have an account? ",
                A(href=f"/login?redirect={redirect_url}")("Sign in here")
            )
        )
    )

def profile_form(user_profile, success_message: str = "", error_message: str = ""):
    """User profile editing form"""
    return Div(cls="card shadow")(
        Div(cls="card-header")(
            H3("Edit Profile"),
            P(cls="text-muted")("Update your profile information")
        ),
        Div(cls="card-body")(
            # Success message
            Div(cls="alert alert-success", style="display: none;" if not success_message else "")(
                success_message
            ) if success_message else "",
            
            # Error message
            Div(cls="alert alert-danger", style="display: none;" if not error_message else "")(
                error_message
            ) if error_message else "",
            
            Form(method="POST", action="/profile")(
                Div(cls="row")(
                    Div(cls="col-md-6")(
                        Div(cls="form-group mb-3")(
                            Label(**{"for": "display_name"})("Display Name"),
                            Input(
                                type="text", 
                                cls="form-control", 
                                id="display_name", 
                                name="display_name", 
                                value=user_profile.display_name or "",
                                required=True
                            )
                        )
                    ),
                    Div(cls="col-md-6")(
                        Div(cls="form-group mb-3")(
                            Label(**{"for": "email"})("Email Address"),
                            Input(
                                type="email", 
                                cls="form-control", 
                                id="email", 
                                value=user_profile.email,
                                disabled=True
                            ),
                            Small(cls="form-text text-muted")("Email cannot be changed")
                        )
                    )
                ),
                
                Div(cls="form-group mb-3")(
                    Label(**{"for": "bio"})("Bio"),
                    Textarea(
                        cls="form-control", 
                        id="bio", 
                        name="bio", 
                        rows="3",
                        placeholder="Tell us about yourself..."
                    )(user_profile.bio or "")
                ),
                
                Div(cls="form-group mb-3")(
                    Label(**{"for": "website_url"})("Website"),
                    Input(
                        type="url", 
                        cls="form-control", 
                        id="website_url", 
                        name="website_url", 
                        value=user_profile.website_url or "",
                        placeholder="https://yourwebsite.com"
                    )
                ),
                
                Div(cls="form-group mb-3")(
                    Label(**{"for": "avatar_url"})("Avatar URL"),
                    Input(
                        type="url", 
                        cls="form-control", 
                        id="avatar_url", 
                        name="avatar_url", 
                        value=user_profile.avatar_url or "",
                        placeholder="https://example.com/avatar.jpg"
                    )
                ),
                
                Hr(),
                
                Div(cls="row")(
                    Div(cls="col-md-6")(
                        Button(type="submit", cls="btn btn-primary")(
                            I(cls="fa fa-save mr-2"),
                            "Update Profile"
                        )
                    ),
                    Div(cls="col-md-6 text-right")(
                        A(href="/change-password", cls="btn btn-outline-secondary")(
                            I(cls="fa fa-key mr-2"),
                            "Change Password"
                        )
                    )
                )
            )
        )
    )

def forgot_password_form(success_message: str = "", error_message: str = ""):
    """Forgot password form"""
    return Div(cls="card shadow")(
        Div(cls="card-header text-center")(
            H3("Reset Password"),
            P(cls="text-muted")("Enter your email to receive reset instructions")
        ),
        Div(cls="card-body")(
            # Success message
            Div(cls="alert alert-success", style="display: none;" if not success_message else "")(
                success_message
            ) if success_message else "",
            
            # Error message
            Div(cls="alert alert-danger", style="display: none;" if not error_message else "")(
                error_message
            ) if error_message else "",
            
            Form(method="POST", action="/forgot-password")(
                Div(cls="form-group mb-3")(
                    Label(**{"for": "email"})("Email Address"),
                    Input(
                        type="email", 
                        cls="form-control", 
                        id="email", 
                        name="email", 
                        placeholder="Enter your email address",
                        required=True
                    )
                ),
                
                Button(type="submit", cls="btn btn-primary btn-block w-100")(
                    I(cls="fa fa-envelope mr-2"),
                    "Send Reset Instructions"
                )
            )
        ),
        Div(cls="card-footer text-center")(
            A(href="/login")("← Back to Login")
        )
    )

# =====================================================
# AUTHENTICATION ROUTES
# =====================================================

def create_auth_routes(app, rt):
    """Create all authentication routes"""
    
    @rt("/login")
    async def login_page(request):
        """Login page"""
        # Check if already authenticated
        auth_ctx = get_auth_context(request)
        if auth_ctx.is_authenticated:
            redirect_url = get_redirect_url(request, "/")
            return RedirectResponse(redirect_url)
        
        redirect_url = request.query_params.get('redirect', '')
        
        return auth_layout(
            "Login",
            login_form(redirect_url=redirect_url)
        )
    
    @rt("/login", methods=["POST"])
    async def login_submit(request):
        """Handle login form submission"""
        try:
            form_data = await request.form()
            email = form_data.get('email', '').strip()
            password = form_data.get('password', '')
            remember_me = form_data.get('remember_me') == 'on'
            redirect_url = form_data.get('redirect', '/')
            
            # Validate input
            if not email or not password:
                return auth_layout(
                    "Login",
                    login_form("Please enter both email and password", redirect_url)
                )
            
            # Attempt login
            result = await login_user(email, password, remember_me)
            
            if result['success']:
                # Create session cookie
                token = result['token']
                cookie = session_manager.create_session_cookie(token, remember_me)
                
                # Redirect with cookie
                response = RedirectResponse(get_redirect_url(request, redirect_url))
                response.headers['Set-Cookie'] = cookie
                return response
            else:
                return auth_layout(
                    "Login",
                    login_form(result['message'], redirect_url)
                )
                
        except Exception as e:
            return auth_layout(
                "Login",
                login_form(f"Login failed: {str(e)}", redirect_url)
            )
    
    @rt("/register")
    async def register_page(request):
        """Registration page"""
        # Check if already authenticated
        auth_ctx = get_auth_context(request)
        if auth_ctx.is_authenticated:
            redirect_url = get_redirect_url(request, "/")
            return RedirectResponse(redirect_url)
        
        redirect_url = request.query_params.get('redirect', '')
        
        return auth_layout(
            "Register",
            register_form(redirect_url=redirect_url)
        )
    
    @rt("/register", methods=["POST"])
    async def register_submit(request):
        """Handle registration form submission"""
        try:
            form_data = await request.form()
            email = form_data.get('email', '').strip()
            password = form_data.get('password', '')
            confirm_password = form_data.get('confirm_password', '')
            display_name = form_data.get('display_name', '').strip()
            terms = form_data.get('terms') == 'on'
            redirect_url = form_data.get('redirect', '/')
            
            # Validate input
            if not all([email, password, confirm_password, display_name]):
                return auth_layout(
                    "Register",
                    register_form("Please fill in all required fields", redirect_url)
                )
            
            if not terms:
                return auth_layout(
                    "Register",
                    register_form("Please accept the terms of service", redirect_url)
                )
            
            # Attempt registration
            result = await register_user(email, password, confirm_password, display_name)
            
            if result['success']:
                # Show success message
                return auth_layout(
                    "Registration Successful",
                    Div(cls="card shadow")(
                        Div(cls="card-body text-center")(
                            I(cls="fa fa-check-circle text-success", style="font-size: 3rem;"),
                            H3(cls="mt-3")("Registration Successful!"),
                            P("Please check your email for verification instructions."),
                            P("Once verified, you can log in to your account."),
                            A(href="/login", cls="btn btn-primary")("Go to Login")
                        )
                    )
                )
            else:
                return auth_layout(
                    "Register",
                    register_form(result['message'], redirect_url)
                )
                
        except Exception as e:
            return auth_layout(
                "Register",
                register_form(f"Registration failed: {str(e)}", redirect_url)
            )
    
    @rt("/logout")
    async def logout(request):
        """Logout user"""
        # Clear session cookie
        cookie = session_manager.clear_session_cookie()
        
        response = RedirectResponse("/")
        response.headers['Set-Cookie'] = cookie
        return response
    
    @rt("/profile")
    async def profile_page(request):
        """User profile page"""
        auth_ctx = get_auth_context(request)
        
        if not auth_ctx.is_authenticated:
            return handle_auth_error("unauthenticated")
        
        user_profile = await get_user_profile(auth_ctx.session.user_id)
        
        return auth_layout(
            "Profile",
            profile_form(user_profile),
            show_navbar=True
        )
    
    @rt("/profile", methods=["POST"])
    async def profile_update(request):
        """Handle profile update"""
        auth_ctx = get_auth_context(request)
        
        if not auth_ctx.is_authenticated:
            return handle_auth_error("unauthenticated")
        
        try:
            form_data = await request.form()
            
            updates = {
                'display_name': form_data.get('display_name', '').strip(),
                'bio': form_data.get('bio', '').strip(),
                'website_url': form_data.get('website_url', '').strip(),
                'avatar_url': form_data.get('avatar_url', '').strip()
            }
            
            # Remove empty values
            updates = {k: v for k, v in updates.items() if v}
            
            success = await auth_service.update_user_profile(auth_ctx.session.user_id, updates)
            
            user_profile = await get_user_profile(auth_ctx.session.user_id)
            
            if success:
                return auth_layout(
                    "Profile",
                    profile_form(user_profile, "Profile updated successfully!"),
                    show_navbar=True
                )
            else:
                return auth_layout(
                    "Profile",
                    profile_form(user_profile, "", "Failed to update profile"),
                    show_navbar=True
                )
                
        except Exception as e:
            user_profile = await get_user_profile(auth_ctx.session.user_id)
            return auth_layout(
                "Profile",
                profile_form(user_profile, "", f"Update failed: {str(e)}"),
                show_navbar=True
            )
    
    @rt("/forgot-password")
    async def forgot_password_page(request):
        """Forgot password page"""
        return auth_layout(
            "Reset Password",
            forgot_password_form()
        )
    
    @rt("/forgot-password", methods=["POST"])
    async def forgot_password_submit(request):
        """Handle forgot password submission"""
        try:
            form_data = await request.form()
            email = form_data.get('email', '').strip()
            
            if not email:
                return auth_layout(
                    "Reset Password",
                    forgot_password_form("", "Please enter your email address")
                )
            
            result = await auth_service.request_password_reset(email)
            
            if result['success']:
                return auth_layout(
                    "Reset Password",
                    forgot_password_form(result['message'])
                )
            else:
                return auth_layout(
                    "Reset Password",
                    forgot_password_form("", result['message'])
                )
                
        except Exception as e:
            return auth_layout(
                "Reset Password",
                forgot_password_form("", f"Reset failed: {str(e)}")
            )

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def add_auth_routes_to_app(app, rt):
    """Add all authentication routes to FastHTML app"""
    create_auth_routes(app, rt)
    print("✅ Authentication routes added to FastHTML app")

# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    """
    Example usage:
    
    from fasthtml.common import *
    from auth_routes import add_auth_routes_to_app
    
    app, rt = fast_app()
    
    # Add authentication routes
    add_auth_routes_to_app(app, rt)
    
    serve()
    """
    print("Authentication routes module loaded successfully!")
    print("Use add_auth_routes_to_app(app, rt) to add routes to your FastHTML app.")