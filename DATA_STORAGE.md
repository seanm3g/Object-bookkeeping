# Data Storage Guide

## Where Your Data is Stored

Your rules and credentials are stored in **different locations** depending on whether you're running locally or on a server:

### 1. Database (When Logged In) ✅ **RECOMMENDED**

**Location**: Depends on environment:
- **Local Development**: `instance/app.db` (SQLite database file)
- **Production/Server**: PostgreSQL database (provided by hosting platform)

**When used**: When you are **logged in** to the application

**What's stored**:
- Your user account (username, email, password hash)
- Shopify credentials (shop domain, access token, API version)
- Export path settings
- Google Sheets OAuth tokens and spreadsheet ID
- **All your product rules**

**Persistence**: 
- ✅ **Local (SQLite)**: Persists across sessions - Your data is saved permanently in `instance/app.db`
- ✅ **Server (PostgreSQL)**: Persists permanently - Data is stored in a managed database service

**How to verify**:
```bash
# Local: Check if database exists
ls -la instance/app.db

# Server: Check hosting platform's database dashboard
# Most platforms (Render, Railway, Heroku) provide a database dashboard
```

**Important Notes**:
- **On servers**: Most hosting platforms automatically provide a `DATABASE_URL` environment variable pointing to PostgreSQL
- **PostgreSQL is persistent**: Data is stored in a managed database service and persists across app restarts
- **SQLite on servers**: Not recommended - file system may be ephemeral (data can be lost on restart)

### 2. JSON File (Fallback - Not Recommended)

**Location**: `config.json` (in the project root)

**When used**: Only as a fallback if you're **not logged in** (legacy support)

**What's stored**:
- Shopify credentials
- Export path
- Product rules (if using old version)

**Persistence**: ⚠️ **May not persist properly** - This is a legacy fallback

## Why Your Data Might Not Be Saving

### Issue 1: Database Not Created

**Problem**: The database file (`instance/app.db`) doesn't exist, so accounts and data can't be saved.

**Solution**: 
1. Run the diagnostic script to check: `python3 check_database.py`
2. The database is created automatically when you first run the app
3. Make sure you're running the app from the project directory: `python app.py`
4. If running from a different location, the database might be created in the wrong place

**Check if database exists**:
```bash
ls -la instance/app.db
```

### Issue 2: Not Logged In

**Problem**: If you're not logged in, the app tries to use the JSON fallback, but rules require login to save.

**Solution**: 
1. Make sure you're logged in (check the top navigation bar - it should show your username)
2. If you see "Login" instead of your username, click it and log in
3. If you don't have an account, click "Register" to create one
4. **Important**: After registering, verify your account was saved by running `python3 check_database.py`

### Issue 3: Running from Wrong Directory

**Problem**: If you run the app from a different directory, the database might be created in the wrong location.

**Solution**:
1. Always run the app from the project root directory: `cd /Users/seangreen/code/Object-bookkeeping && python app.py`
2. Check where the database is being created by running `python3 check_database.py`
3. The database should be at: `/Users/seangreen/code/Object-bookkeeping/instance/app.db`

### Issue 4: Different User Account

**Problem**: You might be logged in as a different user than when you saved the data.

**Solution**:
1. Check which username is shown in the top navigation
2. Make sure you're using the same account you used when saving
3. Each user has their own isolated data

### Issue 5: Database File Deleted

**Problem**: The `instance/` directory or `instance/app.db` file was deleted.

**Solution**:
1. The database will be recreated when you run the app again
2. **WARNING**: If the database is deleted, all user accounts and data are lost
3. You'll need to register again and recreate your rules
4. Run `python3 check_database.py` to verify the database exists

## How to Check Your Data

### Quick Diagnostic Check

Run the diagnostic script to see the status of your database:

```bash
cd /Users/seangreen/code/Object-bookkeeping
python3 check_database.py
```

This will show you:
- Where the database should be located
- Whether the database file exists
- How many users are in the database
- List of all registered users

### Manual Check if Database Exists

```bash
cd /Users/seangreen/code/Object-bookkeeping
ls -la instance/app.db
```

If the file exists, your data is stored there. If you get "No such file or directory", the database hasn't been created yet.

### Check if You're Logged In

1. Open the app in your browser
2. Look at the top navigation bar
3. If you see your username (e.g., "Logged in as: yourname"), you're logged in
4. If you see "Login", you're not logged in

### Verify Data is Saved

