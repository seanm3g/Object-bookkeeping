# Shopify API Credentials Setup Guide

## Overview
To connect your application to Shopify, you need:
1. **Shop Domain** - Your shop's domain (e.g., `your-shop.myshopify.com`)
2. **Access Token** - An **Admin API** access token with the required permissions

## ⚠️ Important: Token Types

Shopify has different types of API tokens. Make sure you get the **correct one**:

| Token Prefix | API Type | What It's For | Can Fetch Orders? |
|--------------|----------|---------------|-------------------|
| `shpat_` | **Admin API** | Managing store data, orders, products | ✅ **YES - This is what you need!** |
| `shpss_` | Storefront API | Public-facing storefront queries | ❌ No - This won't work for orders |
| `shpca_` | Customer Account API | Customer account management | ❌ No |

**You need an Admin API token that starts with `shpat_`** to fetch orders. If you have a token starting with `shpss_`, that's a Storefront API token and won't work for this application.

## Method 1: Custom App (Recommended for MVP/Testing)

This is the **easiest method** for getting started. You create an app directly in your Shopify admin.

### Step-by-Step Instructions

1. **Log into your Shopify Admin**
   - Go to `https://your-shop.myshopify.com/admin`
   - Log in with your shop owner or staff account

2. **Navigate to App Development**
   - Click **"Settings"** (gear icon at bottom left) → **"Apps and sales channels"**
   - You should see the "App development" page

3. **Enable Legacy Custom Apps** (Simplest Option)
   - On the "App development" page, find the section **"Build legacy custom apps"**
   - Click the gray button **"Allow legacy custom app development"**
   - This enables the simpler custom app creation method (perfect for your desktop app)

4. **Create a New App**
   - After enabling legacy custom apps, you'll see a **"Create app"** button or link
   - Click **"Create app"** 
   - Enter an app name (e.g., "Order Categorization Tool")
   - Enter your email address (optional, for notifications)
   - Click **"Create app"**

5. **Configure API Scopes**
   - In your new app, click **"Configure Admin API scopes"**
   - You need to enable these scopes:
     - ✅ **`read_orders`** - Required to fetch orders
     - ✅ **`read_customers`** - Required to get customer information (optional but recommended)
   - Click **"Save"**

6. **Install the App**
   - Click **"Install app"** button at the top
   - Review the permissions and click **"Install"**

7. **Get Your Credentials**
   - After installation, you'll see **"API credentials"** tab
   - Under **"Admin API access token"**, click **"Reveal token once"** or **"Install app"** if you haven't already
   - **Copy the access token** - you'll need this for your config.json
   - ⚠️ **Important:** 
     - This token is only shown once! Save it immediately.
     - The token should start with **`shpat_`** (not `shpss_` or any other prefix)
     - If you see a token starting with `shpss_`, that's the Storefront API token - you need the Admin API token instead

8. **Get Your Shop Domain**
   - Your shop domain is in the URL: `https://your-shop.myshopify.com`
   - Use just the domain part: `your-shop.myshopify.com` (no `https://`)

### What You'll Have After Setup

- **Shop Domain:** `your-shop.myshopify.com`
- **Access Token:** `shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (starts with `shpat_`)
- **API Version:** `2025-10` (or latest stable version)

## Method 2: Partner Dashboard App (For Production)

If you plan to distribute your app or need more advanced features, create a public app through the Partner Dashboard.

### Steps

1. **Create Partner Account**
   - Go to https://partners.shopify.com
   - Sign up or log in

2. **Create App**
   - Click **"Apps"** → **"Create app"**
   - Choose **"Create app manually"**
   - Enter app name and details

3. **Configure OAuth**
   - Set up OAuth redirect URLs
   - Configure API scopes (same as above)

4. **Test Installation**
   - Use the test store or install on your store
   - Get access token after OAuth flow

**Note:** This method is more complex and requires OAuth implementation. For your MVP, Method 1 (Custom App) is recommended.

## Adding Credentials to Your App

Once you have your credentials, add them to `config.json`:

```json
{
  "shopify": {
    "shop_domain": "your-shop.myshopify.com",
    "access_token": "shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "api_version": "2025-10"
  },
  ...
}
```

Or use the GUI:
1. Open your application
2. Go to the "Shopify API Settings" section
3. Enter:
   - **Shop Domain:** `your-shop.myshopify.com`
   - **Access Token:** `shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **API Version:** `2025-10`
4. Click **"Save"**

## Security Best Practices

1. **Never commit tokens to Git**
   - Add `config.json` to `.gitignore` if it contains real credentials
   - Use environment variables for production

2. **Token Storage**
   - Keep your access token secure
   - Don't share it publicly
   - If compromised, regenerate it in the Shopify admin

3. **Scope Limitation**
   - Only request the scopes you need
   - Don't request `write_*` scopes unless necessary

## Troubleshooting

### "I have a token starting with `shpss_`"
- **This is a Storefront API token, not an Admin API token**
- You need to get the **Admin API access token** instead
- Follow steps 4-6 in Method 1 above to get the correct token
- Look specifically for **"Admin API access token"** (not Storefront API)

### "Invalid API key or access token"
- Verify the access token is correct (must start with `shpat_`)
- Make sure you copied the entire token
- Check that the app is installed on your store
- If your token starts with `shpss_`, you have the wrong type of token

### "Access denied" or "Insufficient permissions"
- Verify the app has the required scopes enabled
- Reinstall the app if you changed scopes
- Check that you're using the correct access token

### "Shop not found"
- Verify the shop domain is correct
- Make sure it's in the format: `your-shop.myshopify.com`
- Don't include `https://` or trailing slashes

### "Rate limit exceeded"
- You're making too many requests too quickly
- Implement rate limiting in your code
- Use bulk operations for large data sets

## Testing Your Connection

After adding credentials, test the connection:

1. Open your application
2. Set a date range (e.g., last 30 days)
3. Click **"Fetch Orders"**
4. If successful, you should see orders from your Shopify store
5. If there's an error, check the error message and refer to troubleshooting above

## Next Steps

Once you have your credentials set up:
1. Add them to your `config.json` or through the GUI
2. Test fetching orders with a small date range
3. Verify the data matches what you see in Shopify admin
4. Proceed with categorization and export features

## Resources

- [Shopify Custom Apps Documentation](https://shopify.dev/docs/apps/tools/cli/getting-started)
- [Admin API Authentication](https://shopify.dev/docs/apps/auth/admin-app-access-tokens)
- [API Scopes Reference](https://shopify.dev/docs/api/usage/access-scopes)
- [Shopify Partners Dashboard](https://partners.shopify.com)

