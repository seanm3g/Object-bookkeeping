# How to Check Database Connection on Render

Since `DATABASE_URL` is set correctly but data isn't persisting, let's diagnose the issue.

## Step 1: Check Your App Logs

The app now logs database connection information. Check your logs:

1. **Go to your Render dashboard**
2. **Click on your Web Service**
3. **Click "Logs" tab**
4. **Look for these messages at startup:**

### ✅ Good Signs (PostgreSQL Working):
```
[DATABASE] Using PostgreSQL from DATABASE_URL environment variable
[DATABASE] Successfully connected to database
[DATABASE] Database tables initialized successfully
```

### ❌ Bad Signs (Still Using SQLite):
```
[DATABASE] WARNING: DATABASE_URL not set, using SQLite at ...
[DATABASE] NOTE: SQLite data will be lost on server restart.
```

### ❌ Error Signs (Connection Failed):
```
[DATABASE] ERROR: Failed to initialize database: ...
CRITICAL: Database initialization failed: ...
```

## Step 2: What to Look For in Logs

### If you see "WARNING: DATABASE_URL not set":
- The environment variable isn't being read by the app
- **Possible causes:**
  - Variable name is wrong (should be exactly `DATABASE_URL`)
  - App needs to be restarted after adding the variable
  - Variable is set in wrong service (should be in Web Service, not Database)

### If you see "ERROR: Failed to initialize database":
- The connection is failing
- **Check the error message:**
  - `could not connect to server` → Database service might be paused or URL is wrong
  - `password authentication failed` → Wrong DATABASE_URL value
  - `psycopg2` errors → Missing PostgreSQL driver (but it's in requirements.txt)

### If you see "Successfully connected" but data still doesn't persist:
- Connection works but something else is wrong
- **Check:**
  - Are you registering accounts while logged in?
  - Are you testing with the same account after restart?
  - Check if tables were created (see Step 3)

## Step 3: Verify Tables Were Created

After the app starts, the logs should show:
```
[DATABASE] Database tables initialized successfully
```

If you see this, the tables exist. If not, there might be a permissions issue.

## Step 4: Test the Connection

1. **Register a new account** on your app
2. **Immediately check the logs** - look for any errors when saving
3. **Restart the app** (Manual Deploy → Clear build cache & deploy)
4. **Check logs again** - should see the same database connection messages
5. **Try to log in** with the account you just created

## Step 5: Common Issues and Fixes

### Issue: Logs show "DATABASE_URL not set" but it's set in Render

**Possible causes:**
1. **Variable was added after deployment** - Restart the app
2. **Variable name typo** - Must be exactly `DATABASE_URL` (case-sensitive)
3. **Variable in wrong place** - Must be in Web Service, not Database service
4. **Render hasn't redeployed** - Try manual deploy

**Fix:**
1. Go to Web Service → Environment
2. Verify `DATABASE_URL` exists and value is correct
3. Click "Manual Deploy" → "Clear build cache & deploy"
4. Wait for deployment and check logs again

### Issue: Connection works but data doesn't persist

**Possible causes:**
1. **Using wrong account** - Each user has separate data
2. **Not logged in** - Data only saves when logged in
3. **Database connection is being reset** - Check for connection pool issues

**Fix:**
1. Make sure you're logged in (check top nav bar shows your username)
2. Register account while logged in
3. Test with same account after restart

### Issue: "could not connect to server"

**Possible causes:**
1. **Using External URL instead of Internal** - Must use Internal Database URL
2. **Database service is paused** - Check database service status
3. **Wrong region** - Database and app should be in same region

**Fix:**
1. Go to PostgreSQL service
2. Copy "Internal Database URL" (not External)
3. Update DATABASE_URL in Web Service with Internal URL
4. Redeploy

## Step 6: Get Detailed Error Information

If you're still having issues, the logs should now show:
- Which database type is being used
- Whether connection succeeded
- Any specific error messages

**Share these log messages** to get more specific help:
1. The `[DATABASE]` messages from startup
2. Any error messages when registering/logging in
3. Any `CRITICAL` messages

## Quick Diagnostic Checklist

- [ ] Logs show "Using PostgreSQL from DATABASE_URL"
- [ ] Logs show "Successfully connected to database"
- [ ] Logs show "Database tables initialized successfully"
- [ ] No `WARNING` or `ERROR` messages about database
- [ ] Can register account without errors
- [ ] Account persists after app restart

If all are ✅, database should be working. If any are ❌, follow the fixes above.

