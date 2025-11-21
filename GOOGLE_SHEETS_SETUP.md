# Google Sheets Export Setup Guide

This guide explains how to set up Google Sheets export functionality using OAuth2 authentication.

## Overview

The Google Sheets export feature allows users to export order data directly to Google Sheets with a simple "Sign in with Google" button. No credentials files or service account setup is required for end users.

## For Administrators/Developers: Setting Up OAuth Credentials

Before users can export to Google Sheets, you need to set up OAuth credentials in Google Cloud Console. This is a one-time setup.

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "Shopify Order Export")
4. Click "Create"

### Step 2: Enable Google Sheets API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and click "Enable"

### Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" (unless you have a Google Workspace)
   - Fill in the required fields:
     - App name: "Shopify Order Export" (or your app name)
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"
   - Add scopes:
     - `openid`
     - `https://www.googleapis.com/auth/spreadsheets`
     - `https://www.googleapis.com/auth/userinfo.email`
   - Click "Save and Continue"
   - Add test users (if in testing mode) or publish the app
   - Click "Save and Continue"

4. Create OAuth Client ID:
   - Application type: "Web application"
   - Name: "Shopify Order Export Web Client"
   - Authorized redirect URIs:
     - For local development: `http://127.0.0.1:5001/auth/google/callback`
     - For production: `https://your-domain.com/auth/google/callback`
   - Click "Create"

5. Copy the **Client ID** and **Client Secret**

### Step 4: Configure the Application

You have two options for providing the OAuth credentials:

#### Option A: Environment Variables (Recommended for Production)

Set these environment variables on your server. The app will automatically use them if set, and fall back to `config.json` if not found.

**📖 For detailed step-by-step instructions for your specific hosting platform, see [SET_ENV_VARS.md](SET_ENV_VARS.md)**

**For Local Development:**

```bash
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"
```

**For Production Hosting Platforms:**

**Render:**
1. Go to your service dashboard
2. Click "Environment" in the left sidebar
3. Click "Add Environment Variable"
4. Add:
   - Key: `GOOGLE_CLIENT_ID`, Value: `your-client-id.apps.googleusercontent.com`
   - Key: `GOOGLE_CLIENT_SECRET`, Value: `your-client-secret`
5. Click "Save Changes" (service will redeploy automatically)

**Railway:**
1. Go to your project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Click "New Variable"
5. Add:
   - `GOOGLE_CLIENT_ID` = `your-client-id.apps.googleusercontent.com`
   - `GOOGLE_CLIENT_SECRET` = `your-client-secret`
6. Variables are saved automatically

**Heroku:**
```bash
heroku config:set GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
heroku config:set GOOGLE_CLIENT_SECRET="your-client-secret"
```

Or via dashboard:
1. Go to your app settings
2. Click "Reveal Config Vars"
3. Add the two variables

**Fly.io:**
```bash
fly secrets set GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
fly secrets set GOOGLE_CLIENT_SECRET="your-client-secret"
```

**DigitalOcean App Platform:**
1. Go to your app settings
2. Navigate to "App-Level Environment Variables"
3. Add the two variables
4. Click "Save"

**VPS/Server (systemd service):**
Create/edit `/etc/systemd/system/your-app.service`:
```ini
[Service]
Environment="GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com"
Environment="GOOGLE_CLIENT_SECRET=your-client-secret"
```

**Docker:**
Add to your `docker-compose.yml`:
```yaml
environment:
  - GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
  - GOOGLE_CLIENT_SECRET=your-client-secret
```

Or use `.env` file:
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

**Verification:**
After setting environment variables, restart your app and check that the "Sign in with Google" button works. The app will use environment variables if available, otherwise it falls back to `config.json`.

#### Option B: Config File (For Development)

Add to your `config.json`:

```json
{
  "google_oauth": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "client_secret": "your-client-secret"
  }
}
```

**Note:** Never commit `config.json` with credentials to version control. Use environment variables in production.

## For End Users: Using Google Sheets Export

Once OAuth is configured by the administrator, end users can export to Google Sheets with just a few clicks:

### Step 1: Sign In with Google

1. Go to the Configuration section
2. Find the "Google Sheets Export" section
3. Click "Sign in with Google"
4. Select your Google account
5. Grant permissions to access Google Sheets
6. You'll see "✓ Connected as: your-email@gmail.com"

### Step 2: Export to Google Sheets

1. Fetch orders using the date range picker
2. Click "Export to Google Sheets" button
3. If you've set a Spreadsheet ID in configuration, data will be added to that spreadsheet
4. If no Spreadsheet ID is set, a new spreadsheet will be created
5. The spreadsheet will open automatically (or you can click the link)

### Optional: Use a Specific Spreadsheet

If you want all exports to go to the same spreadsheet:

1. Create a Google Sheet (or use an existing one)
2. Copy the spreadsheet URL from your browser's address bar
   - URL format: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
3. Paste the full URL into the "Spreadsheet ID" field in Configuration
   - The spreadsheet ID will be automatically extracted from the URL
   - Alternatively, you can paste just the ID directly
