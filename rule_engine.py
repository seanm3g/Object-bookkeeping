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
    
    def find_matching_rule(self, product_description: str) -> Optional[Dict]:
        """
        Find the first matching rule for a product description.
        
        Uses first-match logic: returns the first rule whose keywords
        match the product description.
        
        Args:
            product_description: Product description/title to match
        
        Returns:
            Matching rule dictionary or None if no match
        """
        product_lower = product_description.lower()
        
        for rule in self.rules:
            keywords = rule.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in product_lower:
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
        
        # Get product descriptions
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
        component_details = []  # Track all component details with labels
        
        # For now, apply first matching rule to entire order
        # (Could be enhanced to calculate per line item)
        rule_applied = None
        for description in product_descriptions:
            rule = self.find_matching_rule(description)
            if rule and not rule_applied:
                rule_applied = rule
                matched_rules.append(rule.get("description", "Unknown rule"))
                break
        
        # Track running total for sequential calculation
        remaining_amount = base
        
        if rule_applied:
            # Get components and sort by order
            components = rule_applied.get("components", [])
            # Sort by order field
            components = sorted(components, key=lambda x: x.get("order", 999))
            
            # Separate components into: pre-tax, tax, and post-tax
            # Taxes (state_taxes, federal_taxes) are calculated from the same base simultaneously
            tax_types = {"state_taxes", "federal_taxes"}
            pre_tax_components = []
            tax_components = []
            post_tax_components = []
            
            # Find the first tax component to determine where to split
            first_tax_index = None
            for i, comp in enumerate(components):
                comp_type = comp.get("type", "")
                if comp_type in tax_types and first_tax_index is None:
                    first_tax_index = i
            
            # Split components
            if first_tax_index is not None:
                pre_tax_components = components[:first_tax_index]
                # Collect all consecutive tax components
                tax_start = first_tax_index
                tax_end = first_tax_index
                for i in range(first_tax_index, len(components)):
                    if components[i].get("type", "") in tax_types:
                        tax_end = i + 1
                    else:
                        break
                tax_components = components[tax_start:tax_end]
                post_tax_components = components[tax_end:]
            else:
                # No taxes, apply all sequentially
                pre_tax_components = components
                tax_components = []
                post_tax_components = []
            
            # Track component details for display
            component_details = []
            
            # Step 1: Apply pre-tax components sequentially
            for component in pre_tax_components:
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
            
            # Step 2: Calculate all taxes from the same base (remaining after pre-tax components)
            tax_base = remaining_amount
            for component in tax_components:
                comp_type = component.get("type", "")
                comp_label = component.get("label", "").strip()
                calc_type = component.get("calc_type", "percentage")
                value = float(component.get("value", 0))
                
                if calc_type == "flat":
                    amount = value
                else:  # percentage
                    # All taxes calculated from the same base (tax_base)
                    amount = tax_base * (value / 100)
                
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
                
                if comp_type == "state_taxes":
                    total_state_taxes += amount
                elif comp_type == "federal_taxes":
                    total_federal_taxes += amount
            
            # Step 3: Apply post-tax components sequentially
            for component in post_tax_components:
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
        
        # Format component breakdown for display
        component_breakdown = []
        if rule_applied and component_details:
            for comp_detail in component_details:
                component_breakdown.append(f"{comp_detail['display_name']}: ${comp_detail['amount']:.2f}")
        
        return {
            "order_id": str(order.get("id", "")),
            "order_number": str(order.get("order_number", "")),
            "date": order.get("created_at", "")[:10],  # Just the date part
            "customer": customer_name,
            "products": products_str,
            "order_total": float(order.get("total_price", 0)),
            "total_cost": round(total_cost, 2),
            "base_amount": base,
            "revenue": round(total_revenue, 2),
            "investor": round(total_investor, 2),
            "state_taxes": round(total_state_taxes, 2),
            "federal_taxes": round(total_federal_taxes, 2),
            "consigner": round(total_consigner, 2),
            "component_breakdown": component_breakdown,  # Detailed breakdown with labels
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

