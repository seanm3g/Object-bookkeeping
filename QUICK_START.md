# Quick Start: 5-Minute Setup

Get your app running with authentication in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
cd /Users/seangreen/code/Object-bookkeeping
pip install -r requirements.txt
```

## Step 2: Run the App (30 seconds)

```bash
python app.py
```

The browser will open automatically to `http://127.0.0.1:5001`

## Step 3: Create Your Account (1 minute)

1. Click **"Register"** on the login page
2. Enter:
   - Username: `admin` (or your choice)
   - Email: `your@email.com`
   - Password: `password123` (or your choice, min 6 chars)
3. Click **"Register"**

You're now logged in! 🎉

## Step 4: Configure Shopify (2 minutes)

1. Scroll to **"Configuration"** section
2. Enter your Shopify credentials (or leave empty to use dummy data)
3. Click **"Save Configuration"**

## Step 5: Test It! (30 seconds)

1. Go to **"Fetch Orders"**
2. Click **"Fetch Orders"** (uses default date range)
3. See your orders appear!

## That's It!

Your app is now running with authentication. Each user who registers will have their own isolated data.

## Next: Deploy Online

Want to share this with others? See [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md) to deploy to Render, Railway, or Fly.io.

## Troubleshooting

**"Module not found" error?**
```bash
pip install -r requirements.txt
```

**Port already in use?**
- Stop other Flask apps, or
- Change port in `app.py` (line 1172, change `port=5001`)

**Want to start fresh?**
```bash
rm -rf instance/app.db
python app.py
```

---

**Need more details?** See [SETUP_GUIDE.md](SETUP_GUIDE.md) for comprehensive instructions.

