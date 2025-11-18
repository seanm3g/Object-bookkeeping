# Rebuild Instructions

## When to Rebuild

Rebuild the executable after making changes to:
- ✅ Python source files (`app.py`, `rule_engine.py`, `exporter.py`, `shopify_client.py`)
- ✅ Dependencies (`requirements.txt`)
- ✅ Build configuration

**You do NOT need to rebuild for:**
- ❌ Changes to `config.json` (read at runtime)
- ❌ Documentation files
- ❌ README or other markdown files

## Step-by-Step Rebuild Process

### Step 1: Navigate to Project Directory

Open Terminal and go to your project folder:

```bash
cd /Users/seangreen/code/Object-bookkeeping
```

### Step 2: Verify You're in the Right Place

Make sure you can see the build script:

```bash
ls build_executable.py
```

You should see: `build_executable.py`

### Step 3: Run the Build Script

Execute the build command:

```bash
python3 build_executable.py
```

### Step 4: Wait for Build to Complete

The build process takes 2-5 minutes. You'll see output like:
```
Building standalone executable...
This may take a few minutes...
...
Build complete!
```

### Step 5: Verify the New Executable

Check that the executable was created:

```bash
ls -lh dist/ShopifyOrderApp
```

You should see the executable file with a recent timestamp.

### Step 6: Test the New Executable (Optional)

Test that it works:

```bash
./dist/ShopifyOrderApp
```

The browser should open automatically. Press `Ctrl+C` to stop it.

## Quick Rebuild Command (All-in-One)

If you're already in the project directory, just run:

```bash
python3 build_executable.py
```

## Troubleshooting

### Build Fails with "ModuleNotFoundError"

Install missing dependencies:

```bash
pip3 install -r requirements.txt
```

### Build Fails with "PyInstaller not found"

Install PyInstaller:

```bash
pip3 install pyinstaller
```

### Executable Doesn't Work After Rebuild

1. Make sure you stopped any running instances
2. Delete the old executable: `rm dist/ShopifyOrderApp`
3. Rebuild again: `python3 build_executable.py`

### Port 5001 Already in Use

If you see an error about port 5001:
1. Stop any running instances of the app
2. Or kill the process: `lsof -ti:5001 | xargs kill`

## File Locations

- **Source code**: `/Users/seangreen/code/Object-bookkeeping/`
- **Build script**: `build_executable.py`
- **Built executable**: `dist/ShopifyOrderApp`
- **Temporary build files**: `build/` (can be deleted)

## Distribution

After rebuilding, the new executable is ready to distribute:
- **Location**: `dist/ShopifyOrderApp`
- **Size**: ~5-6 MB
- **Platform**: macOS (built on Mac)

To distribute to Windows users, you'll need to build on a Windows machine.

## Notes

- The build process creates a new executable that includes all your latest code
- Old executables are automatically replaced
- The first time the new executable runs, it may take a moment to extract
- Subsequent runs will be faster

