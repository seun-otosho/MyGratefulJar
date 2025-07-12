"""
Authentication System for Nemesis Blog Platform
Integrates Supabase Auth with FastHTML for user management and role-based access control
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
import jwt
from dotenv import load_dotenv
from supabase import create_client, Client
from pydantic import BaseModel, EmailStr

# Load environment variables
load_dotenv()

# =====================================================
# CONFIGURATION
# =====================================================

class AuthConfig:
    """Authentication configuration"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.jwt_secret = os.getenv("JWT_SECRET", "your-jwt-secret-key")
        self.session_timeout = int(os.getenv("SESSION_TIMEOUT", "86400"))  # 24 hours
        
        if not self.supabase_url or not self.supabase_anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
    
    def get_client(self, use_service_key: bool = False) -> Client:
        """Get Supabase client instance"""
        key = self.supabase_service_key if use_service_key else self.supabase_anon_key
        return create_client(self.supabase_url, key)

# Global auth config instance
auth_config = AuthConfig()

# =====================================================
# ENUMS AND MODELS
# =====================================================

class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    AUTHOR = "author"
    USER = "user"

class AuthStatus(str, Enum):
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    EMAIL_NOT_VERIFIED = "email_not_verified"
    ACCOUNT_DISABLED = "account_disabled"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"

class UserSession(BaseModel):
    """User session model"""
    user_id: str
    email: str
    display_name: Optional[str] = None
    role: UserRole = UserRole.USER
    avatar_url: Optional[str] = None
    is_verified: bool = False
    expires_at: datetime
    access_token: str
    refresh_token: Optional[str] = None

class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str
    remember_me: bool = False

class RegisterRequest(BaseModel):
    """Registration request model"""
    email: EmailStr
    password: str
    display_name: str
    confirm_password: str

class AuthResult(BaseModel):
    """Authentication result model"""
    status: AuthStatus
    message: str
    user_session: Optional[UserSession] = None
    redirect_url: Optional[str] = None

# =====================================================
# AUTHENTICATION SERVICE
# =====================================================

