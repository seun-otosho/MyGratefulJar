"""
Authentication System for Nemesis Blog Platform
Fixed version with all required classes and proper dependency handling
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, EmailStr

# Try to import optional dependencies
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("Warning: PyJWT not installed. JWT functionality disabled.")

try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("Warning: python-dotenv not installed. Using environment variables directly.")

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: supabase not installed. Database functionality disabled.")

# =====================================================
# ENUMS AND MODELS
# =====================================================

class UserRole(str, Enum):
    """User roles with hierarchical permissions"""
    ADMIN = "admin"          # Full system access
    EDITOR = "editor"        # Content management
    AUTHOR = "author"        # Create and edit own posts
    USER = "user"           # Comment and interact

class AuthStatus(str, Enum):
    """Authentication status"""
    AUTHENTICATED = "authenticated"
    UNAUTHENTICATED = "unauthenticated"
    EXPIRED = "expired"
    INVALID = "invalid"

class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str
    remember_me: bool = False

class RegisterRequest(BaseModel):
    """Registration request model"""
    email: EmailStr
    password: str
    confirm_password: str
    display_name: str
    terms_accepted: bool = True
    
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self
    
    def validate_password_strength(self):
        if len(self.password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in self.password):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in self.password):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in self.password):
            raise ValueError('Password must contain at least one number')
        return self

class UserProfile(BaseModel):
    """User profile model"""
    id: str
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website_url: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    email_verified: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

class AuthSession(BaseModel):
    """Authentication session model"""
    user_id: str
    email: str
    role: UserRole
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    expires_at: datetime
    is_valid: bool = True

# =====================================================
# CONFIGURATION
# =====================================================

class AuthConfig:
    """Authentication configuration"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        self.jwt_secret = os.getenv("JWT_SECRET", "your-jwt-secret-change-in-production")
        self.session_duration = int(os.getenv("SESSION_DURATION_HOURS", "24"))
        
        if not all([self.supabase_url, self.supabase_anon_key]) and SUPABASE_AVAILABLE:
            print("Warning: SUPABASE_URL and SUPABASE_ANON_KEY not set")
    
    def get_client(self, use_service_key: bool = False):
        """Get Supabase client instance"""
        if not SUPABASE_AVAILABLE:
            raise ImportError("Supabase client not available. Install with: pip install supabase")
        
        key = self.supabase_service_key if use_service_key and self.supabase_service_key else self.supabase_anon_key
        return create_client(self.supabase_url, key)

# Global auth config
auth_config = AuthConfig()

# =====================================================
# AUTHENTICATION SERVICE
# =====================================================

