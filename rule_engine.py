"""
Rule engine for matching product descriptions to categorization rules
and calculating financial breakdowns.
"""

import json
from typing import Dict, List, Optional


class RuleEngine:
    """Engine for matching products to rules and calculating amounts."""
    
    def __init__(self, rules: List[Dict]):
        """
        Initialize rule engine with product rules.
        
        Args:
            rules: List of rule dictionaries from config
        """
        self.rules = rules
    
    def find_matching_rule(self, line_item: Dict) -> Optional[Dict]:
        """
        Find the first matching rule for a line item.
        
        Uses first-match logic: returns the first rule whose keywords
        match any of: product title/name, vendor, product type, tags, or collections.
        
        Args:
            line_item: Line item dictionary with product information
        
        Returns:
            Matching rule dictionary or None if no match
        """
        # Collect all searchable text from the line item
        searchable_texts = []
        
        # Product title/name
        title = line_item.get("name") or line_item.get("title", "")
        if title:
            searchable_texts.append(title.lower())
        
        # Vendor
        vendor = line_item.get("vendor", "")
        if vendor:
            searchable_texts.append(vendor.lower())
        
        # Product type
        product_type = line_item.get("product_type", "")
        if product_type:
            searchable_texts.append(product_type.lower())
        
        # Tags (list of strings)
        tags = line_item.get("tags", [])
        if tags:
            for tag in tags:
                if tag:
                    searchable_texts.append(tag.lower())
        
        # Collections (list of strings)
        collections = line_item.get("collections", [])
        if collections:
            for collection in collections:
                if collection:
                    searchable_texts.append(collection.lower())
        
        # Combine all searchable text
        combined_text = " ".join(searchable_texts)
        
        # Match against rules
        for rule in self.rules:
            keywords = rule.get("keywords", [])
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Check if keyword matches any of the searchable fields
                if keyword_lower in combined_text:
                    return rule
        
        return None
    
    def calculate_order_breakdown(self, order: Dict, base_amount: str = "subtotal") -> Dict:
        """
        Calculate financial breakdown for an order.
        
        Args:
            order: Order dictionary from Shopify API
            base_amount: Which amount to use as base ("subtotal" or "total")
        
        Returns:
            Dictionary with calculated amounts:
            {
                "order_id": str,
                "order_number": str,
                "date": str,
                "customer": str,
                "products": str,
                "order_total": float,
                "total_cost": float,
                "base_amount": float,
                "revenue": float,
                "investor": float,
                "state_taxes": float,
                "federal_taxes": float,
                "consigner": float,
                "vendor": float,
                "matched_rules": List[str]
            }
        """
        # Get base amount for calculations
        if base_amount == "subtotal":
            base = float(order.get("subtotal_price", 0))
        else:
            base = float(order.get("total_price", 0))
        
        # Subtract total cost from base amount before applying rules
        total_cost = float(order.get("total_cost", 0))
        base = max(0, base - total_cost)  # Ensure base doesn't go negative
        
        # Get line items
        line_items = order.get("line_items", [])
        product_descriptions = []
        for item in line_items:
            description = item.get("name") or item.get("title", "")
            if description:
                product_descriptions.append(description)
        
        # Find matching rules for each product
        matched_rules = []
        total_revenue = 0.0
        total_investor = 0.0
        total_state_taxes = 0.0
        total_federal_taxes = 0.0
        total_consigner = 0.0
        total_vendor = 0.0
        component_details = []  # Track all component details with labels
        
        # For now, apply first matching rule to entire order
        # (Could be enhanced to calculate per line item)
        rule_applied = None
        for line_item in line_items:
            rule = self.find_matching_rule(line_item)
            if rule and not rule_applied:
                rule_applied = rule
                matched_rules.append(rule.get("description", "Unknown rule"))
                break
        
        # Track running total for sequential calculation
        remaining_amount = base
        
        if rule_applied:
            # Get components and sort by order
            # Filter out tax components - taxes are calculated from Shopify data after all deductions
            tax_types = {"state_taxes", "federal_taxes"}
            all_components = rule_applied.get("components", [])
            components = [c for c in all_components if c.get("type", "") not in tax_types]
            # Sort by order field
            components = sorted(components, key=lambda x: x.get("order", 999))
            
            # Track component details for display
            component_details = []
            
            # Apply all components sequentially (no tax components)
            for component in components:
                comp_type = component.get("type", "")
                comp_label = component.get("label", "").strip()
                if comp_type == "revenue":
                    continue
                    
                calc_type = component.get("calc_type", "percentage")
                value = float(component.get("value", 0))
                
                if calc_type == "flat":
                    amount = value
                    remaining_amount -= amount
                else:  # percentage
                    amount = remaining_amount * (value / 100)
                    remaining_amount -= amount
                
                # Store and assign
                display_name = comp_type.replace("_", " ").title()
                if comp_label:
                    display_name = f"{display_name} - {comp_label}"
                component_details.append({
                    "type": comp_type,
                    "label": comp_label,
                    "display_name": display_name,
                    "amount": amount
                })
                
                if comp_type == "investor":
                    total_investor += amount
                elif comp_type == "consigner":
                    total_consigner += amount
                elif comp_type == "vendor":
                    total_vendor += amount
            
            # Calculate taxes from Shopify tax data after all other deductions
            # Apply tax rates from Shopify to the remaining amount
            tax_lines = order.get("tax_lines", []) or []
            
            if tax_lines and remaining_amount > 0:
                # Calculate taxes on the remaining amount using Shopify tax rates
                # Use first tax line as state, second as federal (if available)
                for i, tax_line in enumerate(tax_lines):
                    tax_rate_percentage = tax_line.get("rate_percentage")
                    tax_rate = tax_line.get("rate", 0)
                    
                    # Calculate tax amount on remaining amount
                    if tax_rate_percentage:
                        # Use percentage directly
                        rate = float(tax_rate_percentage)
                        tax_amount = remaining_amount * (rate / 100)
                    elif tax_rate:
                        # Convert rate to percentage (rate is typically 0.08 for 8%)
                        rate = float(tax_rate) * 100
                        tax_amount = remaining_amount * float(tax_rate)
                    else:
                        # Fallback: use the amount from tax_line proportionally
                        tax_line_amount = float(tax_line.get("amount", "0"))
                        order_total = float(order.get("total_price", 0))
                        if order_total > 0:
                            tax_rate_from_amount = tax_line_amount / order_total
                            tax_amount = remaining_amount * tax_rate_from_amount
                        else:
                            continue
                    
                    remaining_amount -= tax_amount
                    
                    # Assign to state or federal based on position
                    if i == 0:
                        # First tax line = state taxes
                        total_state_taxes = tax_amount
                        component_details.append({
                            "type": "state_taxes",
                            "label": "",
                            "display_name": "State Taxes",
                            "amount": tax_amount
                        })
                    elif i == 1:
                        # Second tax line = federal taxes
                        total_federal_taxes = tax_amount
                        component_details.append({
                            "type": "federal_taxes",
                            "label": "",
                            "display_name": "Federal Taxes",
                            "amount": tax_amount
                        })
                    else:
                        # Additional tax lines - add to state for now
                        total_state_taxes += tax_amount
                        component_details.append({
                            "type": "state_taxes",
                            "label": "",
                            "display_name": f"Additional Tax ({tax_line.get('title', 'Tax')})",
                            "amount": tax_amount
                        })
            
            # Revenue is automatically calculated as whatever is left over
            total_revenue = max(0, remaining_amount)  # Ensure non-negative
        else:
            # Default: no categorization - revenue equals base amount
            total_revenue = base
        
        
        # Format customer name
        customer = order.get("customer", {})
        customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
        if not customer_name:
            customer_name = order.get("email", "Unknown")
        
        # Format products list
        products_str = ", ".join(product_descriptions)
        
        # Collect vendor, tags, collections, and product types from all line items
        all_vendors = set()
        all_tags = set()
        all_collections = set()
        all_product_types = set()
        
        for item in line_items:
            vendor = item.get("vendor", "")
            if vendor:
                all_vendors.add(vendor)
            
            tags = item.get("tags", [])
            if tags:
                all_tags.update(tags)
            
            collections = item.get("collections", [])
            if collections:
                all_collections.update(collections)
            
            product_type = item.get("product_type", "")
            if product_type:
                all_product_types.add(product_type)
        
        # Format component breakdown for display
        component_breakdown = []
        if rule_applied and component_details:
            for comp_detail in component_details:
                component_breakdown.append(f"{comp_detail['display_name']}: ${comp_detail['amount']:.2f}")
        
        # Extract tax lines from order (Shopify's actual tax breakdown)
        tax_lines = order.get("tax_lines", []) or []
        shopify_tax_breakdown = []
        for tax_line in tax_lines:
            title = tax_line.get("title", "Tax")
            amount = float(tax_line.get("amount", "0"))
            rate_display = tax_line.get("rate_display", "")
            if rate_display:
                shopify_tax_breakdown.append(f"{title} ({rate_display}): ${amount:.2f}")
            else:
                shopify_tax_breakdown.append(f"{title}: ${amount:.2f}")
        
        return {
            "order_id": str(order.get("id", "")),
            "order_number": str(order.get("order_number", "")),
            "date": order.get("created_at", "")[:10],  # Just the date part
            "customer": customer_name,
            "products": products_str,
            "vendor": ", ".join(sorted(all_vendors)) if all_vendors else "",
            "product_type": ", ".join(sorted(all_product_types)) if all_product_types else "",
            "tags": ", ".join(sorted(all_tags)) if all_tags else "",
            "collections": ", ".join(sorted(all_collections)) if all_collections else "",
            "order_total": float(order.get("total_price", 0)),
            "total_cost": round(total_cost, 2),
            "base_amount": base,
            "revenue": round(total_revenue, 2),
            "investor": round(total_investor, 2),
            "state_taxes": round(total_state_taxes, 2),
            "federal_taxes": round(total_federal_taxes, 2),
            "consigner": round(total_consigner, 2),
            "vendor": round(total_vendor, 2),
            "component_breakdown": component_breakdown,  # Detailed breakdown with labels
            "shopify_tax_breakdown": shopify_tax_breakdown,  # Shopify's actual tax breakdown
            "tax_lines": tax_lines,  # Raw tax line data
            "matched_rules": ", ".join(matched_rules) if matched_rules else "No match"
        }
    
    def process_orders(self, orders: List[Dict], base_amount: str = "subtotal") -> List[Dict]:
        """
        Process a list of orders and calculate breakdowns.
        
        Args:
            orders: List of order dictionaries
            base_amount: Which amount to use as base ("subtotal" or "total")
        
        Returns:
            List of breakdown dictionaries
        """
        breakdowns = []
        for order in orders:
            breakdown = self.calculate_order_breakdown(order, base_amount)
            breakdowns.append(breakdown)
        return breakdowns


def load_rules_from_config(config_path: str = "config.json") -> List[Dict]:
    """
    Load product rules from configuration file.
    
    Args:
        config_path: Path to config.json file
    
    Returns:
        List of rule dictionaries
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            return config.get("product_rules", [])
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

