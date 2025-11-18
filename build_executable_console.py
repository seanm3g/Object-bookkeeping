"""
Build script to create a standalone executable WITH console window.
Use this version if you want to see console output for debugging.
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
    # NO --windowed or --noconsole - keep console visible
    '--add-data=config.example.json:.',  # Include example config
    '--hidden-import=flask',     # Ensure Flask is included
    '--hidden-import=werkzeug',  # Flask dependency
    '--hidden-import=jinja2',    # Flask dependency
    '--hidden-import=requests',  # For Shopify API
    '--hidden-import=openpyxl',  # For Excel/Google Sheets export
    '--collect-all=flask',       # Collect all Flask data files
    '--clean',                   # Clean PyInstaller cache before building
]

print("Building standalone executable (with console)...")
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
elif sys.platform == 'win32':
    print(f"\nExecutable location: {script_dir}/dist/ShopifyOrderApp.exe")
    print("You can distribute the .exe file to other Windows users.")
else:
    print(f"\nExecutable location: {script_dir}/dist/ShopifyOrderApp")
    print("You can distribute this executable to other users.")
print("\nNote: The first time the executable runs, it may take a moment to extract.")
print("Subsequent runs will be faster.")

