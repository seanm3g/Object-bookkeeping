"""
Build script to create a standalone executable using PyInstaller.
This packages the entire application into a single executable file that
can run without Python installed.
"""

import PyInstaller.__main__
import os
import sys

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller arguments
args = [
    'app.py',                    # Main script
    '--name=ShopifyOrderApp',    # Name of the executable
    '--onefile',                 # Create a single executable file
    '--add-data=config.example.json:.',  # Include example config
    '--hidden-import=flask',     # Ensure Flask is included
    '--hidden-import=werkzeug',  # Flask dependency
    '--hidden-import=jinja2',    # Flask dependency
    '--hidden-import=requests',  # For Shopify API
    '--hidden-import=openpyxl',  # For Excel/Google Sheets export
    '--collect-all=flask',       # Collect all Flask data files
    '--clean',                   # Clean PyInstaller cache before building
]

# Platform-specific adjustments
if sys.platform == 'darwin':  # macOS
    # On macOS, --windowed creates a .app bundle without console
    # For cleaner user experience, we'll keep console visible to show status
    # To hide console, uncomment the next line:
    # args.append('--windowed')  # Creates .app bundle without console
    pass
elif sys.platform == 'win32':  # Windows
    args.append('--noconsole')  # Hide console on Windows
    # Windows-specific icon (if you have one)
    # args.append('--icon=icon.ico')

print("Building standalone executable...")
print("This may take a few minutes...")
print(f"Working directory: {script_dir}")
print(f"PyInstaller args: {args}\n")

# Change to script directory
os.chdir(script_dir)

# Run PyInstaller
PyInstaller.__main__.run(args)

print("\n" + "="*60)
print("Build complete!")
print("="*60)
if sys.platform == 'darwin':
    print(f"\nExecutable location: {script_dir}/dist/ShopifyOrderApp")
    print("You can distribute this executable to other Mac users.")
    print("Note: On macOS, you may want to create a .app bundle for better integration.")
    print("To create a .app bundle, add --windowed to the PyInstaller args.")
elif sys.platform == 'win32':
    print(f"\nExecutable location: {script_dir}/dist/ShopifyOrderApp.exe")
    print("You can distribute the .exe file to other Windows users.")
else:
    print(f"\nExecutable location: {script_dir}/dist/ShopifyOrderApp")
    print("You can distribute this executable to other users.")
print("\nNote: The first time the executable runs, it may take a moment to extract.")
print("Subsequent runs will be faster.")

