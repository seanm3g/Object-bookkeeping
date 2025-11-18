# Building Standalone Executable

This guide explains how to create a standalone executable that can run without Python installed. The executable will automatically open your browser when launched.

## Prerequisites

1. **Python 3.7+** installed on your development machine
2. **All dependencies** installed (run `pip install -r requirements.txt`)

## Quick Build

### Option 1: Build with Hidden Console (Recommended for End Users)

This creates an executable that runs without showing a console window:

```bash
python3 build_executable.py
```

### Option 2: Build with Visible Console (For Debugging)

This creates an executable that shows console output (useful for troubleshooting):

```bash
python3 build_executable_console.py
```

## Build Process

**⚠️ Important: Platform-Specific Builds**

PyInstaller creates platform-specific executables. You must build on the target platform:
- **Mac executable** → Build on Mac
- **Windows executable** → Build on Windows
- **Linux executable** → Build on Linux

You cannot run a Mac-built executable on Windows, or vice versa.

### Building on Your Platform

1. **Install PyInstaller** (if not already installed):
   ```bash
   # On Mac/Linux:
   pip install pyinstaller
   # On Windows:
   pip install pyinstaller
   ```
   Or install all requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the build script**:
   ```bash
   # On Mac/Linux:
   python3 build_executable.py
   # On Windows:
   python build_executable.py
   ```

3. **Wait for completion** - The build process may take 2-5 minutes depending on your system.

4. **Find your executable**:
   - **macOS**: `dist/ShopifyOrderApp` (or `dist/ShopifyOrderApp.app` if using --windowed)
   - **Windows**: `dist/ShopifyOrderApp.exe`
   - **Linux**: `dist/ShopifyOrderApp`

## Distribution

### For macOS

1. The build creates a `.app` bundle (or standalone executable)
2. You can distribute the entire `dist/ShopifyOrderApp.app` folder
3. Users can double-click the `.app` to launch
4. **Note**: macOS may show a security warning on first launch. Users need to:
   - Right-click the app → Open
   - Or go to System Preferences → Security & Privacy → Allow

### For Windows

1. The build creates `ShopifyOrderApp.exe`
2. You can distribute just the `.exe` file
3. Users can double-click to launch
4. **Note**: Windows Defender may flag it initially. You may need to:
   - Sign the executable with a code signing certificate (for production)
   - Or users can click "More info" → "Run anyway" on first launch

### For Linux

1. The build creates a standalone executable
2. Make it executable: `chmod +x dist/ShopifyOrderApp`
3. Users can run it directly: `./ShopifyOrderApp`

## What Gets Included

The executable bundles:
- Python interpreter
- Flask and all web dependencies
- Shopify API client
- Rule engine
- CSV exporter
- All required libraries

**What's NOT included** (created on first run):
- `config.json` - Created automatically when the app first runs
- User's Shopify API credentials
- Product rules (user configures these in the app)

## Testing the Executable

1. **Test on the build machine first**:
   - Navigate to the `dist` folder
   - Run the executable
   - Verify the browser opens automatically
   - Test basic functionality

2. **Test on a clean machine** (without Python):
   - Copy the executable to a machine without Python
   - Run it
   - Verify it works

## Troubleshooting

### Build Fails

- **Missing dependencies**: Run `pip install -r requirements.txt`
- **PyInstaller not found**: Run `pip install pyinstaller`
- **Import errors**: Check that all modules are properly imported in `app.py`

### Executable Won't Run

- **macOS**: Check System Preferences → Security & Privacy
- **Windows**: Check Windows Defender settings
- **Port 5001 in use**: Close other applications using port 5001
- **Firewall blocking**: Allow the application through your firewall

### Browser Doesn't Open

- The executable should open the browser automatically
- If it doesn't, manually navigate to: `http://127.0.0.1:5001`
- Check the console output (if using console version) for errors

### Large File Size

- The executable includes Python and all dependencies, so it will be 50-100MB
- This is normal for PyInstaller one-file builds
- The first launch extracts files to a temp directory (may take a moment)

## Building for Multiple Platforms

To distribute to both Mac and Windows users, you have several options:

### Option 1: Build on Each Platform (Recommended)

1. **Build on Mac**: Run `python3 build_executable.py` → Get `ShopifyOrderApp` (Mac)
2. **Build on Windows**: Run `python build_executable.py` → Get `ShopifyOrderApp.exe` (Windows)
3. **Distribute both** executables to users

### Option 2: Use a Windows VM or Remote Machine

If you only have a Mac:
1. Set up a Windows virtual machine (VMware, Parallels, VirtualBox)
2. Install Python and dependencies on Windows VM
3. Copy your project files to the VM
4. Build the Windows executable there

### Option 3: Use CI/CD (GitHub Actions, etc.)

Set up automated builds that create executables for multiple platforms:
- GitHub Actions can build on Mac, Windows, and Linux runners
- Each build produces a platform-specific executable
- All executables are available for download

### Option 4: Ask a Windows User to Build

If you have access to a Windows machine or know someone with one:
1. Share your project files (or GitHub repo)
2. Have them run `python build_executable.py` on Windows
3. They'll get a Windows `.exe` file you can distribute

## Advanced Options

### Custom Icon

To add a custom icon:

1. Create or obtain an icon file:
   - **macOS**: `.icns` format
   - **Windows**: `.ico` format

2. Modify `build_executable.py`:
   ```python
   args.append('--icon=path/to/icon.ico')  # Windows
   args.append('--icon=path/to/icon.icns')  # macOS
   ```

### Smaller Executable (Directory Mode)

Instead of `--onefile`, use directory mode for faster startup:

1. Remove `--onefile` from the build script
2. This creates a folder with the executable and dependencies
3. Distribute the entire folder

### Code Signing (Production)

For production distribution, especially on macOS and Windows, you should code sign the executable:

- **macOS**: Requires Apple Developer account and certificate
- **Windows**: Requires code signing certificate

## File Structure After Build

```
Object-bookkeeping/
├── dist/                    # Built executables go here
│   └── ShopifyOrderApp      # Your executable
├── build/                   # Temporary build files (can be deleted)
├── ShopifyOrderApp.spec     # PyInstaller spec file (auto-generated)
└── ...
```

You can delete the `build/` folder and `.spec` file after building - they're just temporary files.