class AuthService:
    """Main authentication service"""
    
    def __init__(self):
        self.config = auth_config
        self.client = self.config.get_client()
        self.admin_client = self.config.get_client(use_service_key=True)
    
    # =====================================================
    # USER REGISTRATION
    # =====================================================
    
    async def register_user(self, request: RegisterRequest) -> AuthResult:
        """Register a new user"""
        try:
            # Validate password confirmation
            if request.password != request.confirm_password:
                return AuthResult(
                    status=AuthStatus.ERROR,
                    message="Passwords do not match"
                )
            
            # Validate password strength
            if not self._validate_password_strength(request.password):
                return AuthResult(
                    status=AuthStatus.ERROR,
                    message="Password must be at least 8 characters with uppercase, lowercase, and number"
                )
            
            # Register with Supabase Auth
            auth_response = self.client.auth.sign_up({
                "email": request.email,
                "password": request.password,
                "options": {
                    "data": {
                        "display_name": request.display_name
                    }
                }
            })
            
            if auth_response.user:
                # Create user record in our database
                await self._create_user_record(
                    auth_response.user.id,
                    request.email,
                    request.display_name
                )
                
                return AuthResult(
                    status=AuthStatus.SUCCESS,
                    message="Registration successful! Please check your email to verify your account.",
                    redirect_url="/login?message=verify_email"
                )
            else:
                return AuthResult(
                    status=AuthStatus.ERROR,
                    message="Registration failed. Please try again."
                )
                
        except Exception as e:
            print(f"Registration error: {e}")
            return AuthResult(
                status=AuthStatus.ERROR,
                message="Registration failed. Email may already be in use."
            )
    
    # =====================================================
    # USER LOGIN
    # =====================================================
    
    async def login_user(self, request: LoginRequest) -> AuthResult:
        """Authenticate user login"""
        try:
            # Attempt login with Supabase Auth
            auth_response = self.client.auth.sign_in_with_password({
                "email": request.email,
                "password": request.password
            })
            
            if auth_response.user and auth_response.session:
                # Check if email is verified
                if not auth_response.user.email_confirmed_at:
                    return AuthResult(
                        status=AuthStatus.EMAIL_NOT_VERIFIED,
                        message="Please verify your email address before logging in."
                    )
                
                # Get user details from our database
                user_details = await self._get_user_details(auth_response.user.id)
                
                # Check if account is active
                if not user_details.get("is_active", True):
                    return AuthResult(
                        status=AuthStatus.ACCOUNT_DISABLED,
                        message="Your account has been disabled. Please contact support."
                    )
                
                # Create user session
                session_duration = timedelta(days=30) if request.remember_me else timedelta(hours=24)
                user_session = UserSession(
                    user_id=auth_response.user.id,
                    email=auth_response.user.email,
                    display_name=user_details.get("display_name"),
                    role=UserRole(user_details.get("role", "user")),
                    avatar_url=user_details.get("avatar_url"),
                    is_verified=bool(auth_response.user.email_confirmed_at),
                    expires_at=datetime.utcnow() + session_duration,
                    access_token=auth_response.session.access_token,
                    refresh_token=auth_response.session.refresh_token
                )
                
                # Update last login time
                await self._update_last_login(auth_response.user.id)
                
                return AuthResult(
                    status=AuthStatus.SUCCESS,
                    message="Login successful!",
                    user_session=user_session,
                    redirect_url="/admin" if user_session.role in [UserRole.ADMIN, UserRole.EDITOR] else "/"
                )
            else:
                return AuthResult(
                    status=AuthStatus.INVALID_CREDENTIALS,
                    message="Invalid email or password."
                )
                
        except Exception as e:
            print(f"Login error: {e}")
            return AuthResult(
                status=AuthStatus.ERROR,
                message="Login failed. Please try again."
            )
    
    # =====================================================
    # SESSION MANAGEMENT
    # =====================================================
    
    async def validate_session(self, access_token: str) -> Optional[UserSession]:
        """Validate and refresh user session"""
        try:
            # Verify token with Supabase
            user_response = self.client.auth.get_user(access_token)
            
            if user_response.user:
                # Get user details from database
                user_details = await self._get_user_details(user_response.user.id)
                
                # Create session object
                user_session = UserSession(
                    user_id=user_response.user.id,
                    email=user_response.user.email,
                    display_name=user_details.get("display_name"),
                    role=UserRole(user_details.get("role", "user")),
                    avatar_url=user_details.get("avatar_url"),
                    is_verified=bool(user_response.user.email_confirmed_at),
                    expires_at=datetime.utcnow() + timedelta(hours=24),
                    access_token=access_token
                )
                
                return user_session
            
        except Exception as e:
            print(f"Session validation error: {e}")
        
        return None
    
    async def refresh_session(self, refresh_token: str) -> Optional[UserSession]:
        """Refresh user session with refresh token"""
        try:
            auth_response = self.client.auth.refresh_session(refresh_token)
            
            if auth_response.session and auth_response.user:
                user_details = await self._get_user_details(auth_response.user.id)
                
                user_session = UserSession(
                    user_id=auth_response.user.id,
                    email=auth_response.user.email,
                    display_name=user_details.get("display_name"),
                    role=UserRole(user_details.get("role", "user")),
                    avatar_url=user_details.get("avatar_url"),
                    is_verified=bool(auth_response.user.email_confirmed_at),
                    expires_at=datetime.utcnow() + timedelta(hours=24),
                    access_token=auth_response.session.access_token,
                    refresh_token=auth_response.session.refresh_token
                )
                
                return user_session
                
        except Exception as e:
            print(f"Session refresh error: {e}")
        
        return None
    
    async def logout_user(self, access_token: str) -> bool:
        """Logout user and invalidate session"""
        try:
            self.client.auth.sign_out()
            return True
        except Exception as e:
            print(f"Logout error: {e}")
            return False
    
    # =====================================================
    # USER MANAGEMENT
    # =====================================================
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            response = self.admin_client.from_("users").select("*").eq("id", user_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile information"""
        try:
            # Update in our database
            response = self.admin_client.from_("users").update(updates).eq("id", user_id).execute()
            
            # Update in Supabase Auth if email or metadata changed
            if "email" in updates or "display_name" in updates:
                auth_updates = {}
                if "email" in updates:
                    auth_updates["email"] = updates["email"]
                if "display_name" in updates:
                    auth_updates["data"] = {"display_name": updates["display_name"]}
                
                if auth_updates:
                    self.admin_client.auth.admin.update_user_by_id(user_id, auth_updates)
            
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    async def change_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """Change user role (admin only)"""
        try:
            response = self.admin_client.from_("users").update({"role": new_role.value}).eq("id", user_id).execute()
            return True
        except Exception as e:
            print(f"Error changing user role: {e}")
            return False
    
    # =====================================================
    # PASSWORD MANAGEMENT
    # =====================================================
    
    async def request_password_reset(self, email: str) -> bool:
        """Request password reset email"""
        try:
            self.client.auth.reset_password_email(email)
            return True
        except Exception as e:
            print(f"Password reset request error: {e}")
            return False
    
    async def update_password(self, access_token: str, new_password: str) -> bool:
        """Update user password"""
        try:
            if not self._validate_password_strength(new_password):
                return False
            
            self.client.auth.update_user(access_token, {"password": new_password})
            return True
        except Exception as e:
            print(f"Password update error: {e}")
            return False
    
    # =====================================================
    # ROLE-BASED ACCESS CONTROL
    # =====================================================
    
    def check_permission(self, user_session: UserSession, required_role: UserRole) -> bool:
        """Check if user has required role permission"""
        role_hierarchy = {
            UserRole.USER: 0,
            UserRole.AUTHOR: 1,
            UserRole.EDITOR: 2,
            UserRole.ADMIN: 3
        }
        
        user_level = role_hierarchy.get(user_session.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def can_edit_post(self, user_session: UserSession, post_author_id: str) -> bool:
        """Check if user can edit a specific post"""
        # Admins and editors can edit any post
        if user_session.role in [UserRole.ADMIN, UserRole.EDITOR]:
            return True
        
        # Authors can edit their own posts
        if user_session.role == UserRole.AUTHOR and user_session.user_id == post_author_id:
            return True
        
        return False
    
    def can_moderate_comments(self, user_session: UserSession) -> bool:
        """Check if user can moderate comments"""
        return user_session.role in [UserRole.ADMIN, UserRole.EDITOR]
    
    # =====================================================
    # HELPER METHODS
    # =====================================================
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_upper and has_lower and has_digit
    
    async def _create_user_record(self, user_id: str, email: str, display_name: str) -> bool:
        """Create user record in our database"""
        try:
            user_data = {
                "id": user_id,
                "email": email,
                "display_name": display_name,
                "role": UserRole.USER.value,
                "is_active": True,
                "email_verified": False
            }
            
            response = self.admin_client.from_("users").insert(user_data).execute()
            return True
        except Exception as e:
            print(f"Error creating user record: {e}")
            return False
    
    async def _get_user_details(self, user_id: str) -> Dict[str, Any]:
        """Get user details from database"""
        try:
            response = self.admin_client.from_("users").select("*").eq("id", user_id).single().execute()
            return response.data if response.data else {}
        except Exception as e:
            print(f"Error getting user details: {e}")
            return {}
    
    async def _update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            response = self.admin_client.from_("users").update({
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating last login: {e}")
            return False

# =====================================================
# GLOBAL AUTH SERVICE INSTANCE
# =====================================================

# Create global auth service instance
auth_service = AuthService()

# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

async def register_user(email: str, password: str, display_name: str, confirm_password: str) -> AuthResult:
    """Convenience function for user registration"""
    request = RegisterRequest(
        email=email,
        password=password,
        display_name=display_name,
        confirm_password=confirm_password
    )
    return await auth_service.register_user(request)

async def login_user(email: str, password: str, remember_me: bool = False) -> AuthResult:
    """Convenience function for user login"""
    request = LoginRequest(
        email=email,
        password=password,
        remember_me=remember_me
    )
    return await auth_service.login_user(request)

async def validate_session(access_token: str) -> Optional[UserSession]:
    """Convenience function for session validation"""
    return await auth_service.validate_session(access_token)

async def logout_user(access_token: str) -> bool:
    """Convenience function for user logout"""
    return await auth_service.logout_user(access_token)

def check_permission(user_session: UserSession, required_role: UserRole) -> bool:
    """Convenience function for permission checking"""
    return auth_service.check_permission(user_session, required_role)

# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    """
    Example usage of the authentication system:
    
    # User registration
    result = await register_user(
        email="user@example.com",
        password="SecurePass123",
        display_name="John Doe",
        confirm_password="SecurePass123"
    )
    
    # User login
    result = await login_user(
        email="user@example.com",
        password="SecurePass123",
        remember_me=True
    )
    
    if result.status == AuthStatus.SUCCESS:
        user_session = result.user_session
        
        # Check permissions
        can_admin = check_permission(user_session, UserRole.ADMIN)
        can_edit = auth_service.can_edit_post(user_session, "post_author_id")
    
    # Session validation
    session = await validate_session("access_token")
    if session:
        print(f"User {session.display_name} is authenticated")
    """
    print("Authentication system loaded successfully!")
    print("Set SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_SERVICE_ROLE_KEY environment variables to use.")