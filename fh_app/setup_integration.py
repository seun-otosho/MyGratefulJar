#!/usr/bin/env python3
"""
Setup script for Nemesis Blog Database Integration
Helps configure environment and test database connection
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path("../.env")
    env_example = Path("../.env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ .env.example file not found")
        return False
    
    # Copy example to .env
    with open(env_example, 'r') as f:
        content = f.read()
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file from template")
    print("⚠️  Please edit .env file with your Supabase credentials")
    return True

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_imports():
    """Test if all required packages can be imported"""
    try:
        import supabase
        print("✅ supabase package imported successfully")
    except ImportError:
        print("❌ supabase package not found. Run: pip install supabase")
        return False
    
    try:
        import pydantic
        print("✅ pydantic package imported successfully")
    except ImportError:
        print("❌ pydantic package not found. Run: pip install pydantic")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv package imported successfully")
    except ImportError:
        print("❌ python-dotenv package not found. Run: pip install python-dotenv")
        return False
    
    return True

async def test_database_connection():
    """Test database connection"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from database_integration import get_homepage_data
        
        print("🔄 Testing database connection...")
        data = await get_homepage_data()
        
        print("✅ Database connection successful!")
        print(f"   - Featured post: {'Yes' if data.get('featured_post') else 'No'}")
        print(f"   - Regular posts: {len(data.get('regular_posts', []))}")
        print(f"   - Categories: {len(data.get('categories', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Check your Supabase URL and API key in .env file")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("🔄 Installing dependencies...")
    os.system("pip install -r requirements.txt")
    print("✅ Dependencies installed")

def main():
    """Main setup function"""
    print("🚀 Nemesis Blog Database Integration Setup")
    print("=" * 50)
    
    # Step 1: Create .env file
    print("\n1. Setting up environment file...")
    if not create_env_file():
        return False
    
    # Step 2: Install dependencies
    print("\n2. Installing dependencies...")
    install_dependencies()
    
    # Step 3: Test imports
    print("\n3. Testing package imports...")
    if not test_imports():
        print("❌ Please install missing packages and try again")
        return False
    
    # Step 4: Check environment variables
    print("\n4. Checking environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    
    if not check_environment():
        print("\n📝 Next steps:")
        print("1. Edit .env file with your Supabase credentials")
        print("2. Get credentials from: https://app.supabase.com/project/[your-project]/settings/api")
        print("3. Run this script again to test database connection")
        return False
    
    # Step 5: Test database connection
    print("\n5. Testing database connection...")
    import asyncio
    
    try:
        success = asyncio.run(test_database_connection())
        if success:
            print("\n🎉 Setup completed successfully!")
            print("\n📝 Next steps:")
            print("1. Run: python main_integrated.py")
            print("2. Visit: http://localhost:5001")
            print("3. Test the /test-db endpoint to verify integration")
            return True
        else:
            print("\n❌ Database connection failed")
            print("Please check your Supabase configuration")
            return False
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)