# Quick Fix for 503 Error

## Most Common Cause: Missing Database Configuration

The 503 error is most likely because your app can't connect to the database. Here's how to fix it:

### Step 1: Check Your Render Logs

1. Go to https://dashboard.render.com
2. Click on your web service
3. Click "Logs" tab
4. Look for errors like:
   - `[DATABASE] ERROR: Failed to initialize database`
   - `psycopg2.OperationalError`
   - `DATABASE_URL not set`

### Step 2: Verify Database Setup

**Do you have a PostgreSQL database?**
- If NO: Create one (see below)
- If YES: Verify the connection (see below)

### Step 3: Create PostgreSQL Database (if needed)

1. In Render dashboard, click "New +" → "PostgreSQL"
2. Name it (e.g., `shopify-order-db`)
3. Choose Free tier
4. Click "Create Database"
5. **Copy the "Internal Database URL"** (starts with `postgres://`)

### Step 4: Set Environment Variables

1. Go to your **Web Service** (not the database)
2. Click "Environment" in the left sidebar
3. Add these variables:

   **Required:**
   - `DATABASE_URL` = (paste the Internal Database URL from step 3)
   - `SECRET_KEY` = (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
   
   **Optional but recommended:**
   - `FLASK_ENV` = `production`

4. Click "Save Changes"

### Step 5: Redeploy

1. Render will automatically redeploy when you save environment variables
2. Wait for deployment to complete (check "Events" tab)
3. Visit your app URL

### Step 6: Test Health Endpoint

Visit: `https://your-app.onrender.com/health`

You should see:
```json
{"status": "ok", "database": "connected"}
```

If you see `"database": "disconnected"`, check your `DATABASE_URL` again.

## Still Getting 503?

### Check These:

1. **Is the database running?**
   - Go to your PostgreSQL service
   - Status should be "Available"

2. **Is DATABASE_URL correct?**
   - Should start with `postgres://` or `postgresql://`
   - Should be the "Internal Database URL" (not External)
   - No extra spaces or quotes

3. **Are there build errors?**
   - Check "Events" tab for build failures
   - Check "Logs" tab for runtime errors

4. **Is the app starting?**
   - Check logs for: `Starting gunicorn`
   - Check logs for: `[DATABASE] Successfully connected`

## Quick Test

After setting `DATABASE_URL`, check your logs. You should see:
```
[DATABASE] Using PostgreSQL from DATABASE_URL environment variable
[DATABASE] Successfully connected to database
[DATABASE] Database tables initialized successfully
```

If you see warnings about SQLite, your `DATABASE_URL` is not set correctly.

## Need More Help?

See [TROUBLESHOOT_503_ERROR.md](TROUBLESHOOT_503_ERROR.md) for detailed troubleshooting.

