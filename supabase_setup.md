# Supabase Database Setup Guide for Nemesis Blog
<!-- cp -->
This guide will help you set up the Supabase database for your Nemesis Blog platform.

## 🚀 Quick Setup Steps

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create an account
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `nemesis-blog`
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your users
5. Click "Create new project"

### 2. Set Up Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Copy and paste the entire contents of `database_schema.sql`
3. Click **Run** to execute the schema
4. Verify tables were created in **Table Editor**

### 3. Configure Environment Variables

Create a `.env` file in your FastHTML project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Optional: Database direct connection (for advanced use)
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```

**To find your keys:**
1. Go to **Settings** → **API** in your Supabase dashboard
2. Copy the **URL** and **anon/public** key
3. Copy the **service_role** key (keep this secret!)

### 4. Install Python Dependencies

```bash
pip install supabase pydantic python-dotenv
```

### 5. Test Database Connection

```python
from fh_app.database_models import db

# Test connection
try:
    settings = await db.get_public_settings()
    print("✅ Database connection successful!")
    print(f"Site settings: {settings}")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

## 📊 Database Schema Overview

### Core Tables Structure

```
users (authors, commenters, admins)
├── posts (blog articles)
│   ├── post_tags (many-to-many with tags)
│   ├── comments (with replies via parent_id)
│   └── media_uploads (featured images, etc.)
├── categories (post categorization)
├── tags (flexible tagging)
├── contact_submissions (contact form data)
├── newsletter_subscribers (email list)
└── site_settings (global configuration)
```

### Key Features

- **UUID Primary Keys**: All tables use UUID for better security
- **Row Level Security**: Automatic security policies
- **Full-Text Search**: PostgreSQL search on posts
- **Automatic Timestamps**: Created/updated timestamps
- **Hierarchical Comments**: Nested replies support
- **Engagement Metrics**: View counts, likes, shares
- **SEO Ready**: Meta tags and descriptions
- **Media Management**: File uploads with metadata

## 🔐 Security Configuration

### Row Level Security (RLS) Policies

The schema includes pre-configured RLS policies:

- **Public Access**: Published posts, active categories, approved comments
- **User Access**: Users can create comments and contact submissions
- **Author Access**: Authors can manage their own posts
- **Admin Access**: Admins can manage all content

### Authentication Integration

To integrate with Supabase Auth:

```python
# In your FastHTML app
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# User signup
user = supabase.auth.sign_up({
    "email": "user@example.com",
    "password": "password123"
})

# User login
session = supabase.auth.sign_in_with_password({
    "email": "user@example.com", 
    "password": "password123"
})
```

## 📝 Sample Data

The schema includes sample data for:
- 6 default categories (Design, Technology, Lifestyle, etc.)
- Common tags (web-development, javascript, css, etc.)
- Essential site settings

## 🔧 Database Operations Examples

### Fetch Published Posts

```python
from fh_app.database_models import db

# Get latest posts
posts = await db.get_published_posts(limit=10)

# Get featured posts for hero slider
featured = await db.get_featured_posts(limit=5)

# Get posts by category
design_posts = await db.get_posts_by_category("design")

# Search posts
results = await db.search_posts("javascript tutorial")
```

### Create Content

```python
from fh_app.database_models import PostModel, CommentModel

# Create new post
post = PostModel(
    title="My New Blog Post",
    slug="my-new-blog-post",
    content="This is the post content...",
    excerpt="Short description...",
    status="published",
    is_featured=True
)
created_post = await db.create_post(post)

# Add comment
comment = CommentModel(
    post_id=created_post.id,
    guest_name="John Doe",
    guest_email="john@example.com",
    content="Great article!"
)
await db.create_comment(comment)
```

### Handle Forms

```python
from fh_app.database_models import ContactSubmissionModel

# Contact form submission
submission = ContactSubmissionModel(
    name="Jane Smith",
    email="jane@example.com",
    message="Hello, I have a question..."
)
await db.create_contact_submission(submission)

# Newsletter subscription
await db.subscribe_to_newsletter("user@example.com", "footer_form")
```

## 🚀 Performance Optimization

### Indexes

The schema includes optimized indexes for:
- Post queries by status, date, author, category
- Full-text search on post content
- Comment queries by post and status
- Category and tag lookups

### Caching Strategy

Consider implementing caching for:
- Published posts list
- Category navigation
- Popular posts
- Site settings

```python
# Example with simple in-memory cache
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_cached_posts(limit: int = 10):
    return await db.get_published_posts(limit)
```

## 🔄 Migration and Backup

### Database Migrations

For schema changes, create migration files:

```sql
-- migrations/001_add_post_views.sql
ALTER TABLE posts ADD COLUMN view_count INTEGER DEFAULT 0;
CREATE INDEX idx_posts_view_count ON posts(view_count DESC);
```

### Backup Strategy

Supabase provides automatic backups, but consider:
- Regular database dumps for critical data
- Export user-generated content
- Backup media files separately

## 📈 Monitoring and Analytics

### Database Metrics

Monitor in Supabase dashboard:
- Query performance
- Table sizes
- Connection usage
- Error rates

### Application Metrics

Track in your FastHTML app:
- Post view counts
- Comment engagement
- Newsletter signups
- Contact form submissions

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check environment variables
   - Verify Supabase project is active
   - Check network connectivity

2. **Permission Errors**
   - Review RLS policies
   - Check user authentication
   - Verify API key permissions

3. **Query Performance**
   - Use EXPLAIN ANALYZE for slow queries
   - Check index usage
   - Consider query optimization

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show all SQL queries
```

## 📚 Next Steps

After setting up the database:

1. **Connect to FastHTML**: Replace sample data with database calls
2. **Add Authentication**: Implement user login/signup
3. **Create Admin Panel**: Build content management interface
4. **Implement Search**: Connect search form to database
5. **Add File Uploads**: Set up Supabase Storage for images
6. **Email Integration**: Set up email notifications
7. **Performance Tuning**: Add caching and optimization

## 🆘 Support

- **Supabase Docs**: [docs.supabase.com](https://docs.supabase.com)
- **Community**: [github.com/supabase/supabase/discussions](https://github.com/supabase/supabase/discussions)
- **Database Models**: See `database_models.py` for detailed usage examples