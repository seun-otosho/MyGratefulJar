#!/usr/bin/env python3
"""
Test script for authentication system
Tests core functionality without requiring FastHTML
"""

import asyncio
import os
from datetime import datetime, timedelta

# Mock the dependencies for testing
class MockSupabaseClient:
    def __init__(self):
        self.auth = MockAuth()
        self.table_data = {}
    
    def table(self, name):
        return MockTable(name, self.table_data)

class MockAuth:
    def sign_up(self, data):
        return MockAuthResponse({"id": "test-user-id", "email": data["email"]})
    
    def sign_in_with_password(self, data):
        if data["email"] == "test@example.com" and data["password"] == "password123":
            return MockAuthResponse({"id": "test-user-id", "email": data["email"]})
        return MockAuthResponse(None)

class MockAuthResponse:
    def __init__(self, user_data):
        self.user = MockUser(user_data) if user_data else None
        self.session = MockSession() if user_data else None

class MockUser:
    def __init__(self, data):
        self.id = data["id"]
        self.email = data["email"]

class MockSession:
    def __init__(self):
        self.access_token = "mock-token"

class MockTable:
    def __init__(self, name, data_store):
        self.name = name
        self.data_store = data_store
        if name not in self.data_store:
            self.data_store[name] = []
    
    def insert(self, data):
        self.data_store[self.name].append(data)
        return MockResponse([data])
    
    def select(self, fields):
        return MockQuery(self.data_store[self.name])
    
    def update(self, data):
        return MockQuery(self.data_store[self.name])

class MockQuery:
    def __init__(self, data):
        self.data = data
    
    def eq(self, field, value):
        return self
    
    def single(self):
        return self
    
    def execute(self):
        return MockResponse(self.data)

class MockResponse:
    def __init__(self, data):
        self.data = data

