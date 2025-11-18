# Recommended Component Sequence

## Standard Recommended Order

**Important:** Investor and Consigner are **mutually exclusive** - they never appear in the same deal. Each deal will have either an Investor OR a Consigner, but never both.

### Option 1: Expenses First, Then Taxes (Most Common)

**Recommended Order:**
1. **Investor** OR **Consigner** (mutually exclusive - only one per deal)
2. **State Taxes** (calculated simultaneously with Federal)
3. **Federal Taxes** (calculated simultaneously with State)
4. **Revenue** (automatic - whatever remains)

**Why this order?**
- Taxes are typically calculated on **net income** (after business expenses)
- This matches standard accounting: Revenue → Expenses → Taxes → Net Profit
- Investor or Consigner payments are business expenses that reduce taxable income
- Since they're mutually exclusive, the order between them doesn't matter

**Example 1 - Deal with Investor:**
- Order: $100
- Investor: 20% → $20 (from $100)
- State Taxes: 5% → $4.00 (from $80 base, calculated simultaneously)
- Federal Taxes: 3% → $2.40 (from $80 base, calculated simultaneously)
- Revenue: $73.60 (remaining)

**Example 2 - Deal with Consigner:**
- Order: $100
- Consigner: 50% → $50 (from $100)
- State Taxes: 5% → $2.50 (from $50 base, calculated simultaneously)
- Federal Taxes: 3% → $1.50 (from $50 base, calculated simultaneously)
- Revenue: $46.00 (remaining)

### Option 2: Taxes First (Less Common)

**Order:**
1. **State Taxes** (calculated simultaneously with Federal)
2. **Federal Taxes** (calculated simultaneously with State)
3. **Investor** OR **Consigner** (mutually exclusive - only one per deal)
4. **Revenue** (automatic)

**When to use:**
- If taxes are calculated on **gross revenue** (before expenses)
- If you need to pay taxes first, then distribute remaining funds
- Less common in standard accounting

**Example - Deal with Investor:**
- Order: $100
- State Taxes: 5% → $5.00 (from $100 base)
- Federal Taxes: 3% → $3.00 (from $100 base)
- Investor: 20% → $18.40 (from $92 remaining)
- Revenue: $73.60 (remaining)

## Current Configuration Analysis

Looking at your current rules, you have different orders:

### Rule 1: "Candles"
- Consigner (1) → Investor (2) → State Taxes (3) → Federal Taxes (4)
- **This is Option 1** ✅ (Expenses first, then taxes)

### Rule 2: "Bunny consignment"
- Investor (1) → Consigner (2) → State Taxes (3) → Federal Taxes (4)
- **This is Option 1** ✅ (Expenses first, then taxes)

### Rule 3: "Dan's records"
- Consigner (1) → State Taxes (2) → Federal Taxes (3)
- **This is Option 1** ✅ (Expenses first, then taxes)

### Rule 4: "Desert Flower Milk Bath"
- Investor (1) → Consigner (2) → State Taxes (3) → Federal Taxes (4)
- **This is Option 1** ✅ (Expenses first, then taxes)

## Recommendations

### For Your Business Model

Based on your rules, **Option 1 (Expenses First, Then Taxes)** appears to be what you're using. This is the standard approach.

**Recommended Standard Order:**
1. **Investor** (if you have investors)
2. **Consigner** (if consignment items)
3. **State Taxes** (always together with Federal)
4. **Federal Taxes** (always together with State)
5. **Revenue** (automatic)

### Key Considerations

1. **Investor vs Consigner:**
   - These are **mutually exclusive** - never both in the same deal
   - Order between them doesn't matter since they never appear together
   - Each rule should have either Investor OR Consigner, not both

2. **Tax Base:**
   - With current setup, taxes are calculated on amount **after** Investor/Consigner
   - This means taxes are on **net income** (standard accounting)
   - If you want taxes on **gross**, put taxes first

3. **Consistency:**
   - Use the same order pattern across all rules for consistency
   - Recommended: [Investor OR Consigner] → State Taxes → Federal Taxes
   - Makes it easier to understand and audit

## How to Change Order

1. Go to the "Product Rules" tab in the app
2. Click "Edit" on any rule
3. Use the ↑/↓ buttons to reorder components
4. Click "Update Rule"

**Remember:** 
- Tax components (State Taxes, Federal Taxes) will always be calculated simultaneously from the same base
- The order of taxes relative to each other doesn't matter (they're simultaneous)
- The order of non-tax components DOES matter (they're sequential)

## Questions to Consider

1. **Are taxes calculated on gross or net?**
   - Gross = Taxes first
   - Net = Expenses first (current setup - recommended)

2. **Standard order for all rules?**
   - Recommended: [Investor OR Consigner] → State Taxes → Federal Taxes
   - Since Investor and Consigner are mutually exclusive, this works for all deals

3. **Do you want consistency across all rules?**
   - Same order pattern for all products is recommended
   - Makes it easier to understand and audit

