# Fix: Accounts Not Persisting on Server

## The Problem

If you have to recreate your account every time the server restarts, you're using **SQLite on an ephemeral filesystem**. Most hosting platforms (Render, Railway, etc.) wipe the filesystem on each deployment/restart, which deletes your SQLite database file.

## The Solution: Use PostgreSQL

You need to set up a **PostgreSQL database** that persists separately from your app. This is a managed database service that survives restarts and deployments.

---

## Quick Fix for Render

### Step 1: Create a PostgreSQL Database

1. **Go to your Render dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"PostgreSQL"**
3. **Configure the database**:
   - **Name**: `shopify-order-db` (or your choice)
   - **Database**: `shopify_order_app` (or your choice)
   - **User**: Auto-generated (you can change it)
   - **Region**: Same region as your web service
   - **Plan**: Free tier is fine for development
4. **Click "Create Database"**

### Step 2: Connect Your App to the Database

1. **Copy the Internal Database URL**:
   - In your PostgreSQL service dashboard
   - Look for "Internal Database URL" (starts with `postgres://`)
   - Click "Copy" to copy it

2. **Add it to your Web Service**:
   - Go to your **Web Service** dashboard (not the database service)
   - **Click "Environment" in the left sidebar** (if you don't see it, see troubleshooting below)
   - Click **"Add Environment Variable"** button
   - **Key**: `DATABASE_URL` (exactly like this, all caps)
   - **Value**: Paste the Internal Database URL you copied (no quotes needed)
   - Click **"Save Changes"**

3. **Your app will automatically redeploy** and use PostgreSQL instead of SQLite

**📖 Having trouble finding the Environment section? See [RENDER_ADD_DATABASE_URL.md](RENDER_ADD_DATABASE_URL.md) for detailed step-by-step instructions with troubleshooting.**

### Step 3: Verify It Works

1. **Wait for the deployment to finish**
2. **Go to your app** and register a new account
3. **Restart your app** (or wait for a redeploy)
4. **Try to log in** - your account should still exist!

---

## Quick Fix for Railway

### Step 1: Create a PostgreSQL Database

1. **Go to your Railway project dashboard**
2. **Click "New"** → **"Database"** → **"Add PostgreSQL"**
3. **Railway automatically creates the database**

### Step 2: Connect Your App

1. **Click on your PostgreSQL service**
2. **Go to the "Variables" tab**
3. **Copy the `DATABASE_URL`** value

4. **Go to your Web Service**
5. **Go to the "Variables" tab**
6. **Click "New Variable"**
7. **Add**:
   - **Variable**: `DATABASE_URL`
   - **Value**: Paste the `DATABASE_URL` from the PostgreSQL service
8. **Variables are saved automatically**

### Step 3: Verify It Works

Same as Render - register an account, restart, and verify it persists.

---

## Quick Fix for Heroku

### Step 1: Add PostgreSQL Add-on

```bash
heroku addons:create heroku-postgresql:mini --app your-app-name
```

This automatically sets the `DATABASE_URL` environment variable.

### Step 2: Verify

```bash
heroku config:get DATABASE_URL --app your-app-name
```

You should see a PostgreSQL URL. Your app will automatically use it.

---

## How to Check What Database You're Using

### Check Your App Logs

Look for database connection messages. If you see SQLite, you're using the file-based database. If you see PostgreSQL, you're using the persistent database.

### Check Environment Variables

In your hosting platform's dashboard, check if `DATABASE_URL` is set:
- ✅ **If set**: You're using PostgreSQL (persistent)
- ❌ **If not set**: You're using SQLite (ephemeral, will be lost)

---

## Why This Happens

### SQLite (File-Based Database)
- ❌ Stored as a file on the filesystem
- ❌ Gets deleted when the server restarts/redeploys
- ❌ Not suitable for production hosting

### PostgreSQL (Managed Database)
- ✅ Stored in a separate database service
- ✅ Persists across restarts and deployments
- ✅ Recommended for production

---

## Important Notes

1. **Free Tier Databases**: Most platforms offer free PostgreSQL databases that are perfect for development
2. **Automatic Connection**: Once you set `DATABASE_URL`, your app automatically uses PostgreSQL
3. **No Code Changes Needed**: The app already supports PostgreSQL - just set the environment variable
4. **Data Migration**: Your old SQLite data won't automatically transfer - you'll need to recreate accounts (but this is a one-time thing)

---

## Troubleshooting

### "Database connection failed"

- Check that `DATABASE_URL` is set correctly
- Verify the database service is running
- Check that you're using the **Internal Database URL** (not External) on Render
- Make sure the database is in the same region as your app

### "Still losing data after setting DATABASE_URL"

- Verify `DATABASE_URL` is actually set (check your platform's environment variables)
- Restart your app after setting the variable
- Check app logs for database connection errors
- Make sure you're using the correct database URL format

### "How do I know if it's working?"

1. Register a new account
2. Note the username
3. Restart your app (or trigger a redeploy)
4. Try to log in with that username
5. If it works, PostgreSQL is configured correctly!

---

## Summary

**The Problem**: SQLite database files are deleted on server restart  
**The Solution**: Use PostgreSQL (managed database service)  
**How to Fix**: Add a PostgreSQL database and set `DATABASE_URL` environment variable  
**Result**: Your accounts and data will persist permanently

Once you set up PostgreSQL, you'll never have to recreate your account again!

