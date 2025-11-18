# Simple Deployment Guide: Get Your App Online

Follow these steps to get your app on a website you can access from anywhere.

## Option 1: Render (Recommended - Easiest)

### What You Need:
- A GitHub account (free)
- 10 minutes

### Step-by-Step:

#### 1. Put Your Code on GitHub

**A. Create GitHub Account** (if needed):
- Go to https://github.com/signup
- Sign up (it's free)

**B. Create a Repository**:
- Go to https://github.com/new
- Repository name: `shopify-order-app`
- Make it **Public** (required for free hosting)
- Click "Create repository"

**C. Upload Your Code**:

Open Terminal and run these commands:

```bash
cd /Users/seangreen/code/Object-bookkeeping

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit"

# Add your GitHub repository (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/shopify-order-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Note**: When you push, GitHub will ask for your username and password. 
- Username: Your GitHub username
- Password: Use a **Personal Access Token** (not your GitHub password)
  - Get one here: https://github.com/settings/tokens
  - Click "Generate new token (classic)"
  - Check "repo" permission
  - Copy the token and use it as your password

#### 2. Deploy to Render

**A. Sign Up for Render**:
- Go to https://render.com
- Click "Get Started for Free"
- Sign up with GitHub (click "Continue with GitHub")

**B. Create Web Service**:
- Click "New +" → "Web Service"
- Find and select your repository: `shopify-order-app`
- Click "Connect"

**C. Configure**:
- **Name**: `shopify-order-app` (or your choice)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Plan**: **Free**

**D. Add Environment Variables**:
Click "Advanced" → "Add Environment Variable":

1. First variable:
   - **Key**: `SECRET_KEY`
   - **Value**: `aab2b7fa03888e592dff8dc59b8aab18dde6565f4e79c36043abd3e37ff5ba0b`

2. Second variable:
   - **Key**: `FLASK_ENV`
   - **Value**: `production`

**E. Deploy**:
- Click "Create Web Service"
- Wait 2-5 minutes for deployment
- Watch the logs - you'll see "Your service is live at:"
- Click the URL!

#### 3. Use Your App

1. Visit your URL (e.g., `https://shopify-order-app.onrender.com`)
2. Click "Register"
3. Create your account
4. Start using the app!

---

## Option 2: Railway (Alternative - Also Easy)

1. **Sign up**: https://railway.app (use GitHub to sign up)

2. **New Project** → **Deploy from GitHub repo**

3. **Select your repository**

4. **Add Environment Variables**:
   - Click "Variables" tab
   - Add `SECRET_KEY`: `aab2b7fa03888e592dff8dc59b8aab18dde6565f4e79c36043abd3e37ff5ba0b`
   - Add `FLASK_ENV`: `production`

5. **Deploy!** Railway auto-detects everything

Your app: `https://your-app-name.up.railway.app`

---

## Quick Reference

### Your SECRET_KEY (already generated):
```
aab2b7fa03888e592dff8dc59b8aab18dde6565f4e79c36043abd3e37ff5ba0b
```

### Environment Variables to Set:
- `SECRET_KEY` = (the key above)
- `FLASK_ENV` = `production`

### Important Files (already created):
- ✅ `Procfile` - Tells platform how to run your app
- ✅ `requirements.txt` - Lists all dependencies
- ✅ `.gitignore` - Prevents uploading secrets

---

## Troubleshooting

### "Git push failed"
- Make sure you created the GitHub repository first
- Use a Personal Access Token as your password (not your GitHub password)
- Get token: https://github.com/settings/tokens

### "Build failed"
- Check that all files are committed to git
- Make sure `requirements.txt` exists
- Check Render logs for specific errors

### "App won't start"
- Verify environment variables are set correctly
- Check that `SECRET_KEY` is set
- Look at runtime logs in Render dashboard

### "App is slow"
- Free tier spins down after 15 min of inactivity
- First request after spin-down takes ~30 seconds
- This is normal for free tier

---

## After Deployment

Once your app is live:
1. ✅ Bookmark your URL
2. ✅ Register your account
3. ✅ Configure Shopify API credentials
4. ✅ Add product rules
5. ✅ Start using it!

Your app will be accessible from anywhere with just the URL!

---

**Need help?** Check the deployment logs in your hosting platform's dashboard.

