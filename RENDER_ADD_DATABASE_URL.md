# How to Add DATABASE_URL to Your Render App

## Step-by-Step Instructions

### Step 1: Get Your Internal Database URL

1. **Go to your Render dashboard**: https://dashboard.render.com
2. **Find your PostgreSQL database service** (the one you created, not your web service)
   - It should be listed on your dashboard
   - It might be named something like `shopify-order-db` or similar
3. **Click on the PostgreSQL service** to open it
4. **Look for "Internal Database URL"** in the service details
   - It will look like: `postgres://user:password@hostname:5432/database_name`
   - **Important**: Use the "Internal Database URL", NOT the "External Database URL"
5. **Click the "Copy" button** next to the Internal Database URL
   - Or manually select and copy the entire URL

### Step 2: Add DATABASE_URL to Your Web Service

1. **Go back to your Render dashboard** (click "Dashboard" in the top left)
2. **Find your Web Service** (your app, not the database)
   - It should be listed on your dashboard
   - It might be named something like `shopify-order-app` or similar
3. **Click on your Web Service** to open it
4. **Look for the left sidebar menu** - you should see:
   - Overview
   - **Environment** ← Click this one!
   - Logs
   - Events
   - Settings
   - etc.
5. **Click "Environment"** in the left sidebar
6. **You should now see the Environment Variables section**
   - It will show existing environment variables (like `SECRET_KEY`, `FLASK_ENV`, etc.)
   - There's an "Add Environment Variable" button or a "+" button

### Step 3: Add the DATABASE_URL Variable

1. **Click "Add Environment Variable"** (or the "+" button)
2. **In the "Key" field**, type: `DATABASE_URL`
   - Make sure it's exactly: `DATABASE_URL` (all caps, with underscore)
3. **In the "Value" field**, paste the Internal Database URL you copied in Step 1
   - It should look like: `postgres://user:password@hostname:5432/database_name`
   - Don't add quotes around it
4. **Click "Save Changes"** (or "Add" or "Save")
5. **Your app will automatically redeploy** with the new environment variable

## If You Can't Find the Environment Section

### Option A: Check Different Views

Render's interface can vary. Try these:

1. **Look for tabs at the top** of your web service page:
   - Overview
   - Environment
   - Logs
   - Settings
   - Click the "Environment" tab

2. **Look in the Settings page**:
   - Click "Settings" in the left sidebar
   - Scroll down - environment variables might be here
   - Look for "Environment Variables" section

3. **Look for a gear icon or settings icon** near the top of the page

### Option B: Use the Search/Filter

1. On your web service page, use `Ctrl+F` (or `Cmd+F` on Mac)
2. Search for "Environment" or "Variable"
3. This will highlight where it is on the page

### Option C: Check the URL

The environment variables page URL should be something like:
```
https://dashboard.render.com/web/your-service-name/environment
```

Try navigating directly to:
1. Your web service page
2. Add `/environment` to the end of the URL

## Visual Guide (What to Look For)

When you're on your Web Service page, you should see:

**Left Sidebar:**
```
Dashboard
  └─ Your Services
      ├─ shopify-order-app (Web Service) ← Click this
      └─ shopify-order-db (PostgreSQL) ← Get URL from here
```

**After clicking your Web Service:**
```
Left Sidebar:
  Overview
  Environment ← Click this!
  Logs
  Events
  Settings
```

**Environment Variables Section:**
```
Environment Variables
┌─────────────────────────────────────┐
│ Key              Value              │
│ SECRET_KEY       ****************   │
│ FLASK_ENV        production         │
│                                   │
│ [+ Add Environment Variable]       │
└─────────────────────────────────────┘
```

## Alternative: Using Render CLI

If you can't find the UI, you can use Render's CLI:

1. **Install Render CLI**:
   ```bash
   npm install -g render-cli
   ```

2. **Login**:
   ```bash
   render login
   ```

3. **Set the environment variable**:
   ```bash
   render env:set DATABASE_URL="your-internal-database-url-here" --service your-service-name
   ```

Replace:
- `your-internal-database-url-here` with the Internal Database URL you copied
- `your-service-name` with your actual web service name

## Verifying It Worked

After adding the `DATABASE_URL`:

1. **Wait for the deployment to finish** (you'll see it in the "Events" or "Logs" tab)
2. **Check that the variable is set**:
   - Go back to Environment section
   - You should see `DATABASE_URL` in the list
3. **Test your app**:
   - Register a new account
   - Restart your app (or wait for a redeploy)
   - Try to log in - your account should still exist!

## Troubleshooting

### "I still can't find the Environment section"

- Make sure you're on your **Web Service** page, not the PostgreSQL database page
- Try refreshing the page
- Try logging out and back into Render
- Check if you have the right permissions (are you the owner of the service?)

### "The Internal Database URL is grayed out or I can't copy it"

- Make sure your PostgreSQL database is running (not paused)
- Try clicking directly on the URL text to select it, then copy manually
- Check if there's a "Show" or "Reveal" button to display the full URL

### "I get an error when saving"

- Make sure the URL starts with `postgres://` or `postgresql://`
- Don't include quotes around the value
- Make sure there are no extra spaces before or after the URL
- The key must be exactly: `DATABASE_URL` (case-sensitive)

### "My app still loses data after adding DATABASE_URL"

- Verify `DATABASE_URL` is actually set (check the Environment section again)
- Check your app logs for database connection errors
- Make sure you used the **Internal** Database URL, not External
- Restart your app after setting the variable

## Quick Checklist

- [ ] Found your PostgreSQL database service
- [ ] Copied the Internal Database URL
- [ ] Found your Web Service
- [ ] Clicked "Environment" in the left sidebar
- [ ] Added `DATABASE_URL` as the key
- [ ] Pasted the Internal Database URL as the value
- [ ] Clicked "Save Changes"
- [ ] Waited for deployment to finish
- [ ] Verified `DATABASE_URL` appears in the environment variables list

## Still Stuck?

If you're still having trouble:

1. **Take a screenshot** of your Render dashboard and web service page
2. **Check Render's documentation**: https://render.com/docs/environment-variables
3. **Contact Render support** - they're usually very helpful

The key is: **Environment Variables are in the "Environment" section of your Web Service**, not in the database service.

