# Fix: OAuth Redirect URI Mismatch Error

If you're seeing the error:
```
Error 400: redirect_uri_mismatch
You can't sign in to this app because it doesn't comply with Google's OAuth 2.0 policy.
```

This means your production redirect URI is not registered in Google Cloud Console.

## Quick Fix

### Step 1: Go to Google Cloud Console

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (the one where you created the OAuth credentials)

### Step 2: Edit Your OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Find your OAuth 2.0 Client ID (the one you're using for this app)
3. Click the **pencil icon** (Edit) next to it

### Step 3: Add Your Production Redirect URI

1. Scroll down to **"Authorized redirect URIs"**
2. Click **"+ ADD URI"**
3. Add your production redirect URI:
   ```
   https://object-bookkeeping.onrender.com/auth/google/callback
   ```
   ⚠️ **Important**: Replace `object-bookkeeping.onrender.com` with your actual domain if different!

4. Click **"SAVE"** at the bottom

### Step 4: Wait a Few Minutes

Google's changes can take 1-5 minutes to propagate. Wait a moment, then try again.

### Step 5: Test

1. Go back to your app: `https://object-bookkeeping.onrender.com`
2. Navigate to the Configuration section
3. Click **"Sign in with Google"**
4. It should now work! ✅

## Common Redirect URIs

Based on your hosting platform, your redirect URI will be:

- **Render**: `https://your-app-name.onrender.com/auth/google/callback`
- **Railway**: `https://your-app-name.up.railway.app/auth/google/callback`
- **Heroku**: `https://your-app-name.herokuapp.com/auth/google/callback`
- **Fly.io**: `https://your-app-name.fly.dev/auth/google/callback`
- **Custom Domain**: `https://your-domain.com/auth/google/callback`
- **Local Development**: `http://127.0.0.1:5001/auth/google/callback`

## Multiple Environments

If you're using the same OAuth credentials for both local development and production, make sure to add **both** redirect URIs:

1. `http://127.0.0.1:5001/auth/google/callback` (for local development)
2. `https://object-bookkeeping.onrender.com/auth/google/callback` (for production)

## Fix: OAuth 401 Error (Missing Authentication Credential)

If you're seeing an error like:
```
HttpError 401: Request is missing required authentication credential
```

This usually means:
1. **You have an old OAuth token** that was authorized with only the `spreadsheets` scope
2. **The code needs to be redeployed** with the updated scopes

### Solution:

1. **Make sure your code is deployed** with the latest changes (the code now requests both `spreadsheets` and `userinfo.email` scopes)

2. **Clear your old OAuth token**:
   - Go to your app's Configuration page
   - If you see "✓ Connected as: [email]", click the **"Disconnect"** button
   - This will clear the old token

3. **Re-authorize with Google**:
   - Click **"Sign in with Google"** again
   - You'll be prompted to authorize both scopes
   - This will create a new token with the correct permissions

4. **Alternative: Revoke access in Google**:
   - Go to [Google Account Security](https://myaccount.google.com/permissions)
   - Find your app and click "Remove Access"
   - Then sign in again from your app

## Still Not Working?

1. **Double-check the exact URL**: Make sure there are no typos, and it matches exactly (including `https://` and the trailing `/auth/google/callback`)

2. **Check your app's actual URL**: 
   - Go to your Render dashboard
   - Check what your actual app URL is
   - Make sure it matches what you added in Google Cloud Console

3. **Verify OAuth credentials**: Make sure the Client ID and Client Secret in your environment variables match the ones in Google Cloud Console

4. **Check OAuth consent screen**: Make sure your OAuth consent screen includes both scopes:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/userinfo.email`

5. **Wait longer**: Sometimes it can take up to 10 minutes for changes to propagate

6. **Verify code is deployed**: Make sure the latest code with both scopes is deployed to your server

## Need Help?

If you're still having issues:
1. Check the error message in your browser - it will show the exact redirect URI that's being used
2. Compare it character-by-character with what you added in Google Cloud Console
3. Make sure there are no extra spaces or characters