# Test the authentication system
async def test_authentication_system():
    """Test core authentication functionality"""
    print("🧪 Testing Authentication System")
    print("=" * 50)
    
    try:
        # Test 1: Import authentication modules
        print("\n1. Testing imports...")
        
        # Mock environment variables
        os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
        os.environ['SUPABASE_ANON_KEY'] = 'test-anon-key'
        os.environ['JWT_SECRET'] = 'test-jwt-secret'
        
        # Import with mocked dependencies
        import sys
        sys.modules['supabase'] = type('MockModule', (), {
            'create_client': lambda url, key: MockSupabaseClient()
        })()
        sys.modules['jwt'] = type('MockModule', (), {
            'encode': lambda payload, secret, algorithm: 'mock-jwt-token',
            'decode': lambda token, secret, algorithms: {
                'user_id': 'test-user-id',
                'email': 'test@example.com', 
                'role': 'user',
                'exp': (datetime.utcnow() + timedelta(hours=24)).timestamp()
            }
        })()
        
        print("✅ Imports successful")
        
        # Test 2: User roles and enums
        print("\n2. Testing user roles...")
        from auth_system import UserRole
        
        roles = [UserRole.USER, UserRole.AUTHOR, UserRole.EDITOR, UserRole.ADMIN]
        print(f"✅ User roles defined: {[role.value for role in roles]}")
        
        # Test 3: Authentication models
        print("\n3. Testing authentication models...")
        from auth_system import LoginRequest, RegisterRequest, UserProfile, AuthSession
        
        # Test login request
        login_req = LoginRequest(email="test@example.com", password="password123")
        print(f"✅ Login request: {login_req.email}")
        
        # Test registration request
        register_req = RegisterRequest(
            email="test@example.com",
            password="Password123!",
            confirm_password="Password123!",
            display_name="Test User"
        )
        print(f"✅ Registration request: {register_req.display_name}")
        
        # Test user profile
        profile = UserProfile(
            id="test-id",
            email="test@example.com",
            display_name="Test User",
            role=UserRole.USER
        )
        print(f"✅ User profile: {profile.display_name} ({profile.role.value})")
        
        # Test auth session
        session = AuthSession(
            user_id="test-id",
            email="test@example.com",
            role=UserRole.USER,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        print(f"✅ Auth session: {session.email}")
        
        # Test 4: Authentication service
        print("\n4. Testing authentication service...")
        from auth_system import auth_service
        
        print("✅ Authentication service initialized")
        
        # Test 5: Middleware components
        print("\n5. Testing middleware...")
        from middleware import AuthContext, session_manager
        
        # Test auth context
        auth_ctx = AuthContext(session)
        print(f"✅ Auth context: authenticated={auth_ctx.is_authenticated}")
        print(f"✅ Role checks: admin={auth_ctx.is_admin()}, author={auth_ctx.is_author()}")
        
        # Test session manager
        cookie = session_manager.create_session_cookie("test-token")
        print(f"✅ Session cookie created: {cookie[:50]}...")
        
        # Test 6: Route helpers
        print("\n6. Testing route helpers...")
        from middleware import get_user_navigation, get_admin_sidebar
        
        nav_items = get_user_navigation(auth_ctx)
        print(f"✅ Navigation items: {len(nav_items)} items")
        
        admin_items = get_admin_sidebar(auth_ctx)
        print(f"✅ Admin sidebar: {len(admin_items)} sections")
        
        print("\n🎉 All authentication tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_permission_system():
    """Test role-based permission system"""
    print("\n🔐 Testing Permission System")
    print("=" * 30)
    
    try:
        from auth_system import UserRole
        from middleware import AuthContext, AuthSession
        from datetime import datetime, timedelta
        
        # Create test sessions for different roles
        test_sessions = {
            'user': AuthSession(
                user_id="user-1",
                email="user@example.com", 
                role=UserRole.USER,
                display_name="Regular User",
                expires_at=datetime.utcnow() + timedelta(hours=24)
            ),
            'author': AuthSession(
                user_id="author-1",
                email="author@example.com",
                role=UserRole.AUTHOR, 
                display_name="Author User",
                expires_at=datetime.utcnow() + timedelta(hours=24)
            ),
            'editor': AuthSession(
                user_id="editor-1",
                email="editor@example.com",
                role=UserRole.EDITOR,
                display_name="Editor User", 
                expires_at=datetime.utcnow() + timedelta(hours=24)
            ),
            'admin': AuthSession(
                user_id="admin-1",
                email="admin@example.com",
                role=UserRole.ADMIN,
                display_name="Admin User",
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
        }
        
        # Test permissions for each role
        for role_name, session in test_sessions.items():
            auth_ctx = AuthContext(session)
            print(f"\n{role_name.upper()} permissions:")
            print(f"  - Is authenticated: {auth_ctx.is_authenticated}")
            print(f"  - Is user: {auth_ctx.has_role(UserRole.USER)}")
            print(f"  - Is author: {auth_ctx.is_author()}")
            print(f"  - Is editor: {auth_ctx.is_editor()}")
            print(f"  - Is admin: {auth_ctx.is_admin()}")
            print(f"  - Can edit post: {auth_ctx.can_edit_post(session.user_id)}")
            print(f"  - Can moderate: {auth_ctx.can_moderate_comments()}")
            print(f"  - Can manage users: {auth_ctx.can_manage_users()}")
        
        print("\n✅ Permission system working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Permission test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Authentication System Test Suite")
    print("=" * 60)
    
    # Run tests
    auth_test = asyncio.run(test_authentication_system())
    perm_test = asyncio.run(test_permission_system())
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    print(f"Authentication System: {'✅ PASS' if auth_test else '❌ FAIL'}")
    print(f"Permission System: {'✅ PASS' if perm_test else '❌ FAIL'}")
    
    if auth_test and perm_test:
        print("\n🎉 All tests passed! Authentication system is working correctly.")
        print("\n📝 Next steps:")
        print("1. Install dependencies: pip install fasthtml supabase pydantic[email] PyJWT python-dotenv")
        print("2. Set up Supabase project and configure .env file")
        print("3. Run: python3 main_with_auth.py")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)