# Troubleshooting 503 Error on Render

A 503 error means your app is not responding. This guide will help you diagnose and fix the issue.

## Quick Diagnosis Steps

### Step 1: Check Render Logs

1. Go to your Render dashboard: https://dashboard.render.com
2. Click on your web service
3. Click on the **"Logs"** tab
4. Look for error messages, especially:
   - Database connection errors
   - Import errors
   - Startup errors
   - Timeout errors

### Step 2: Common Causes and Fixes

#### Issue 1: Database Connection Failure

**Symptoms:**
- Logs show: `[DATABASE] ERROR: Failed to initialize database`
- Logs show: `psycopg2.OperationalError` or similar database errors

**Fix:**
1. Verify `DATABASE_URL` is set in your web service environment variables
2. Make sure you created a PostgreSQL database (not just the web service)
3. Copy the **Internal Database URL** from your PostgreSQL service
4. Add it as `DATABASE_URL` environment variable in your web service
5. Redeploy

**How to check:**
- Go to your Render dashboard
- Click on your **PostgreSQL database** service
- Copy the "Internal Database URL" (starts with `postgres://`)
- Go to your **Web Service** → Environment tab
- Verify `DATABASE_URL` is set correctly

#### Issue 2: Missing Environment Variables

**Symptoms:**
- App starts but crashes on first request
- Authentication errors

**Required Environment Variables:**
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `FLASK_ENV=production` (optional but recommended)
- `DATABASE_URL` - From your PostgreSQL service

**Fix:**
1. Go to your Web Service → Environment tab
2. Add missing variables
3. Redeploy

#### Issue 3: App Taking Too Long to Start

**Symptoms:**
- Logs show app starting but then timeout
- 503 error after 30-60 seconds

**Fix:**
1. Check if database connection is slow
2. Add a health check endpoint (see below)
3. Increase gunicorn timeout (see below)

#### Issue 4: Gunicorn Configuration Issues

**Symptoms:**
- App starts but workers crash
- Intermittent 503 errors

**Fix:**
Create a `gunicorn_config.py` file (see below)

## Solutions

### Solution 1: Add Health Check Endpoint

Add this to your `app.py` to help Render detect when your app is ready:

```python
@app.route('/health')
def health():
    """Health check endpoint for Render."""
    return jsonify({'status': 'ok'}), 200
```

### Solution 2: Improve Database Error Handling

The app should handle database connection failures gracefully. Check that `init_db()` in `models.py` doesn't crash the app.

### Solution 3: Add Gunicorn Configuration

Create `gunicorn_config.py`:

```python
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "shopify-order-app"
```

Then update your Procfile:
```
web: gunicorn app:app -c gunicorn_config.py
```

### Solution 4: Test Database Connection Locally

Before deploying, test your database connection:

```python
# test_db.py
import os
from models import get_database_url, init_db

# Set your DATABASE_URL
os.environ['DATABASE_URL'] = 'your-postgres-url-here'

try:
    engine = init_db()
    print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

## Step-by-Step Recovery

1. **Check Logs First**
   - Go to Render dashboard → Your service → Logs
   - Look for the last error message
   - Copy the error

2. **Verify Environment Variables**
   - Go to Environment tab
   - Verify all required variables are set
   - Check for typos

3. **Test Database Connection**
   - Go to your PostgreSQL service
   - Verify it's running (status should be "Available")
   - Copy the Internal Database URL
   - Verify it's set in your web service

4. **Redeploy**
   - Make a small change (add a comment) and commit
   - Or manually trigger a redeploy in Render

5. **Check Health Endpoint**
   - Once deployed, visit: `https://your-app.onrender.com/health`
   - Should return: `{"status": "ok"}`

## Still Not Working?

If you're still getting 503 errors:

1. **Check Render Status**: https://status.render.com
2. **Verify Build Succeeded**: Check the "Events" tab in Render
3. **Check Resource Limits**: Free tier has limits
4. **Try Manual Deploy**: Use Render's "Manual Deploy" option
5. **Contact Support**: Render support is helpful for deployment issues

## Prevention

To prevent future 503 errors:

1. ✅ Always set `DATABASE_URL` before deploying
2. ✅ Test locally first with the same environment variables
3. ✅ Monitor logs regularly
4. ✅ Set up health checks
5. ✅ Use proper error handling in your code