1. **Save your configuration**:
   - Enter your Shopify credentials
   - Click "Save Configuration"
   - You should see "Configuration saved!" alert

2. **Add a rule**:
   - Create a product rule
   - Click "Add Rule"
   - You should see "Rule added!" alert

3. **Reload the page**:
   - Press F5 or refresh the browser
   - Your credentials and rules should still be there

4. **Restart the app**:
   - Stop the app (Ctrl+C)
   - Start it again (`python app.py`)
   - Log in with the same account
   - Your data should still be there

## Troubleshooting

### "I registered an account but it's gone after restarting"

**This is the most common issue!**

**Check**:
1. Run `python3 check_database.py` to see if the database exists
2. If the database doesn't exist, it means:
   - The app wasn't run from the correct directory, OR
   - The database wasn't created properly, OR
   - The database was deleted

**Solution**: 
1. Make sure you're running the app from the project root: `cd /Users/seangreen/code/Object-bookkeeping && python app.py`
2. Register your account again
3. After registering, run `python3 check_database.py` to verify your account was saved
4. If the account still doesn't persist, check the terminal output for any database errors

### "I saved my data but it's gone after restarting"

**Check**:
1. Are you logged in? (Check top navigation)
2. Are you using the same user account?
3. Does `instance/app.db` exist? (Run `python3 check_database.py`)

**Solution**: Make sure you're logged in before saving data. The database persists your data permanently.

### "I see my credentials but not my rules"

**Check**:
1. Are you logged in?
2. Did you click "Add Rule" after creating the rule?
3. Did you see a success message?

**Solution**: Rules are saved separately from credentials. Make sure you click "Add Rule" to save each rule.

### "The database file doesn't exist"

**This is normal** if:
- You haven't run the app yet
- You just installed the app

**The database will be created**:
- Automatically when you first run the app
- When you first register a user account
- When you first save configuration

### "I want to reset everything"

**To reset all data**:
```bash
# Stop the app first (Ctrl+C)
rm -rf instance/
python app.py  # Will create fresh database
```

**WARNING**: This deletes ALL users, accounts, and data. You'll need to register again.

## Best Practices

1. **Always log in** before using the app
2. **Use the same account** each time
3. **Verify data persists** by refreshing the page after saving
4. **Back up the database** if you have important data:
   ```bash
   cp instance/app.db instance/app.db.backup
   ```

## Database Location Details

### Local Development
- **File**: `instance/app.db`
- **Type**: SQLite database
- **Created**: Automatically on first run
- **Location**: Inside the project directory, in an `instance/` subdirectory
- **Backup**: Copy the `instance/app.db` file to back up your data

### Production/Server
- **Type**: PostgreSQL (recommended) or SQLite
- **Location**: Managed database service provided by hosting platform
- **Configuration**: Set via `DATABASE_URL` environment variable
- **Persistence**: ✅ **Data persists permanently** - Managed databases don't lose data on restart
- **Backup**: Most hosting platforms provide automatic backups

**How it works on servers**:
1. Hosting platforms (Render, Railway, Heroku, etc.) automatically provide a `DATABASE_URL`
2. The app detects this and uses PostgreSQL instead of SQLite
3. Your data is stored in a persistent, managed database
4. Data survives app restarts, deployments, and server reboots

## Migration from JSON to Database

If you have data in `config.json` and want to migrate to the database:

1. **Log in** to the app (or register if you don't have an account)
2. **Manually enter** your Shopify credentials in the Configuration section
3. **Manually recreate** your rules in the Product Rules section
4. The data will be saved to the database automatically

The app will continue to work with `config.json` as a fallback, but for proper persistence, use the database (by logging in).

## Server vs Local: Key Differences

### On a Server (Production)
- ✅ **PostgreSQL database** (provided by hosting platform)
- ✅ **Data persists permanently** - Managed database service
- ✅ **Survives restarts** - Database is separate from app
- ✅ **Automatic backups** - Most platforms provide this
- ✅ **Multiple users** - PostgreSQL handles concurrent access well

### Local Development
- ✅ **SQLite database** (`instance/app.db`)
- ✅ **Data persists** - File on your local disk
- ⚠️ **Single user** - SQLite works best for one user at a time
- ⚠️ **Manual backups** - You need to copy the file yourself

**Bottom line**: On servers, your data is stored in a persistent PostgreSQL database that survives restarts and deployments. The database is managed by your hosting platform and data is safe.