4. Click "Save Configuration"

## How It Works

- **OAuth Flow**: Users sign in once with their Google account. The app stores an OAuth token securely.
- **Token Refresh**: Tokens are automatically refreshed when they expire (no need to sign in again).
- **Monthly Tabs**: Orders are organized by month into separate tabs (e.g., "2024-01", "2024-02").
- **Same Format as CSV**: The Google Sheets export uses the same column structure as the CSV export, including dynamic columns for consigners and investors.

## Troubleshooting

### "OAuth libraries not installed"
Install the required packages:
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client gspread
```

### "Google OAuth not configured"
The administrator needs to set up OAuth credentials (see above).

### "Token expired and refresh failed"
Sign in with Google again. This usually happens if the refresh token is invalid.

### "Insufficient authentication scopes" or "Request had insufficient authentication scopes"

This error means your OAuth token doesn't have all the required permissions. This can happen for several reasons:

#### Common Causes:

1. **You authenticated before the app was updated** with the `openid` scope
2. **Your token was created with older scopes**
3. **The OAuth consent screen wasn't properly configured** in Google Cloud Console
4. **Your account isn't authorized** (if the app is in testing mode)
5. **Account-level restrictions** (work/school accounts may have restrictions)

#### Solution Steps:

**Step 1: Check OAuth Consent Screen Configuration (Administrator)**

If you're the administrator, verify the OAuth consent screen is configured correctly:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **OAuth consent screen**
3. Check the **Scopes** section - make sure all three scopes are listed:
   - `openid`
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/userinfo.email`
4. If any are missing, click **"ADD OR REMOVE SCOPES"** and add them
5. Save the changes

**Step 2: Check if App is in Testing Mode**

1. In the OAuth consent screen, check the **Publishing status**
2. If it says **"Testing"**:
   - Your email must be added as a **Test User**
   - Go to **Test users** section
   - Click **"+ ADD USERS"**
   - Add your Google account email address
   - Save changes
3. **OR** publish the app (if appropriate for your use case):
   - Click **"PUBLISH APP"**
   - Confirm the publishing

**Step 3: Re-authenticate Your Account**

1. **Disconnect your Google account**:
   - Go to the Configuration section in the app
   - Click the **"Disconnect"** button next to your connected email
   
2. **Sign in again with Google**:
   - Click **"Sign in with Google"**
   - You'll be prompted to authorize the app
   - **Important**: Make sure you see all three permissions being requested:
     - See your email address
     - See, edit, create, and delete all your Google Sheets spreadsheets
   - Grant all permissions
   
3. **Try exporting again**

**Step 4: Check Account Type Restrictions**

If you're using a **Google Workspace (work/school) account**, your organization may have restrictions:
- Contact your IT administrator to allow the app
- Or use a personal Google account instead

**Step 5: Verify Token Has Correct Scopes**

After re-authenticating, the app should work. If it still doesn't:
- Check the error message - it should now be more specific
- Make sure you granted all permissions during the OAuth flow
- Try disconnecting and reconnecting one more time

**Note:** After re-authenticating with the correct OAuth consent screen configuration, you'll have a fresh token with all the correct scopes, and the export should work.

### "Spreadsheet not found" or "Permission denied" or "Failed to open spreadsheet"

This error means the Google account you signed in with doesn't have access to the spreadsheet. Here's how to fix it:

#### Option 1: Share the Spreadsheet with Your Google Account (Recommended)

1. **Open the spreadsheet** in Google Sheets
2. **Click the "Share" button** (top right corner)
3. **Enter the email address** of the Google account you used to sign in to the app
   - You can find this email in the app - it shows "✓ Connected as: [your-email]" in the Configuration section
4. **Set permissions to "Editor"** (or at least "Viewer" if you only want to read)
5. **Click "Send"**
6. **Try exporting again**

#### Option 2: Use a Different Spreadsheet

1. **Create a new spreadsheet** in Google Sheets (or use one you already own)
2. **Copy the spreadsheet ID** from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
   - The `SPREADSHEET_ID` is the long string between `/d/` and `/edit`
3. **Paste it into the "Spreadsheet ID" field** in the app's Configuration section
4. **Click "Save Configuration"**
5. **Try exporting again**

#### Option 3: Re-authenticate with the Correct Account

If you want to use a different Google account:

1. **Click "Disconnect"** in the Configuration section
2. **Click "Sign in with Google"** again
3. **Choose the Google account** that has access to the spreadsheet
4. **Grant permissions**
5. **Try exporting again**

#### Option 4: Leave Spreadsheet ID Empty

If you leave the "Spreadsheet ID" field empty, the app will create a new spreadsheet for each export. This is useful if you don't have a specific spreadsheet to use.

### Export button is disabled
Make sure you've:
1. Fetched orders first
2. Signed in with Google (if using Google Sheets export)

## Security Notes

- OAuth tokens are stored encrypted in the database
- Each user's tokens are stored separately
- Tokens only have access to Google Sheets (not other Google services)
- Users can revoke access at any time in their Google Account settings

