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

### "Spreadsheet not found"
Check that the Spreadsheet ID is correct and that you have access to the spreadsheet.

### Export button is disabled
Make sure you've:
1. Fetched orders first
2. Signed in with Google (if using Google Sheets export)

## Security Notes

- OAuth tokens are stored encrypted in the database
- Each user's tokens are stored separately
- Tokens only have access to Google Sheets (not other Google services)
- Users can revoke access at any time in their Google Account settings

