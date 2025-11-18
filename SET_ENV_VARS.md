# Setting Environment Variables on Your Server

This guide shows you exactly where to set the Google OAuth credentials (`GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`) on different hosting platforms.

## Quick Steps by Platform

### Render (Most Common)

**Use Environment Variables (NOT Secret Files)**

1. **Go to your Render dashboard**: https://dashboard.render.com
2. **Click on your web service** (the app you deployed)
3. **Click "Environment"** in the left sidebar
4. **Click "Add Environment Variable"** button (this is in the "Environment Variables" section, NOT "Secret Files")
5. **Add these two variables**:
   - **Key**: `GOOGLE_CLIENT_ID`
     **Value**: `your-actual-client-id.apps.googleusercontent.com` (paste your real Client ID here)
   - **Key**: `GOOGLE_CLIENT_SECRET`
     **Value**: `your-actual-client-secret` (paste your real Client Secret here)
6. **Click "Save Changes"** - Your app will automatically redeploy

**Important**: 
- ✅ Use **Environment Variables** (key-value pairs)
- ❌ Do NOT use **Secret Files** (those are for file-based secrets like certificates)
- The app reads these as environment variables, so they must be in the "Environment Variables" section

**Where to find your credentials**: 
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Navigate to: APIs & Services → Credentials
- Find your OAuth 2.0 Client ID
- Click on it to see both the Client ID and Client Secret

---

### Railway

1. **Go to your Railway dashboard**: https://railway.app
2. **Click on your project**
3. **Click on your service** (the deployed app)
4. **Click the "Variables" tab** at the top
5. **Click "New Variable"** button
6. **Add these two variables**:
   - **Variable**: `GOOGLE_CLIENT_ID`
     **Value**: `your-actual-client-id.apps.googleusercontent.com`
   - **Variable**: `GOOGLE_CLIENT_SECRET`
     **Value**: `your-actual-client-secret`
7. Variables are saved automatically

---

### Heroku

**Option 1: Via Dashboard**
1. Go to https://dashboard.heroku.com
2. Click on your app
3. Go to **Settings** tab
4. Click **"Reveal Config Vars"**
5. Click **"Add"** and add:
   - `GOOGLE_CLIENT_ID` = `your-actual-client-id.apps.googleusercontent.com`
   - `GOOGLE_CLIENT_SECRET` = `your-actual-client-secret`
6. Click **"Save"**

**Option 2: Via Command Line**
```bash
heroku config:set GOOGLE_CLIENT_ID="your-actual-client-id.apps.googleusercontent.com" --app your-app-name
heroku config:set GOOGLE_CLIENT_SECRET="your-actual-client-secret" --app your-app-name
```

---

### Fly.io

1. **Install Fly CLI** (if not already installed):
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Set the secrets**:
   ```bash
   fly secrets set GOOGLE_CLIENT_ID="your-actual-client-id.apps.googleusercontent.com" -a your-app-name
   fly secrets set GOOGLE_CLIENT_SECRET="your-actual-client-secret" -a your-app-name
   ```

3. **Restart your app**:
   ```bash
   fly deploy -a your-app-name
   ```

---

### DigitalOcean App Platform

1. Go to https://cloud.digitalocean.com/apps
2. Click on your app
3. Go to **Settings** → **App-Level Environment Variables**
4. Click **"Edit"**
5. Add:
   - `GOOGLE_CLIENT_ID` = `your-actual-client-id.apps.googleusercontent.com`
   - `GOOGLE_CLIENT_SECRET` = `your-actual-client-secret`
6. Click **"Save"**

---

### VPS / Your Own Server

If you're running the app on your own server (VPS, DigitalOcean Droplet, etc.):

**Option 1: Export in your shell session** (temporary - lost on restart):
```bash
export GOOGLE_CLIENT_ID="your-actual-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-actual-client-secret"
```

**Option 2: Add to your systemd service file** (permanent):
1. Edit your service file:
   ```bash
   sudo nano /etc/systemd/system/your-app.service
   ```

2. Add under `[Service]`:
   ```ini
   [Service]
   Environment="GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com"
   Environment="GOOGLE_CLIENT_SECRET=your-actual-client-secret"
   ```

3. Reload and restart:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart your-app
   ```

**Option 3: Use a `.env` file** (if using a process manager like PM2 or supervisor):
1. Create `.env` file in your app directory:
   ```bash
   GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-actual-client-secret
   ```

2. Make sure your app loads the `.env` file (most Python apps do this automatically with `python-dotenv`)

---

## Getting Your Google OAuth Credentials

If you don't have your Client ID and Client Secret yet:

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Select your project** (or create a new one)
3. **Enable Google Sheets API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. **Create OAuth Credentials**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure OAuth consent screen first
   - Application type: **Web application**
   - Name: Your app name
   - **Authorized redirect URIs**: 
     - For production: `https://your-domain.com/auth/google/callback`
     - For local: `http://127.0.0.1:5001/auth/google/callback`
   - Click "Create"
5. **Copy the credentials**:
   - **Client ID**: Looks like `123456789-abc.apps.googleusercontent.com`
   - **Client Secret**: Looks like `GOCSPX-abc123xyz`

---

## Verifying It Works

After setting the environment variables:

1. **Restart your app** (if it doesn't auto-restart)
2. **Go to your app's Configuration page**
3. **Look for the "Google Sheets Export" section**
4. **Click "Sign in with Google"**
5. **If it works**: You'll be redirected to Google's login page
6. **If it doesn't work**: Check the error message - it will tell you if the credentials are missing or invalid

---

## Important Notes

- ✅ **Use Environment Variables, not Secret Files** - These credentials should be set as environment variables (key-value pairs), not as secret files
- ✅ **Environment variables are secure** - They're not visible in your code or logs
- ✅ **Never commit credentials to git** - Always use environment variables in production
- ✅ **Restart required** - Most platforms auto-restart, but some require manual restart
- ✅ **Case sensitive** - Make sure variable names are exactly: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
- ⚠️ **No quotes needed** - When setting via dashboard, don't include quotes around the values
- ⚠️ **Quotes needed for CLI** - When using command line, use quotes if values contain special characters

### Render-Specific Notes

- **Environment Variables vs Secret Files**: 
  - ✅ **Environment Variables**: Use these for `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
  - ❌ **Secret Files**: These are for file-based secrets (like SSL certificates, SSH keys). Don't use these for OAuth credentials.
- In Render's dashboard, you'll see both sections. Make sure you're adding to "Environment Variables", not "Secret Files"

---

## Troubleshooting

**"Google OAuth not configured" error:**
- Check that both variables are set (not just one)
- Check for typos in variable names
- Restart your app after setting variables
- Check your hosting platform's logs for errors

**"Invalid client" error:**
- Verify your Client ID and Client Secret are correct
- Make sure the redirect URI in Google Console matches your app's URL
- Check that Google Sheets API is enabled in your Google Cloud project

**Variables not working:**
- Some platforms require a redeploy after setting variables
- Check that you're setting them at the correct level (app-level, not build-level)
- Verify the variables are actually set by checking your platform's environment variable viewer

