"""
Minimal Authentication System for Testing
Works without external dependencies
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

# =====================================================
# ENUMS AND MODELS (No Pydantic)
# =====================================================

class UserRole(str, Enum):
    """User roles with hierarchical permissions"""
    ADMIN = "admin"
    EDITOR = "editor"
    AUTHOR = "author"
    USER = "user"

class AuthSession:
    """Authentication session model"""
    def __init__(self, user_id: str, email: str, role: UserRole, 
                 display_name: str = None, avatar_url: str = None, 
                 expires_at: datetime = None, is_valid: bool = True):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.display_name = display_name
        self.avatar_url = avatar_url
        self.expires_at = expires_at or (datetime.utcnow() + timedelta(hours=24))
        self.is_valid = is_valid
    
    def dict(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "role": self.role.value,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_valid": self.is_valid
        }

class LoginRequest:
    """Login request model"""
    def __init__(self, email: str, password: str, remember_me: bool = False):
        self.email = email
        self.password = password
        self.remember_me = remember_me

class RegisterRequest:
    """Registration request model"""
    def __init__(self, email: str, password: str, confirm_password: str, 
                 display_name: str, terms_accepted: bool = True):
        self.email = email
        self.password = password
        self.confirm_password = confirm_password
        self.display_name = display_name
        self.terms_accepted = terms_accepted

class UserProfile:
    """User profile model"""
    def __init__(self, id: str, email: str, display_name: str = None, 
                 avatar_url: str = None, bio: str = None, website_url: str = None,
                 role: UserRole = UserRole.USER, is_active: bool = True,
                 email_verified: bool = False, created_at: datetime = None,
                 last_login: datetime = None):
        self.id = id
        self.email = email
        self.display_name = display_name
        self.avatar_url = avatar_url
        self.bio = bio
        self.website_url = website_url
        self.role = role
        self.is_active = is_active
        self.email_verified = email_verified
        self.created_at = created_at
        self.last_login = last_login
    
    def dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "website_url": self.website_url,
            "role": self.role.value,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

# =====================================================
# SIMPLE AUTHENTICATION SERVICE
# =====================================================

class AuthenticationService:
    """Minimal authentication service for testing"""
    
    def __init__(self):
        self.sessions = {}
        self.users = {}
    
    async def register_user(self, registration: RegisterRequest) -> Dict[str, Any]:
        """Register a new user"""
        try:
            if registration.password != registration.confirm_password:
                return {"success": False, "message": "Passwords do not match"}
            
            if registration.email in self.users:
                return {"success": False, "message": "Email already registered"}
            
            user_id = f"user_{len(self.users) + 1}"
            self.users[registration.email] = {
                "id": user_id,
                "email": registration.email,
                "password": registration.password,  # In production, hash this!
                "display_name": registration.display_name,
                "role": UserRole.USER.value,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            
            return {
                "success": True,
                "message": "Registration successful",
                "user_id": user_id
            }
        except Exception as e:
            return {"success": False, "message": f"Registration failed: {str(e)}"}
    
    async def login_user(self, login: LoginRequest) -> Dict[str, Any]:
        """Authenticate user"""
        try:
            if login.email not in self.users:
                return {"success": False, "message": "Invalid email or password"}
            
            user = self.users[login.email]
            if user["password"] != login.password:
                return {"success": False, "message": "Invalid email or password"}
            
            # Create session
            session = AuthSession(
                user_id=user["id"],
                email=user["email"],
                role=UserRole(user["role"]),
                display_name=user["display_name"]
            )
            
            token = f"token_{user['id']}_{datetime.utcnow().timestamp()}"
            self.sessions[token] = session
            
            return {
                "success": True,
                "message": "Login successful",
                "token": token,
                "session": session.dict()
            }
        except Exception as e:
            return {"success": False, "message": f"Login failed: {str(e)}"}
    
    def validate_session_token(self, token: str) -> Optional[AuthSession]:
        """Validate session token"""
        return self.sessions.get(token)
    
    def check_permission(self, user_role: UserRole, required_role: UserRole) -> bool:
        """Check permissions"""
        role_hierarchy = {
            UserRole.USER: 1,
            UserRole.AUTHOR: 2,
            UserRole.EDITOR: 3,
            UserRole.ADMIN: 4
        }
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

# Global service instance
auth_service = AuthenticationService()

# Convenience functions
async def register_user(email: str, password: str, confirm_password: str, display_name: str):
    registration = RegisterRequest(email, password, confirm_password, display_name)
    return await auth_service.register_user(registration)

async def login_user(email: str, password: str, remember_me: bool = False):
    login_request = LoginRequest(email, password, remember_me)
    return await auth_service.login_user(login_request)

def validate_session(token: str) -> Optional[AuthSession]:
    return auth_service.validate_session_token(token)

def check_permission(user_role: UserRole, required_role: UserRole) -> bool:
    return auth_service.check_permission(user_role, required_role)

if __name__ == "__main__":
    print("✅ Minimal authentication system loaded!")
    print("📋 Available: UserRole, AuthSession, LoginRequest, RegisterRequest, UserProfile")
    print("🔧 No external dependencies required")