# Quick Start: Deploying to a Web Service

This guide will help you deploy your Shopify Order Categorization app to a hosting platform so users can access it via URL with username/password authentication.

## What's Changed

Your app now supports:
- ✅ User registration and login
- ✅ Multi-user support (each user has their own config and rules)
- ✅ Database storage (SQLite for development, PostgreSQL for production)
- ✅ Secure password hashing
- ✅ Session management

## Quick Deploy Options

### Option 1: Render (Recommended - Easiest)

1. **Sign up** at https://render.com (free tier available)

2. **Create a new Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Or deploy from a public Git repository

3. **Configure the service**:
   - **Name**: `shopify-order-app` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or paid for always-on)

4. **Add a PostgreSQL Database** (IMPORTANT - Required for data persistence):
   - Click "New +" → "PostgreSQL"
   - Name it (e.g., `shopify-order-db`)
   - Choose Free tier
   - Click "Create Database"
   - Copy the "Internal Database URL"

5. **Add Environment Variables** to your Web Service:
   - `SECRET_KEY`: Generate a random string (use: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `FLASK_ENV`: `production`
   - `DATABASE_URL`: Paste the Internal Database URL from step 4

6. **Deploy!** Click "Create Web Service"

**⚠️ IMPORTANT**: Without a PostgreSQL database, your accounts and data will be lost on every restart! See [FIX_DATABASE_PERSISTENCE.md](FIX_DATABASE_PERSISTENCE.md) for details.

7. **Your app will be live at**: `https://your-app-name.onrender.com`

### Option 2: Railway

1. **Sign up** at https://railway.app

2. **Create a new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo" (or upload code)

3. **Railway auto-detects Python** and will:
   - Install dependencies from `requirements.txt`
   - Run `gunicorn app:app` (from Procfile)

4. **Add a PostgreSQL Database** (IMPORTANT - Required for data persistence):
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway automatically creates it
   - Copy the `DATABASE_URL` from the database service's Variables tab

5. **Add Environment Variables** to your Web Service:
   - `SECRET_KEY`: (generate as above)
   - `FLASK_ENV`: `production`
   - `DATABASE_URL`: Paste the `DATABASE_URL` from the PostgreSQL service

6. **Deploy!** Railway automatically deploys on git push

**⚠️ IMPORTANT**: Without a PostgreSQL database, your accounts and data will be lost on every restart! See [FIX_DATABASE_PERSISTENCE.md](FIX_DATABASE_PERSISTENCE.md) for details.

7. **Your app will be live at**: `https://your-app-name.up.railway.app`

### Option 3: Fly.io

1. **Install Fly CLI**: `curl -L https://fly.io/install.sh | sh`

2. **Sign up**: `fly auth signup`

3. **Create app**: `fly launch` (in your project directory)

4. **Add secrets**:
   ```bash
   fly secrets set SECRET_KEY="your-secret-key-here"
   fly secrets set FLASK_ENV="production"
   ```

5. **Deploy**: `fly deploy`

6. **Your app will be live at**: `https://your-app-name.fly.dev`

## Testing Locally First

Before deploying, test the authentication locally:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**:
   ```bash
   python app.py
   ```

3. **Open browser** to `http://127.0.0.1:5001`

4. **Register a new account**:
   - Click "Register"
   - Enter username, email, password
   - Click "Register"

5. **Test the app**:
   - Configure Shopify API credentials
   - Add product rules
   - Fetch orders
   - Export CSV

## Production Checklist

Before going live:

- [ ] **Set up PostgreSQL database** (REQUIRED - see [FIX_DATABASE_PERSISTENCE.md](FIX_DATABASE_PERSISTENCE.md))
- [ ] Set `DATABASE_URL` environment variable to your PostgreSQL connection string
- [ ] Set a strong `SECRET_KEY` (use `secrets.token_hex(32)`)
- [ ] Set `FLASK_ENV=production`
- [ ] Enable HTTPS (most platforms do this automatically)
- [ ] Test user registration and login
- [ ] **Test that accounts persist after restart** (register, restart app, try to log in)
- [ ] Test that users can't see each other's data
- [ ] Set up database backups (if using PostgreSQL)

**⚠️ CRITICAL**: If you skip setting up PostgreSQL, all user accounts and data will be lost every time the server restarts or redeploys!

## Database Migration

If you have existing data in `config.json`:

1. **Run locally** with the new code
2. **Register a user account**
3. **Manually copy** your rules and config from the old JSON file into the web interface
4. **Or** create a migration script (advanced)

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask_login'"
- Make sure `requirements.txt` includes all dependencies
- Run `pip install -r requirements.txt` locally to test

### "Database locked" errors
- This happens with SQLite in production with multiple workers
- Switch to PostgreSQL on your hosting platform

### Users can see each other's data
- Check that all routes have `@login_required`
- Verify `load_config()` uses `current_user.id`

### App won't start
- Check logs on your hosting platform
- Verify `gunicorn` is in `requirements.txt`
- Check that `Procfile` exists with `web: gunicorn app:app`

## Security Notes

1. **Never commit** `SECRET_KEY` to git
2. **Use environment variables** for all secrets
3. **Enable HTTPS** (most platforms do this automatically)
4. **Use PostgreSQL** in production (SQLite is fine for single-user local use)
5. **Regular backups** of your database

## Next Steps

After deployment:
1. Share your URL with users
2. They can register their own accounts
3. Each user configures their own Shopify API credentials
4. Each user has their own product rules

## Support

If you encounter issues:
1. Check the hosting platform's logs
2. Test locally first to isolate issues
3. Verify all environment variables are set
4. Check that the database is accessible

---

**That's it!** Your app is now ready to be shared as a web service. Users can access it from anywhere with just a URL and create their own accounts.

