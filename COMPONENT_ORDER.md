# Component Calculation Order

## How Components Are Applied

Financial components are calculated in a **three-phase process**:
1. **Pre-tax components** are applied sequentially
2. **Tax components** (State Taxes, Federal Taxes) are calculated **simultaneously** from the same base amount
3. **Post-tax components** are applied sequentially

Each component can be either a **flat amount** or a **percentage**. The order matters for non-tax components, but all tax components are calculated from the same base amount at the same time.

**Revenue** is automatically calculated as the remainder after all other components are applied - it is not a configurable component.

### Calculation Method

Components are processed in three phases:

#### Phase 1: Pre-Tax Components (Sequential)
- Applied in order before any taxes
- If **percentage**: Calculated from the remaining amount after previous pre-tax components
- If **flat**: Uses the flat amount value
- Each component reduces the remaining amount

#### Phase 2: Tax Components (Simultaneous)
- **All tax components** (State Taxes, Federal Taxes) are calculated **at the same time**
- All taxes use the **same base amount** (the amount remaining after pre-tax components)
- If **percentage**: Each tax is calculated from this shared base
- If **flat**: Uses the flat amount value
- Taxes do NOT affect each other's calculations

#### Phase 3: Post-Tax Components (Sequential)
- Applied in order after all taxes
- If **percentage**: Calculated from the remaining amount after taxes
- If **flat**: Uses the flat amount value
- Each component reduces the remaining amount

### Component Types

Each component can be configured as:
- **Percentage**: A percentage of the current remaining amount (or base for first component)
- **Flat Amount**: A fixed dollar amount

### Revenue (Automatic)

- **Revenue is NOT a configurable component** - it's automatically calculated as whatever remains after all other components are applied
- Revenue = Base Amount - (Sum of all other components)
- Revenue will always be displayed in results and exports, but you don't configure it in rules

### Order Configuration

- Each rule defines its own component order
- Components can be reordered using the ↑/↓ buttons in the UI
- The order number determines the sequence of calculation
- Each component type (consignment, taxes, financing, shipping) can appear once per rule

### Example Calculation

**Order subtotal**: $100.00  
**Rule components** (in order):
1. **Investor**: 20% (percentage) → $20.00 (from $100 base)
   - Remaining: $80.00
2. **State Taxes**: 5% (percentage) → $4.00 (from $80 base - calculated simultaneously)
3. **Federal Taxes**: 3% (percentage) → $2.40 (from $80 base - calculated simultaneously)
   - Both taxes calculated from $80, not sequentially
   - Remaining after taxes: $80 - $4 - $2.40 = $73.60
4. **Consigner**: 30% (percentage) → $22.08 (from $73.60 remaining)
   - Remaining: $51.52
5. **Revenue** (automatic) → $51.52 (whatever is left)

**Total allocated**: $20 + $4 + $2.40 + $22.08 + $51.52 = $100.00 ✓

**Key Point**: State Taxes ($4.00) and Federal Taxes ($2.40) were both calculated from $80.00, not sequentially. If they were sequential, Federal Taxes would be calculated from $76.00 ($80 - $4), resulting in $2.28 instead of $2.40.

### Important Notes

- **Tax components are simultaneous**: All tax components (State Taxes, Federal Taxes) are calculated from the same base amount at the same time
- **Pre-tax components are sequential**: Each pre-tax component affects the remaining amount for the next
- **Post-tax components are sequential**: Each post-tax component affects the remaining amount for the next
- **Tax base**: Taxes use the amount remaining after all pre-tax components are applied
- **Percentage components**: Calculated from the current remaining amount (or tax base for taxes)
- **Flat amounts**: Always use the exact value specified
- **Order matters**: Changing the order of non-tax components will change the final amounts, but tax order doesn't matter (they're all calculated from the same base)
- **Revenue**: Automatically calculated as the remainder after all components

