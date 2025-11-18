# Deploy to Website: Step-by-Step Guide

This guide will help you deploy your app to a website so you can access it from anywhere with a URL.

## Recommended: Render (Free & Easy)

Render is the easiest option with a free tier. Your app will be available at a URL like `https://your-app-name.onrender.com`

### Step 1: Prepare Your Code

Your code is already ready! Just make sure you have:
- ✅ `app.py` (with authentication)
- ✅ `requirements.txt` (with all dependencies)
- ✅ `Procfile` (for deployment)
- ✅ `models.py` and `auth.py` (authentication files)

### Step 2: Push to GitHub (Required for Render)

If you haven't already, you need to put your code on GitHub:

1. **Create a GitHub account** (if you don't have one): https://github.com/signup

2. **Create a new repository**:
   - Go to https://github.com/new
   - Name it: `shopify-order-app` (or any name)
   - Make it **Public** (required for free Render tier)
   - Click "Create repository"

3. **Push your code to GitHub**:
   ```bash
   cd /Users/seangreen/code/Object-bookkeeping
   
   # Initialize git if not already done
   git init
   
   # Add all files
   git add .
   
   # Commit
   git commit -m "Initial commit with authentication"
   
   # Add your GitHub repository (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/shopify-order-app.git
   
   # Push to GitHub
   git branch -M main
   git push -u origin main
   ```

   **Note**: If you get authentication errors, you may need to set up a GitHub Personal Access Token.

### Step 3: Deploy to Render

1. **Sign up for Render**:
   - Go to https://render.com
   - Click "Get Started for Free"
   - Sign up with your GitHub account (easiest option)

2. **Create a New Web Service**:
   - In Render dashboard, click "New +"
   - Select "Web Service"
   - Click "Connect account" if you haven't connected GitHub yet
   - Select your repository: `shopify-order-app` (or whatever you named it)
   - Click "Connect"

3. **Configure Your Service**:
   - **Name**: `shopify-order-app` (or your choice - this becomes part of your URL)
   - **Region**: Choose closest to you (e.g., "Oregon (US West)")
   - **Branch**: `main` (or `master`)
   - **Root Directory**: Leave empty (or `.` if needed)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: **Free** (or "Starter" for always-on)

4. **Add Environment Variables**:
   Click "Advanced" → "Add Environment Variable" and add:
   
   - **Key**: `SECRET_KEY`
   - **Value**: `aab2b7fa03888e592dff8dc59b8aab18dde6565f4e79c36043abd3e37ff5ba0b`
     (This is a secure random key generated for you)
   
   - **Key**: `FLASK_ENV`
   - **Value**: `production`

5. **Deploy!**:
   - Click "Create Web Service"
   - Render will start building and deploying your app
   - This takes 2-5 minutes
   - Watch the logs to see progress

6. **Your App is Live!**:
   - Once deployed, you'll see "Your service is live at:"
   - Your URL will be: `https://your-app-name.onrender.com`
   - Click the URL to open your app!

### Step 4: First Use

1. **Visit your URL** (e.g., `https://shopify-order-app.onrender.com`)

2. **Register your account**:
   - Click "Register"
   - Enter username, email, and password
   - Click "Register"

3. **Start using the app!**:
   - Configure your Shopify API credentials
   - Add product rules
   - Fetch orders and export

## Important Notes

### Free Tier Limitations (Render)

- **Spins down after 15 minutes of inactivity**: First request after inactivity takes ~30 seconds to wake up
- **750 hours/month free**: Plenty for personal use
- **Public repository required**: Your code must be public on GitHub (or upgrade to paid)

### If You Want Always-On

Upgrade to Render's "Starter" plan ($7/month) for:
- Always-on (no spin-down)
- Private repositories
- Better performance

## Alternative: Railway (Also Free & Easy)

If you prefer Railway:

1. **Sign up**: https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. **Select your repository**
4. **Add Environment Variables**:
   - `SECRET_KEY`: (same as above)
   - `FLASK_ENV`: `production`
5. **Deploy!** Railway auto-detects Python and uses your `Procfile`

Your app will be at: `https://your-app-name.up.railway.app`

## Troubleshooting

### Build Fails

- Check the build logs in Render dashboard
- Make sure `requirements.txt` has all dependencies
- Verify `Procfile` exists with `web: gunicorn app:app`

### App Won't Start

- Check the runtime logs
- Verify environment variables are set
- Make sure `SECRET_KEY` is set

### Database Issues

- SQLite works on free tier but has limitations
- For production, consider upgrading to use PostgreSQL (Render provides this)

### App is Slow to Load

- Free tier spins down after inactivity
- First request after spin-down takes ~30 seconds
- Upgrade to paid plan for always-on

## Security Reminder

- **Never commit** your `SECRET_KEY` to GitHub
- Use environment variables (as shown above)
- The key I generated above is safe to use

## Next Steps

Once deployed:
1. ✅ Bookmark your URL
2. ✅ Register your account
3. ✅ Configure Shopify API
4. ✅ Start using it!

---

**Need help?** Check the logs in your Render dashboard for error messages.

