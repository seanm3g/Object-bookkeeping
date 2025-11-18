# How to Verify Your Database Setup on Render

This guide will help you verify that PostgreSQL is properly configured and your data will persist after server restarts.

## Quick Verification Checklist

- [ ] PostgreSQL database service exists on Render
- [ ] `DATABASE_URL` environment variable is set in your Web Service
- [ ] `DATABASE_URL` value starts with `postgres://` or `postgresql://`
- [ ] App logs show no database connection errors
- [ ] You can register an account and it persists after restart

---

## Step 1: Verify PostgreSQL Database Exists

1. **Go to your Render dashboard**: https://dashboard.render.com
2. **Look at your services list** - you should see:
   - Your Web Service (e.g., `object-bookkeeping`)
   - A PostgreSQL service (e.g., `shopify-order-db` or similar)

**✅ If you see a PostgreSQL service**: Good! Continue to Step 2.

**❌ If you DON'T see a PostgreSQL service**: You need to create one first. See [FIX_DATABASE_PERSISTENCE.md](FIX_DATABASE_PERSISTENCE.md) for instructions.

---

## Step 2: Verify DATABASE_URL Environment Variable

### Option A: Check in Render Dashboard

1. **Click on your Web Service** (not the database)
2. **Click "Environment" in the left sidebar**
3. **Look for `DATABASE_URL` in the list**

**What to check:**
- ✅ **Key**: Should be exactly `DATABASE_URL` (all caps)
- ✅ **Value**: Should start with `postgres://` or `postgresql://`
- ✅ **Value**: Should NOT be empty

**Example of correct value:**
```
postgres://user:password@dpg-xxxxx-a.oregon-postgres.render.com/dbname
```

**❌ If `DATABASE_URL` is missing**: You need to add it. See [RENDER_ADD_DATABASE_URL.md](RENDER_ADD_DATABASE_URL.md).

**❌ If `DATABASE_URL` is empty or wrong**: Delete it and add it again with the correct value.

### Option B: Check via Logs (Alternative Method)

1. **Go to your Web Service**
2. **Click "Logs" tab**
3. **Look for startup messages**

If you see errors like:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```
This means you're still using SQLite (not PostgreSQL).

---

## Step 3: Get the Correct Database URL

If you need to add or fix `DATABASE_URL`:

1. **Click on your PostgreSQL database service** (not the web service)
2. **Look for "Internal Database URL"** in the service details
3. **Click "Copy"** to copy the URL
4. **Important**: Use "Internal Database URL", NOT "External Database URL"

The Internal Database URL should look like:
```
postgres://username:password@hostname:5432/database_name
```

---

## Step 4: Verify the Connection Works

### Check App Logs

1. **Go to your Web Service**
2. **Click "Logs" tab**
3. **Look for these indicators:**

**✅ Good signs (using PostgreSQL):**
- No database errors
- App starts successfully
- You see normal Flask startup messages

**❌ Bad signs (still using SQLite or connection failed):**
- `sqlite3.OperationalError` errors
- `psycopg2` import errors
- `OperationalError: could not connect to server`
- `FATAL: password authentication failed`

### Common Errors and Fixes

**Error: `ModuleNotFoundError: No module named 'psycopg2'`**
- **Fix**: Add `psycopg2-binary>=2.9.0` to your `requirements.txt`
- Commit and push to trigger a redeploy

**Error: `could not connect to server`**
- **Fix**: Make sure you're using the **Internal Database URL**, not External
- Make sure the database service is running (not paused)

**Error: `password authentication failed`**
- **Fix**: The DATABASE_URL might be incorrect. Delete it and re-add it from the PostgreSQL service

---

## Step 5: Test Data Persistence

This is the ultimate test - if your data persists after restart, everything is working!

### Test Steps:

1. **Register a new account** on your app
   - Use a unique username (e.g., `test-user-123`)
   - Note the username and password

2. **Verify you can log in** with that account

3. **Restart your app**:
   - Go to your Web Service on Render
   - Click "Manual Deploy" → "Clear build cache & deploy"
   - OR wait for an automatic redeploy
   - Wait for deployment to finish

4. **Try to log in again** with the same account

**✅ If login works**: PostgreSQL is configured correctly! Your data is persisting.

**❌ If login fails** (account doesn't exist): You're still using SQLite. Go back and verify Steps 1-4.

---

## Step 6: Verify Database Tables Were Created

You can check if the database tables exist by looking at the logs or testing functionality:

1. **Register an account** - this creates the `users` table
2. **Add a product rule** - this creates the `user_rules` table
3. **Save configuration** - this creates/updates the `user_configs` table

If these work without errors, the tables exist and are working.

---

## Visual Guide: What to Look For

### In Render Dashboard - Services List:
```
Your Services:
├─ object-bookkeeping (Web Service) ← Your app
└─ shopify-order-db (PostgreSQL) ← Your database (should exist!)
```

### In Web Service - Environment Variables:
```
Environment Variables
┌─────────────────────────────────────────────┐
│ Key              Value                      │
│ SECRET_KEY       ****************          │
│ FLASK_ENV        production                 │
│ DATABASE_URL     postgres://user:pass@...  │ ← Should be here!
└─────────────────────────────────────────────┘
```

### In PostgreSQL Service - Connection Info:
```
Connection Info
Internal Database URL: postgres://user:pass@host/db ← Copy this!
External Database URL: postgres://... ← Don't use this!
```

---

## Quick Diagnostic Commands

If you have SSH access to your Render service, you can run:

```bash
# Check if DATABASE_URL is set
echo $DATABASE_URL

# Should output something like: postgres://user:pass@host/db
```

But most users won't have SSH access, so use the dashboard method above.

---

## Still Having Issues?

### Double-Check These Common Mistakes:

1. **Wrong URL type**: Using "External Database URL" instead of "Internal Database URL"
   - ✅ Use Internal Database URL (starts with `postgres://`)
   - ❌ Don't use External Database URL

2. **Wrong service**: Adding DATABASE_URL to the database service instead of web service
   - ✅ Add to Web Service environment variables
   - ❌ Don't add to PostgreSQL service

3. **Typo in variable name**: 
   - ✅ Must be exactly: `DATABASE_URL` (all caps, underscore)
   - ❌ Not: `DATABASE_URLS`, `database_url`, `DB_URL`, etc.

4. **Missing PostgreSQL driver**:
   - Check `requirements.txt` includes `psycopg2-binary>=2.9.0`
   - If not, add it and redeploy

5. **Database service is paused**:
   - Check your PostgreSQL service status
   - It should be "Active", not "Paused"

---

## Summary

**To verify your database is set up correctly:**

1. ✅ PostgreSQL service exists
2. ✅ `DATABASE_URL` is set in Web Service environment variables
3. ✅ `DATABASE_URL` starts with `postgres://`
4. ✅ No database errors in logs
5. ✅ Data persists after app restart

**If all 5 are true, you're good to go!** 🎉

**If any are false, follow the fixes above.**

---

## Need More Help?

- **Can't find Environment section?** See [RENDER_ADD_DATABASE_URL.md](RENDER_ADD_DATABASE_URL.md)
- **Don't have a PostgreSQL database?** See [FIX_DATABASE_PERSISTENCE.md](FIX_DATABASE_PERSISTENCE.md)
- **Still losing data?** Check the logs for specific error messages and troubleshoot from there

