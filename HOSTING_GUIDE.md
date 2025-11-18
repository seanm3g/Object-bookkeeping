# Hosting Guide: Converting to a Web Service

This guide explains how to convert your Shopify Order Categorization app into a hosted web service (like Zapier) with username/password authentication.

## Overview

To host this application online with authentication, you need to:

1. **Add User Authentication** - Login/logout system with password hashing
2. **Multi-User Support** - Each user has their own configuration and rules
3. **Database Storage** - Store user accounts and per-user configurations
4. **Session Management** - Secure session handling
5. **Deploy to a Web Server** - Host on a platform like Heroku, Railway, Render, or your own server

## Architecture Changes

### Current Architecture (Single User)
- Single `config.json` file
- No authentication
- Runs on localhost only

### New Architecture (Multi-User Web Service)
- SQLite/PostgreSQL database for users and configs
- Flask-Login for session management
- Password hashing with Werkzeug
- Per-user configuration storage
- Protected routes requiring authentication

## Implementation Steps

### Step 1: Add Authentication Dependencies

Add these to `requirements.txt`:
- `flask-login` - User session management
- `werkzeug` - Password hashing (usually included with Flask)

### Step 2: Database Schema

Create tables for:
- **users**: id, username, email, password_hash, created_at
- **user_configs**: user_id, shop_domain, access_token, api_version
- **user_rules**: user_id, rule_id, rule_data (JSON)

### Step 3: Authentication Routes

Add routes for:
- `/login` - User login page
- `/register` - User registration page
- `/logout` - Logout endpoint
- `/profile` - User profile/settings page

### Step 4: Update Existing Routes

All existing routes need to:
- Check if user is authenticated
- Load user-specific configuration
- Save user-specific data

### Step 5: Deployment Options

#### Option A: Platform-as-a-Service (Easiest)

**Recommended Platforms:**
1. **Render** (https://render.com) - Free tier available, easy setup
2. **Railway** (https://railway.app) - Simple deployment, good free tier
3. **Heroku** (https://heroku.com) - Popular, but no free tier anymore
4. **Fly.io** (https://fly.io) - Good free tier, global deployment

**Steps for Render:**
1. Create account on Render
2. Connect your GitHub repository
3. Create a new "Web Service"
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn app:app`
6. Add environment variables (SECRET_KEY, DATABASE_URL)
7. Deploy!

#### Option B: VPS/Cloud Server

**Recommended Providers:**
- **DigitalOcean** - $6/month droplet
- **Linode** - $5/month instance
- **AWS EC2** - Pay-as-you-go
- **Google Cloud Platform** - Free tier available

**Steps:**
1. Set up Ubuntu server
2. Install Python, nginx, PostgreSQL
3. Clone your repository
4. Set up systemd service
5. Configure nginx as reverse proxy
6. Set up SSL with Let's Encrypt

#### Option C: Docker Container

Package the app in Docker for easy deployment anywhere:
- Docker Hub
- AWS ECS
- Google Cloud Run
- Azure Container Instances

## Security Considerations

1. **Password Hashing**: Use Werkzeug's password hashing (bcrypt)
2. **Session Security**: Use secure, HTTP-only cookies
3. **CSRF Protection**: Add Flask-WTF for CSRF tokens
4. **Rate Limiting**: Prevent brute force attacks
5. **HTTPS**: Always use SSL/TLS in production
6. **Secret Key**: Use strong, random SECRET_KEY
7. **SQL Injection**: Use parameterized queries (SQLAlchemy handles this)
8. **API Tokens**: Encrypt stored Shopify access tokens

## Environment Variables

Set these in your hosting platform:

```bash
SECRET_KEY=your-random-secret-key-here
DATABASE_URL=sqlite:///app.db  # or PostgreSQL URL
FLASK_ENV=production
```

## Database Migration

For production, consider:
- **SQLite** - Simple, file-based (good for small deployments)
- **PostgreSQL** - Better for production, multiple users
- **MySQL** - Alternative to PostgreSQL

## File Structure Changes

```
Object-bookkeeping/
├── app.py                 # Main Flask app (updated with auth)
├── models.py              # Database models (NEW)
├── auth.py                # Authentication routes (NEW)
├── templates/
│   ├── login.html         # Login page (NEW)
│   ├── register.html      # Registration page (NEW)
│   └── base.html          # Base template with nav (NEW)
├── static/                # CSS, JS (optional)
├── migrations/            # Database migrations (if using Flask-Migrate)
└── instance/
    └── app.db             # SQLite database (created automatically)
```

## Testing Locally Before Deployment

1. Test user registration
2. Test login/logout
3. Verify each user sees only their own data
4. Test that unauthenticated users are redirected
5. Test password reset (if implemented)

## Monitoring & Maintenance

1. **Logging**: Set up application logging
2. **Error Tracking**: Use Sentry or similar
3. **Backups**: Regular database backups
4. **Updates**: Keep dependencies updated
5. **Monitoring**: Uptime monitoring (UptimeRobot, Pingdom)

## Cost Estimates

**Free Tier Options:**
- Render: Free tier (spins down after inactivity)
- Railway: $5/month credit
- Fly.io: Generous free tier

**Paid Options:**
- VPS: $5-10/month
- Platform hosting: $7-25/month
- Domain: $10-15/year

## Next Steps

After implementing authentication:
1. Add password reset functionality
2. Add email verification
3. Add user management (admin panel)
4. Add usage analytics
5. Add API rate limiting per user
6. Add subscription/billing (if monetizing)

## Quick Start Commands

Once deployed, users can:
1. Visit your URL
2. Click "Register" to create account
3. Log in with username/password
4. Configure their Shopify API credentials
5. Start using the app!

---

**Note**: This guide provides the roadmap. The actual implementation code is in the updated `app.py` and new files created for authentication.

