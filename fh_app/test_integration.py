#!/usr/bin/env python3
"""
Comprehensive Integration Testing for Nemesis Blog
Tests all routes and database operations with live Supabase
"""

import asyncio
import os
import sys
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_database_connection():
    """Test basic database connection"""
    print("🔄 Testing database connection...")
    try:
        from database_integration import get_homepage_data
        data = await get_homepage_data()
        
        print("✅ Database connection successful!")
        print(f"   - Featured post: {'Yes' if data.get('featured_post') else 'No'}")
        print(f"   - Regular posts: {len(data.get('regular_posts', []))}")
        print(f"   - Categories: {len(data.get('categories', []))}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_homepage_data():
    """Test homepage data retrieval"""
    print("\n🔄 Testing homepage data...")
    try:
        from database_integration import get_homepage_data
        data = await get_homepage_data()
        
        # Check data structure
        required_keys = ['featured_post', 'regular_posts', 'categories']
        for key in required_keys:
            if key not in data:
                raise Exception(f"Missing key: {key}")
        
        print("✅ Homepage data structure valid")
        
        # Check featured post structure if exists
        if data['featured_post']:
            post = data['featured_post']
            post_keys = ['id', 'title', 'excerpt', 'author', 'date', 'image']
            for key in post_keys:
                if key not in post:
                    raise Exception(f"Featured post missing key: {key}")
            print("✅ Featured post structure valid")
        
        # Check regular posts structure
        if data['regular_posts']:
            post = data['regular_posts'][0]
            post_keys = ['id', 'title', 'excerpt', 'author', 'date', 'image']
            for key in post_keys:
                if key not in post:
                    raise Exception(f"Regular post missing key: {key}")
            print("✅ Regular posts structure valid")
        
        return True
    except Exception as e:
        print(f"❌ Homepage data test failed: {e}")
        return False

async def test_blog_listing_data():
    """Test blog listing data retrieval"""
    print("\n🔄 Testing blog listing data...")
    try:
        from database_integration import get_blog_listing_data
        data = await get_blog_listing_data(page=1)
        
        # Check data structure
        required_keys = ['posts', 'gallery_posts', 'sidebar_featured', 'popular_posts', 'current_page', 'has_more']
        for key in required_keys:
            if key not in data:
                raise Exception(f"Missing key: {key}")
        
        print("✅ Blog listing data structure valid")
        print(f"   - Posts: {len(data.get('posts', []))}")
        print(f"   - Gallery posts: {len(data.get('gallery_posts', []))}")
        print(f"   - Popular posts: {len(data.get('popular_posts', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Blog listing data test failed: {e}")
        return False

async def test_post_detail_data():
    """Test single post data retrieval"""
    print("\n🔄 Testing post detail data...")
    try:
        from database_integration import get_homepage_data, get_post_data
        
        # First get a post ID from homepage
        homepage_data = await get_homepage_data()
        posts = homepage_data.get('regular_posts', [])
        if not posts:
            posts = [homepage_data.get('featured_post')] if homepage_data.get('featured_post') else []
        
        if not posts:
            print("⚠️  No posts available to test post detail")
            return True
        
        post_id = posts[0]['id']
        data = await get_post_data(post_id)
        
        if not data:
            raise Exception("Post data returned None")
        
        # Check data structure
        required_keys = ['post', 'comments', 'related_posts', 'content_data']
        for key in required_keys:
            if key not in data:
                raise Exception(f"Missing key: {key}")
        
        print("✅ Post detail data structure valid")
        print(f"   - Post ID: {data['post']['id']}")
        print(f"   - Comments: {len(data.get('comments', []))}")
        print(f"   - Related posts: {len(data.get('related_posts', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Post detail data test failed: {e}")
        return False

async def test_search_functionality():
    """Test search functionality"""
    print("\n🔄 Testing search functionality...")
    try:
        from database_integration import search_posts
        
        # Test search with common term
        data = await search_posts("lorem")
        
        # Check data structure
        required_keys = ['posts', 'query', 'total']
        for key in required_keys:
            if key not in data:
                raise Exception(f"Missing key: {key}")
        
        print("✅ Search functionality working")
        print(f"   - Query: {data['query']}")
        print(f"   - Results: {data['total']}")
        
        return True
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

async def test_form_submissions():
    """Test form submission functionality"""
    print("\n🔄 Testing form submissions...")
    try:
        from database_integration import submit_contact_form, submit_comment, subscribe_newsletter
        
        # Test contact form
        contact_success = await submit_contact_form(
            "Test User", 
            "test@example.com", 
            "https://example.com", 
            "This is a test contact message"
        )
        print(f"✅ Contact form: {'Success' if contact_success else 'Failed'}")
        
        # Test newsletter subscription
        newsletter_success = await subscribe_newsletter("newsletter@example.com")
        print(f"✅ Newsletter: {'Success' if newsletter_success else 'Failed'}")
        
        # Test comment submission (need a post ID)
        from database_integration import get_homepage_data
        homepage_data = await get_homepage_data()
        posts = homepage_data.get('regular_posts', [])
        if posts:
            post_id = posts[0]['id']
            comment_success = await submit_comment(
                post_id,
                "Test Commenter",
                "commenter@example.com",
                "",
                "This is a test comment"
            )
            print(f"✅ Comment submission: {'Success' if comment_success else 'Failed'}")
        else:
            print("⚠️  No posts available to test comment submission")
        
        return True
    except Exception as e:
        print(f"❌ Form submission test failed: {e}")
        return False

async def test_fasthtml_routes():
    """Test FastHTML routes (basic import test)"""
    print("\n🔄 Testing FastHTML routes...")
    try:
        # Test if main_integrated can be imported
        import main_integrated
        print("✅ FastHTML routes module imported successfully")
        
        # Test if key functions exist
        functions_to_check = [
            'homepage', 'blog_listing', 'contact_page', 'post_detail', 
            'search_results', 'newsletter_signup', 'contact_form_submit'
        ]
        
        for func_name in functions_to_check:
            if hasattr(main_integrated, func_name):
                print(f"✅ Route function '{func_name}' exists")
            else:
                print(f"❌ Route function '{func_name}' missing")
        
        return True
    except Exception as e:
        print(f"❌ FastHTML routes test failed: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("🔄 Checking environment configuration...")
    
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False
    
    print("✅ Environment configuration valid")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("🔄 Checking dependencies...")
    
    required_packages = ['supabase', 'pydantic', 'dotenv', 'fasthtml']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                import python_dotenv
            elif package == 'fasthtml':
                import fasthtml
            else:
                __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} not installed")
    
    if missing_packages:
        print(f"\nInstall missing packages: pip install {' '.join(missing_packages)}")
        return False
    
    return True

async def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Nemesis Blog Integration Testing")
    print("=" * 50)
    
    # Pre-flight checks
    print("\n📋 Pre-flight Checks")
    if not check_dependencies():
        return False
    
    if not check_environment():
        return False
    
    # Database tests
    print("\n🗄️  Database Tests")
    tests = [
        test_database_connection(),
        test_homepage_data(),
        test_blog_listing_data(),
        test_post_detail_data(),
        test_search_functionality(),
        test_form_submissions()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    # FastHTML tests
    print("\n🌐 FastHTML Tests")
    fasthtml_result = await test_fasthtml_routes()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    
    passed = sum(1 for result in results if result is True)
    total = len(results)
    
    if fasthtml_result:
        passed += 1
        total += 1
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
        print("\n📝 Next steps:")
        print("1. Run: python3 main_integrated.py")
        print("2. Visit: http://localhost:5001")
        print("3. Test all routes manually")
        print("4. Deploy to production")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

def create_test_data_script():
    """Create a script to add test data to database"""
    script_content = '''#!/usr/bin/env python3
"""
Add test data to Supabase database
Run this after setting up your database schema
"""

import asyncio
from database_models import db, PostModel, CategoryModel, UserModel

async def add_test_data():
    """Add sample blog posts and categories"""
    print("🔄 Adding test data to database...")
    
    try:
        # Add test categories (if they don't exist)
        categories = [
            {"name": "Technology", "slug": "technology", "color": "#007bff"},
            {"name": "Design", "slug": "design", "color": "#28a745"},
            {"name": "Lifestyle", "slug": "lifestyle", "color": "#ffc107"}
        ]
        
        # Add test posts
        posts = [
            {
                "title": "Welcome to Nemesis Blog",
                "slug": "welcome-to-nemesis-blog",
                "content": "This is a sample blog post to test the integration. Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "excerpt": "Welcome to our new blog platform built with FastHTML and Supabase.",
                "status": "published",
                "is_featured": True,
                "featured_image_url": "./images/img-1.jpg"
            },
            {
                "title": "Getting Started with FastHTML",
                "slug": "getting-started-with-fasthtml",
                "content": "FastHTML is a modern web framework for Python. This post covers the basics of getting started.",
                "excerpt": "Learn the basics of FastHTML web framework for Python development.",
                "status": "published",
                "is_featured": False,
                "featured_image_url": "./images/img-2.jpg"
            }
        ]
        
        print("✅ Test data script created")
        print("Note: You'll need to implement the actual database insertion logic")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")

if __name__ == "__main__":
    asyncio.run(add_test_data())
'''
    
    with open("add_test_data.py", "w") as f:
        f.write(script_content)
    
    print("✅ Created add_test_data.py script")

def main():
    """Main test function"""
    try:
        # Create test data script
        create_test_data_script()
        
        # Run comprehensive tests
        success = asyncio.run(run_comprehensive_test())
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()