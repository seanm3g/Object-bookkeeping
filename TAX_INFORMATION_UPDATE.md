# Tax Information Update

## Overview

The application now fetches and displays detailed tax information from Shopify orders, including tax breakdowns with rates and amounts.

## What Was Added

### 1. GraphQL Query Updates
- Added `taxLines` field to both GraphQL queries (with and without cost data)
- Fetches:
  - Tax title/name (e.g., "State Tax", "GST", "PST")
  - Tax amount
  - Tax rate (decimal)
  - Tax rate percentage

### 2. Data Processing
- Extracts tax lines from each order
- Formats tax information with rates displayed as percentages
- Stores both formatted display strings and raw tax data

### 3. Export Updates
- **CSV Export**: 
  - Adds a column for each unique tax type found across all orders
  - Columns named: "Shopify Tax - {Tax Type}" (e.g., "Shopify Tax - State Tax")
  - Includes "Shopify Tax Breakdown" column with formatted tax information
  - Tax amounts are included in totals row

- **Google Sheets Export**: 
  - Same columns as CSV
  - Tax amounts properly formatted and included in totals

### 4. UI Updates
- Order results now display Shopify tax breakdown
- Shown in blue text below the order total
- Format: "Shopify Taxes: Tax Name (Rate%): $Amount | ..."

## Tax Information Structure

Each order can have multiple tax lines, for example:
- State Tax (8.5%): $8.50
- County Tax (1.0%): $1.00
- GST (5.0%): $5.00
- PST (7.0%): $7.00

The application dynamically creates columns for each unique tax type found across all orders in the export.

## Export Format

### New Columns in Exports

After the standard columns and before "Component Breakdown", you'll find:

1. **Shopify Tax - {Tax Type}** columns (one for each unique tax type)
   - Contains the tax amount for that specific tax type
   - Empty if the order doesn't have that tax type
   - Included in totals

2. **Shopify Tax Breakdown** column
   - Contains formatted string: "Tax Name (Rate%): $Amount | ..."
   - Useful for quick reference

### Example Export Columns

```
Order ID | Order Number | Date | Customer | Products | ... | 
Shopify Tax - State Tax | Shopify Tax - County Tax | Shopify Tax - GST | 
Shopify Tax Breakdown | Component Breakdown | Matched Rules
```

## Display in UI

In the order results, you'll see:
```
Order #1001 - 2024-01-15
Customer: John Doe
Products: Widget A
Total: $100.00 | Cost: $50.00
Shopify Taxes: State Tax (8.5%): $8.50 | County Tax (1.0%): $1.00
Revenue: $40.00 | Investor: $0.00 | State Taxes: $5.00 | ...
```

## Notes

- **Tax rates** are displayed as percentages (e.g., "8.5%")
- **Tax amounts** are in the order's currency
- If an order has no tax lines, the tax columns will be empty
- Different orders may have different tax types, and the export will include columns for all unique tax types found
- The "State Taxes" and "Federal Taxes" columns in your rule-based breakdown are separate from Shopify's actual tax breakdown - they represent your calculated allocations, not the actual taxes charged

## Use Cases

This feature is useful for:
- **Reconciliation**: Compare your calculated tax allocations with actual Shopify taxes
- **Reporting**: Export detailed tax information for accounting purposes
- **Analysis**: Understand which tax types are being charged and at what rates
- **Compliance**: Track tax amounts by type for tax reporting

## API Requirements

No additional API scopes are required - tax information is part of the order data that's already accessible with the `read_orders` scope.

