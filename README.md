# Shopify Order Categorization App

A web-based application for fetching Shopify orders, categorizing them based on product descriptions, and exporting financial breakdowns to CSV or Google Sheets.

## Features

- **Web Interface**: Easy-to-use browser-based interface (works on any platform)
- **Multi-User Authentication**: Username/password login system for hosted deployment
- **Product Rule Matching**: Define rules based on product description keywords
- **Financial Categorization**: Automatically splits order amounts into consignment, revenue, taxes, and financing
- **Quick Date Ranges**: One-click buttons for Last 30 Days, Last Month, Last Week, This Month to Date
- **CSV Export**: Export to CSV for easy import into Google Sheets
- **Google Sheets Integration**: Direct export to Google Sheets with monthly tabs (coming soon)
- **Real Shopify API Integration**: Fetches real orders from your Shopify store
- **Standalone Executable**: Available as a single-file executable (no Python installation required)
- **Hosted Deployment Ready**: Deploy to Render, Railway, Fly.io, or any platform (see [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md))

## Quick Start

### Option 1: Hosted Web Service (Recommended for Sharing)

Deploy this app to a hosting platform so users can access it via URL with their own accounts:

1. **See [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md)** for step-by-step deployment instructions
2. **Deploy to Render, Railway, or Fly.io** (all have free tiers)
3. **Share the URL** with users - they can register their own accounts
4. **Each user** configures their own Shopify API credentials and rules

### Option 2: Standalone Executable (Local Use)

**For End Users**: If you have received a standalone executable:

1. **Double-click the executable** (`.app` on Mac, `.exe` on Windows)
2. **The browser will open automatically** - no configuration needed!
3. **Register an account** (first-time setup)
4. **Start using the app** - configure your Shopify API credentials in the app

That's it! No Python, no installation, no command line needed.

---

## Installation (For Developers or Building Executables)

If you want to run from source code or build your own executable:

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python3 app.py
   ```
   
   The browser will open automatically at **http://127.0.0.1:5001**
   
   The app starts a local web server that you can access from any browser.

### Building a Standalone Executable

To create a standalone executable that doesn't require Python:

**⚠️ Important**: You must build on the target platform. A Mac-built executable won't run on Windows, and vice versa.

1. **Install PyInstaller** (if not already installed):
   ```bash
   pip install pyinstaller
   ```

2. **Run the build script**:
   ```bash
   # On Mac/Linux:
   python3 build_executable.py
   # On Windows:
   python build_executable.py
   ```

3. **Find your executable** in the `dist/` folder:
   - **macOS**: `dist/ShopifyOrderApp`
   - **Windows**: `dist/ShopifyOrderApp.exe`
   - **Linux**: `dist/ShopifyOrderApp`

**To build for multiple platforms**, you'll need to:
- Build on Mac to get a Mac executable
- Build on Windows to get a Windows executable
- Or use a Windows VM/CI/CD service

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for detailed build instructions, cross-platform building options, and troubleshooting.

## Usage

### First Time Setup

1. **Launch the application**:
   - **If using executable**: Just double-click it - the browser opens automatically
   - **If running from source**: Run `python3 app.py` - the browser opens automatically
   - **If using hosted version**: Navigate to your deployment URL
   
   The app will be available at **http://127.0.0.1:5001** (local) or your deployment URL

2. **Create an account** (first time only):
   - Click "Register" to create a new account
   - Enter username, email, and password
   - Click "Register" - you'll be automatically logged in

3. **Configure Shopify API**:
   - Go to the "Configuration" tab
   - Enter your Shopify shop domain (e.g., `myshop.myshopify.com`)
   - Enter your Shopify Admin API access token
   - Click "Save Configuration"
   - **Note**: For MVP testing, you can leave these empty to use dummy data

3. **Set up Product Rules**:
   - Go to the "Product Rules" tab
   - Click "Add Rule" to create categorization rules
   - Enter:
     - **Description**: A name for this rule (e.g., "Consignment items")
     - **Keywords**: Comma-separated keywords that match product descriptions (e.g., "consignment, consign")
     - **Percentages**: Set percentages for consignment, revenue, taxes, and financing
   - Click "OK" to save
   - Rules are matched using "first match wins" logic

### Fetching Orders

1. Go to the "Fetch Orders" tab
2. Select a date range:
   - **Option 1**: Use the quick date range buttons (Last 30 Days, Last Month, Last Week, This Month to Date)
   - **Option 2**: Manually enter dates in YYYY-MM-DD format (e.g., 2024-01-01)
3. Click "Fetch Orders"
4. Review the results displayed below

### Exporting Data

1. After fetching orders, go to the "Export" tab
2. Choose export method:
   - **Export to CSV**: Saves a CSV file that you can import into Google Sheets
   - **Export to Google Sheets**: Directly writes to Google Sheets (currently uses dummy data for MVP)

## Configuration File

The app uses `config.json` to store:
- Shopify API credentials
- Product categorization rules
- Google Sheets settings

You can edit this file directly or use the GUI. The file is automatically created on first run.

## Product Rules

Rules are matched based on product descriptions. The first rule that matches (by keyword) is applied to the entire order.

Example rule:
```json
{
  "id": 1,
  "keywords": ["consignment", "consign"],
  "description": "Consignment items",
  "consignment_percent": 50.0,
  "revenue_percent": 30.0,
  "taxes_percent": 10.0,
  "financing_percent": 10.0
}
```

## CSV Export Format

The CSV file includes the following columns:
- Order ID
- Order Number
- Date
- Customer
- Products
- Order Total
- Consignment
- Revenue
- Taxes
- Financing
- Matched Rules

## Google Sheets Integration (Future)

Google Sheets integration will be added in a future update. For now, use CSV export and import into Google Sheets manually.

## Troubleshooting

### App won't start
- Make sure Python 3.7+ is installed: `python3 --version`
- Install dependencies: `pip3 install -r requirements.txt` or `python3 -m pip install -r requirements.txt`
- If port 5001 is in use, the app will fail to start. Check for other processes using that port.

### Connection refused
- Make sure the Flask server is running (you should see "Starting web server..." in the terminal)
- Check that you're using the correct URL: **http://127.0.0.1:5001**
- If you see "ModuleNotFoundError", run `pip3 install -r requirements.txt` to install dependencies

### No orders fetched
- Check your date range format (YYYY-MM-DD)
- Verify your Shopify API credentials are correct in the Configuration section
- Make sure your access token has the `read_orders` scope enabled
- Verify date range is valid (start date before end date)
- Check the error message for specific API issues

### Rules not matching
- Check that keywords match product descriptions (case-insensitive)
- Remember: first matching rule wins
- Keywords are matched as substrings (e.g., "consign" matches "Consignment Art Piece")

## Development Notes

### Current Status
- ✅ Real Shopify API integration (GraphQL Admin API)
- ✅ Quick date range buttons
- ⏳ Google Sheets export uses mock/dummy implementation

### Future Enhancements
- Real Google Sheets API integration
- Per-line-item calculations (currently applies rule to entire order)
- Rule priority/ordering
- Import/export of rules
- Historical data tracking

## Support

For issues or questions, please refer to the codebase or create an issue in the repository.

