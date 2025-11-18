# Shopify Order Categorization App

## Product Description

This application helps manage and categorize Shopify orders for financial bookkeeping. It pulls orders from the Shopify API and automatically categorizes portions of each order's amount into different financial categories (consignment, revenue, taxes, financing) based on product descriptions.

## Features

### Core Functionality
- **Order Fetching**: Retrieves orders from Shopify API within a specified date range
- **Product Rule Matching**: Matches product descriptions to user-defined rules using keyword/phrase matching
- **Financial Categorization**: Automatically calculates and splits order amounts into:
  - Consignment
  - Revenue
  - Taxes[  ]
  - Financing
- **Export Options**: 
  - CSV export for easy import into Google Sheets
  - Direct Google Sheets integration (optional) with monthly tab organization

### User Interface
- Simple desktop GUI built with tkinter (cross-platform: Mac and PC)
- Product rule management interface to add/edit categorization rules
- Date range picker for selecting which orders to fetch
- One-click export to CSV or Google Sheets

### Configuration
- JSON-based configuration file for:
  - Shopify API credentials
  - Product categorization rules (keywords/phrases → percentages)
- All configuration manageable through the GUI

## Technical Details

### Rule Matching Logic
- First matching rule wins (stops after first match)
- Rules match based on product description keywords/phrases
- Each rule defines percentages for: consignment, revenue, taxes, financing
- Percentages apply to order subtotal

### Export Format
- Each row represents one order
- Columns include: Order ID, Date, Customer, Products, Order Total, Consignment, Revenue, Taxes, Financing
- Google Sheets export organizes orders by month in separate tabs
- CSV export includes date column for filtering/sorting in Google Sheets

## MVP Scope

This is a minimal viable product focused on simplicity and ease of use:
- Desktop GUI application (no web server required)
- Dummy data for API testing (real APIs to be integrated later)
- CSV export as primary method (simplest for end users)
- Google Sheets API integration as optional feature
- No authentication flows (manual API token entry)
- No database (JSON config only)
- Comprehensive setup instructions included