class AuthenticationService:
    """Main authentication service class"""
    
    def __init__(self):
        self.config = auth_config
        if SUPABASE_AVAILABLE and self.config.supabase_url and self.config.supabase_anon_key:
            self.client = self.config.get_client()
            self.admin_client = self.config.get_client(use_service_key=True)
        else:
            self.client = None
            self.admin_client = None
            print("Warning: Supabase clients not initialized")
    
    # =====================================================
    # USER REGISTRATION
    # =====================================================
    
    async def register_user(self, registration: RegisterRequest) -> Dict[str, Any]:
        """Register a new user with email verification"""
        try:
            if not self.client:
                return {"success": False, "message": "Database not available", "error": "No client"}
            
            # Validate passwords
            registration.validate_passwords_match()
            registration.validate_password_strength()
            
            # Register with Supabase Auth
            auth_response = self.client.auth.sign_up({
                "email": registration.email,
                "password": registration.password,
                "options": {
                    "data": {
                        "display_name": registration.display_name,
                        "role": UserRole.USER.value
                    }
                }
            })
            
            if auth_response.user:
                # Create user profile in our users table
                user_data = {
                    "id": auth_response.user.id,
                    "email": registration.email,
                    "display_name": registration.display_name,
                    "role": UserRole.USER.value,
                    "email_verified": False
                }
                
                # Insert into users table
                if self.admin_client:
                    self.admin_client.table("users").insert(user_data).execute()
                
                return {
                    "success": True,
                    "message": "Registration successful. Please check your email for verification.",
                    "user_id": auth_response.user.id,
                    "email_verification_required": True
                }
            else:
                return {
                    "success": False,
                    "message": "Registration failed. Please try again.",
                    "error": "No user returned from Supabase"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Registration failed: {str(e)}",
                "error": str(e)
            }
    
    # =====================================================
    # USER LOGIN
    # =====================================================
    
    async def login_user(self, login: LoginRequest) -> Dict[str, Any]:
        """Authenticate user and create session"""
        try:
            if not self.client:
                return {"success": False, "message": "Database not available", "error": "No client"}
            
            # Authenticate with Supabase
            auth_response = self.client.auth.sign_in_with_password({
                "email": login.email,
                "password": login.password
            })
            
            if auth_response.user and auth_response.session:
                # Get user profile from our database
                user_profile = await self.get_user_profile(auth_response.user.id)
                
                if not user_profile:
                    return {
                        "success": False,
                        "message": "User profile not found",
                        "error": "Profile missing"
                    }
                
                # Check if user is active
                if not user_profile.is_active:
                    return {
                        "success": False,
                        "message": "Account is deactivated. Please contact support.",
                        "error": "Account deactivated"
                    }
                
                # Update last login
                await self.update_last_login(auth_response.user.id)
                
                # Create session
                session_duration = timedelta(hours=self.config.session_duration)
                if login.remember_me:
                    session_duration = timedelta(days=30)  # Extended session
                
                session = AuthSession(
                    user_id=auth_response.user.id,
                    email=user_profile.email,
                    role=user_profile.role,
                    display_name=user_profile.display_name,
                    avatar_url=user_profile.avatar_url,
                    expires_at=datetime.utcnow() + session_duration
                )
                
                # Generate JWT token
                token = self.generate_session_token(session)
                
                return {
                    "success": True,
                    "message": "Login successful",
                    "token": token,
                    "session": session.dict(),
                    "user": user_profile.dict()
                }
            else:
                return {
                    "success": False,
                    "message": "Invalid email or password",
                    "error": "Authentication failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Login failed: {str(e)}",
                "error": str(e)
            }
    
    # =====================================================
    # SESSION MANAGEMENT
    # =====================================================
    
    def generate_session_token(self, session: AuthSession) -> str:
        """Generate JWT token for session"""
        if not JWT_AVAILABLE:
            # Fallback to simple token for testing
            return f"simple-token-{session.user_id}-{session.expires_at.timestamp()}"
            
        payload = {
            "user_id": session.user_id,
            "email": session.email,
            "role": session.role.value,
            "display_name": session.display_name,
            "exp": session.expires_at.timestamp(),
            "iat": datetime.utcnow().timestamp()
        }
        
        return jwt.encode(payload, self.config.jwt_secret, algorithm="HS256")
    
    def validate_session_token(self, token: str) -> Optional[AuthSession]:
        """Validate JWT token and return session"""
        try:
            if not JWT_AVAILABLE:
                # Simple token validation for testing
                if token.startswith("simple-token-"):
                    parts = token.split("-")
                    if len(parts) >= 4:
                        user_id = parts[2]
                        exp_timestamp = float(parts[3])
                        if datetime.utcnow().timestamp() < exp_timestamp:
                            return AuthSession(
                                user_id=user_id,
                                email="test@example.com",
                                role=UserRole.USER,
                                expires_at=datetime.fromtimestamp(exp_timestamp)
                            )
                return None
            
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=["HS256"])
            
            # Check expiration
            if datetime.utcnow().timestamp() > payload["exp"]:
                return None
            
            session = AuthSession(
                user_id=payload["user_id"],
                email=payload["email"],
                role=UserRole(payload["role"]),
                display_name=payload.get("display_name"),
                expires_at=datetime.fromtimestamp(payload["exp"])
            )
            
            return session
            
        except Exception:
            return None
    
    # =====================================================
    # USER PROFILE MANAGEMENT
    # =====================================================
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        try:
            if not self.admin_client:
                return None
                
            response = self.admin_client.table("users").select("*").eq("id", user_id).single().execute()
            
            if response.data:
                return UserProfile(**response.data)
            return None
            
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    async def update_user_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user profile"""
        try:
            if not self.admin_client:
                return False
                
            # Remove sensitive fields that shouldn't be updated directly
            safe_updates = {k: v for k, v in updates.items() 
                          if k not in ['id', 'email', 'role', 'created_at']}
            
            if safe_updates:
                self.admin_client.table("users").update(safe_updates).eq("id", user_id).execute()
            
            return True
            
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    async def update_last_login(self, user_id: str) -> bool:
        """Update user's last login timestamp"""
        try:
            if not self.admin_client:
                return False
                
            self.admin_client.table("users").update({
                "last_login": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            return True
            
        except Exception as e:
            print(f"Error updating last login: {e}")
            return False
    
    # =====================================================
    # ROLE-BASED ACCESS CONTROL
    # =====================================================
    
    def check_permission(self, user_role: UserRole, required_role: UserRole) -> bool:
        """Check if user role has required permissions"""
        role_hierarchy = {
            UserRole.USER: 1,
            UserRole.AUTHOR: 2,
            UserRole.EDITOR: 3,
            UserRole.ADMIN: 4
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)

# =====================================================
# GLOBAL AUTH SERVICE INSTANCE
# =====================================================

# Create global authentication service
auth_service = AuthenticationService()

# =====================================================
# CONVENIENCE FUNCTIONS
# =====================================================

async def register_user(email: str, password: str, confirm_password: str, display_name: str) -> Dict[str, Any]:
    """Convenience function for user registration"""
    registration = RegisterRequest(
        email=email,
        password=password,
        confirm_password=confirm_password,
        display_name=display_name
    )
    return await auth_service.register_user(registration)

async def login_user(email: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
    """Convenience function for user login"""
    login_request = LoginRequest(
        email=email,
        password=password,
        remember_me=remember_me
    )
    return await auth_service.login_user(login_request)

def validate_session(token: str) -> Optional[AuthSession]:
    """Convenience function for session validation"""
    return auth_service.validate_session_token(token)

async def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """Convenience function for getting user profile"""
    return await auth_service.get_user_profile(user_id)

def check_permission(user_role: UserRole, required_role: UserRole) -> bool:
    """Convenience function for permission checking"""
    return auth_service.check_permission(user_role, required_role)

# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    print("✅ Authentication system loaded successfully!")
    print("📋 Available classes:")
    print("   - UserRole, AuthSession, LoginRequest, RegisterRequest, UserProfile")
    print("📋 Available functions:")
    print("   - register_user, login_user, validate_session, get_user_profile, check_permission")
    print("⚙️  Configure SUPABASE_URL, SUPABASE_ANON_KEY, and JWT_SECRET environment variables.")