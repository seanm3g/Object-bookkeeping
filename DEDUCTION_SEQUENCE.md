# Deduction Sequence from Sale Price

This document outlines the exact sequence of operations that occur when calculating financial breakdowns from an order's sale price.

## Overview

The system processes deductions in a specific order, with each step working on the remaining amount from the previous step. This ensures accurate allocation and tax calculations.

## Sequence of Operations

### Step 1: Calculate Original Sale Price
```
Original Sale Price = Σ (Line Item Price × Quantity)
```
- Sum of all line item prices multiplied by their quantities
- This is the price BEFORE any refunds or discounts

### Step 2: Subtract Refunds (if any)
```
Sale Price After Refunds = Original Sale Price - Total Refunded
```
- For partially refunded orders, subtract the refunded amount
- Fully refunded orders are excluded entirely (skipped)
- Refunds are applied BEFORE discounts

### Step 3: Apply Discounts
```
Discounted Amount = Sale Price After Refunds - Total Discounts
```

Discounts are calculated and subtracted:
- **Percentage Discounts**: `Discount = Original Sale Price × (Percentage / 100)`
- **Fixed Amount Discounts**: `Discount = Fixed Amount` (from discount_applications)
- Multiple discounts are summed together
- Discounts are applied BEFORE any other deductions

### Step 4: Subtract Total Cost
```
Base Amount = Discounted Amount - Total Cost
```
- Total cost is the sum of all line item costs (from inventory)
- This gives us the base amount for allocation calculations

### Step 5: Apply Allocation Components (Sequential, in Rule Order)

If a matching rule is found, components are applied **sequentially** in the order specified by the rule's `order` field. Each component is calculated from the **remaining amount** after previous deductions.

```
Remaining Amount = Base Amount
```

For each component (in order):
- **Percentage Component**: `Amount = Remaining Amount × (Percentage / 100)`
- **Flat Amount Component**: `Amount = Fixed Value`
- **Then**: `Remaining Amount = Remaining Amount - Amount`

Component types applied:
1. **Investor** (if present in rule)
2. **Consigner** (if present in rule)
3. **Vendor** (if present in rule)
4. Components with labels are tracked separately (e.g., "Investor - Bank A", "Investor - Bank B")

**Note**: Tax components in rules are ignored here - taxes are calculated separately in Step 5.

### Step 6: Calculate Taxes (Sequential Application)

Taxes are calculated from Shopify's tax data and applied to the remaining amount after all allocation components.

```
Tax Amount = Remaining Amount × Tax Rate
Remaining Amount = Remaining Amount - Tax Amount
```

Tax calculation order:
1. **State Taxes** (first tax line from Shopify)
   - Calculated from remaining amount
   - Remaining amount is reduced
2. **Federal Taxes** (second tax line from Shopify, if present)
   - Calculated from remaining amount (after state taxes)
   - Remaining amount is reduced
3. **Additional Taxes** (any additional tax lines)
   - Added to state taxes
   - Remaining amount is reduced

**Note**: While state and federal taxes are conceptually separate tax types, they are applied sequentially (not in parallel) because each tax calculation uses the remaining amount after the previous tax was deducted.

### Step 7: Calculate Revenue
```
Revenue = Remaining Amount (after all deductions)
```
- Revenue is automatically calculated as whatever is left over
- This is the final amount after all deductions

## Visual Flow Diagram

```
┌─────────────────────────────────────┐
│  Original Sale Price                │
│  (Sum of line item prices × qty)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Subtract Refunds (if any)          │
│  • Partial refunds only             │
│  • Fully refunded orders skipped    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Subtract Discounts                 │
│  • Percentage discounts             │
│  • Fixed amount discounts           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Subtract Total Cost                │
│  (Inventory costs)                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Apply Allocation Components        │
│  (Sequential, in rule order)        │
│                                     │
│  1. Investor (if present)           │
│  2. Consigner (if present)          │
│  3. Vendor (if present)             │
│  ... (each reduces remaining)       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Calculate Taxes                    │
│  (Sequential application)           │
│                                     │
│  1. State Taxes                     │
│     (from remaining amount)         │
│  2. Federal Taxes                   │
│     (from remaining after state)    │
│  3. Additional Taxes                │
│     (if any)                        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Revenue                            │
│  (Remaining amount)                 │
└─────────────────────────────────────┘
```

## Example Calculation

Let's say we have:
- Original Sale Price: $100.00
- Discount (10%): $10.00
- Total Cost: $30.00
- Rule Components (in order):
  1. Consigner: 20% (percentage)
  2. Investor: $10.00 (flat)
- State Tax: 8%
- Federal Tax: 2%

**Calculation:**
1. Start: $100.00
2. After refund (if any): $100.00 - $0.00 = $100.00 (no refund in this example)
3. After discount: $100.00 - $10.00 = $90.00
4. After cost: $90.00 - $30.00 = $60.00
5. After consigner (20%): $60.00 - ($60.00 × 0.20) = $60.00 - $12.00 = $48.00
6. After investor (flat $10): $48.00 - $10.00 = $38.00
7. After state tax (8%): $38.00 - ($38.00 × 0.08) = $38.00 - $3.04 = $34.96
8. After federal tax (2%): $34.96 - ($34.96 × 0.02) = $34.96 - $0.70 = $34.26
9. **Revenue: $34.26**

## Important Notes

1. **Refunds are applied FIRST** - before discounts and all other deductions
2. **Fully refunded orders are excluded** - orders with `financial_status` of "REFUNDED" are skipped entirely
3. **Partially refunded orders are processed** - the refund amount is subtracted from the sale price
4. **Discounts are applied after refunds** - discounts are calculated on the sale price after refunds
5. **Components are sequential** - each uses the remaining amount from the previous step
6. **Taxes are sequential** - state tax is calculated first, then federal tax from the remaining amount
7. **Revenue is residual** - it's whatever remains after all deductions

## Special Cases

- **Fully refunded orders**: Skipped entirely (not processed)
- **Partially refunded orders**: Refund amount is subtracted from original sale price before discounts
- **No matching rule**: Revenue equals the base amount (after refunds, discounts, and cost)
- **No discounts**: Sale price after refunds is used directly
- **No taxes**: Revenue is calculated after allocation components only
- **Multiple discounts**: All discounts are summed before subtraction
- **Multiple components of same type**: Each is tracked separately with labels

