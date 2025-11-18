# Setup Guide: Getting Started with Authentication

This guide will walk you through setting up the app with authentication, both locally and for deployment.

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Step 1: Install Dependencies

Open a terminal in your project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- Flask and Flask-Login (web framework and authentication)
- SQLAlchemy (database)
- Werkzeug (password hashing)
- Gunicorn (production server)
- All other existing dependencies

## Step 2: Test Locally

### Run the Application

```bash
python app.py
```

You should see:
```
============================================================
Shopify Order Categorization App
============================================================

Starting web server...
The browser will open automatically...
If it doesn't, go to: http://127.0.0.1:5001

Press Ctrl+C to stop the server
```

### First-Time Setup

1. **The browser should open automatically** to `http://127.0.0.1:5001`
   - If not, manually navigate to that URL

2. **You'll see the login page** (since you're not logged in yet)

3. **Click "Register"** to create your first account:
   - Username: Choose any username
   - Email: Your email address
   - Password: At least 6 characters
   - Confirm Password: Same password

4. **Click "Register"** - you'll be automatically logged in

5. **You're now in the app!** You should see:
   - Navigation bar at the top showing your username
   - The main dashboard with Fetch Orders, Product Rules, and Configuration sections

## Step 3: Configure Your Shopify API

1. **Go to the "Configuration" section** (scroll down on the main page)

2. **Enter your Shopify credentials**:
   - Shop Domain: `your-shop.myshopify.com`
   - Access Token: Your Shopify Admin API access token
   - API Version: `2024-01` (or your preferred version)

3. **Click "Save Configuration"**

4. **Note**: If you leave these empty, the app will use dummy data for testing

## Step 4: Create Product Rules

1. **Go to the "Product Rules" section**

2. **Click "Add Rule"**:
   - Description: e.g., "Consignment items"
   - Keywords: e.g., "consignment, consign"
   - Add components (Investor, State Taxes, Federal Taxes, Consigner)
   - Set percentages or flat amounts

3. **Click "Add Rule"** to save

## Step 5: Test the Full Workflow

1. **Go to "Fetch Orders"**
2. **Select a date range** (or use quick buttons)
3. **Click "Fetch Orders"**
4. **Review the results**
5. **Click "Export to CSV"** to download

## Step 6: Test Multiple Users (Optional)

To verify multi-user isolation:

1. **Click "Logout"** in the top navigation
2. **Register a second account** with different credentials
3. **Notice**: This user has no rules or configuration (isolated data)
4. **Add rules and config** for this user
5. **Logout and login as the first user** - you'll see only your data

## Database Location

The database is automatically created in:
- **Location**: `instance/app.db` (SQLite database file)
- **Created automatically** on first run
- **Contains**: Users, configurations, and rules

You can delete this file to reset everything (all users and data will be lost).

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask_login'"

**Solution**: Run `pip install -r requirements.txt` again

### "Port 5001 already in use"

**Solution**: 
- Stop any other Flask apps running on port 5001
- Or modify `app.py` to use a different port (change `port=5001` to another number)

### "Database locked" error

**Solution**: 
- This can happen if multiple processes try to access SQLite
- Close any other instances of the app
- For production, use PostgreSQL instead of SQLite

### Can't access the app

**Solution**:
- Make sure the server is running (check terminal for "Starting web server...")
- Try `http://localhost:5001` instead of `127.0.0.1:5001`
- Check your firewall settings

### Forgot your password

**Current limitation**: There's no password reset feature yet. You'll need to:
- Delete the `instance/app.db` file to reset all users
- Or manually edit the database (advanced)

## Next Steps: Deploy to Production

Once you've tested locally and everything works:

1. **See [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md)** for deployment instructions
2. **Choose a platform**: Render, Railway, or Fly.io (all have free tiers)
3. **Deploy** and share the URL with users

## Environment Variables (For Production)

When deploying, you'll need to set:

- `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `FLASK_ENV`: Set to `production`
- `DATABASE_URL`: Usually provided automatically by hosting platform

## Quick Reference

### Start the app:
```bash
python app.py
```

### Stop the app:
Press `Ctrl+C` in the terminal

### Reset everything:
```bash
rm -rf instance/app.db
python app.py  # Will create fresh database
```

### Check if it's working:
- Visit `http://127.0.0.1:5001`
- You should see the login page
- Register and login to access the app

---

**That's it!** Your app is now set up with authentication. Users can register accounts and each will have their own isolated data.

