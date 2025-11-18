# Product Metadata Update

## Overview

The application has been updated to fetch and use product metadata from Shopify, including:
- **Vendor** (e.g., "Monsoon Chocolate")
- **Product Type** (e.g., "Art", "Furniture")
- **Tags** (e.g., "Consignment", "Inventory")
- **Collections** (e.g., "Art Collection", "Furniture")

## What Changed

### 1. GraphQL Query Updates
- Updated both GraphQL queries (with and without cost data) to fetch product metadata
- Now retrieves: `vendor`, `productType`, `tags`, and `collections` for each line item

### 2. Rule Matching Enhancement
- **Before**: Rules only matched against product title/name
- **After**: Rules now match against:
  - Product title/name
  - Vendor
  - Product type
  - Tags (all tags)
  - Collections (all collections)

### 3. Export Updates
- **CSV Export**: Added columns for Vendor, Product Type, Tags, and Collections
- **Google Sheets Export**: Same columns added
- All exports now include this metadata for better filtering and analysis

### 4. UI Updates
- Order results now display vendor, product type, tags, and collections
- Shown in a smaller gray text below the product names

## How to Use

### Creating Rules with Metadata

You can now create rules that match based on vendor, tags, or collections:

**Example 1: Match by Vendor**
- Description: "Monsoon Chocolate Products"
- Keywords: `Monsoon Chocolate`
- This will match all products from the "Monsoon Chocolate" vendor

**Example 2: Match by Tag**
- Description: "Inventory Items"
- Keywords: `Inventory`
- This will match all products with the "Inventory" tag

**Example 3: Match by Collection**
- Description: "Art Collection Items"
- Keywords: `Art Collection`
- This will match all products in the "Art Collection" collection

**Example 4: Match by Product Type**
- Description: "Furniture Items"
- Keywords: `Furniture`
- This will match all products with product type "Furniture"

### Multiple Keywords

You can still use multiple keywords (comma-separated), and the rule will match if ANY keyword matches ANY of the searchable fields:

- Keywords: `Monsoon Chocolate, Consignment, Art`
- Will match products that have:
  - Vendor = "Monsoon Chocolate", OR
  - Tag = "Consignment", OR
  - Collection = "Art", OR
  - Product type = "Art", OR
  - Title contains any of these keywords

## API Requirements

To use this feature, your Shopify API access token needs the `read_products` scope. This is required to access product metadata.

If you get errors about missing product data:
1. Check that your app has the `read_products` scope enabled
2. Reinstall your Shopify app to grant the new permissions
3. Update your access token

## Export Format

The CSV and Google Sheets exports now include these columns (in order):
1. Order ID
2. Order Number
3. Date
4. Customer
5. Products
6. **Vendor** (new)
7. **Product Type** (new)
8. **Tags** (new)
9. **Collections** (new)
10. Order Total
11. Total Cost
12. Revenue
13. State Taxes
14. Federal Taxes
15. Investor columns (if any)
16. Consigner columns (if any)
17. Component Breakdown
18. Matched Rules

## Notes

- If an order has multiple products with different vendors/tags/collections, they are combined with commas
- Empty fields are left blank in exports
- The matching is case-insensitive
- Matching uses substring matching (e.g., "Monsoon" will match "Monsoon Chocolate")

## Testing

The dummy data generator has been updated to include sample metadata, so you can test the feature even without real Shopify data.

