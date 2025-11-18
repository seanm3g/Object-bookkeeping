"""
Shopify API client for fetching orders.
Uses GraphQL Admin API to fetch real order data.
"""

import json
import random
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional


def generate_dummy_orders(start_date: str, end_date: str, count: int = 10) -> List[Dict]:
    """
    Generate dummy order data for testing.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        count: Number of orders to generate
    
    Returns:
        List of order dictionaries matching Shopify API format
    """
    orders = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    date_range = (end - start).days
    
    sample_products = [
        {"title": "Consignment Art Piece", "description": "Beautiful consignment artwork", "price": 150.00},
        {"title": "Standard Furniture", "description": "Regular furniture item", "price": 299.99},
        {"title": "Consignment Vintage Lamp", "description": "Vintage consignment lighting", "price": 89.50},
        {"title": "Premium Sofa", "description": "Standard premium furniture", "price": 599.99},
        {"title": "Art Consignment Collection", "description": "Consignment art collection", "price": 250.00},
    ]
    
    for i in range(count):
        # Generate random date within range
        days_offset = (i * date_range) // max(count - 1, 1)
        order_date = start + timedelta(days=days_offset)
        
        # Select random products
        num_items = random.randint(1, 3)
        line_items = random.sample(sample_products, min(num_items, len(sample_products)))
        
        subtotal = sum(item["price"] for item in line_items)
        tax = subtotal * 0.10  # 10% tax
        total = subtotal + tax
        # Calculate total cost (assume 50% of price as cost for dummy data)
        total_cost = sum(item["price"] * 0.5 for item in line_items)
        
        order = {
            "id": 1000 + i,
            "order_number": 2000 + i,
            "created_at": order_date.isoformat(),
            "email": f"customer{i}@example.com",
            "customer": {
                "first_name": f"Customer{i}",
                "last_name": "Test"
            },
            "line_items": [
                {
                    "id": 10000 + (i * 10) + j,
                    "title": item["title"],
                    "product_id": 5000 + j,
                    "variant_id": 6000 + j,
                    "quantity": 1,
                    "price": str(item["price"]),
                    "name": item["title"],
                    "cost": str(item["price"] * 0.5)  # Dummy cost: 50% of price
                }
                for j, item in enumerate(line_items)
            ],
            "subtotal_price": str(subtotal),
            "total_tax": str(tax),
            "total_price": str(total),
            "total_cost": str(total_cost),
            "currency": "USD"
        }
        orders.append(order)
    
    return orders


def transform_order(node: Dict) -> Dict:
    """
    Transform GraphQL order node to expected format.
    
    Args:
        node: GraphQL order node from Shopify API
    
    Returns:
        Order dictionary in expected format
    """
    # Extract order number from name (e.g., "#1001" -> "1001")
    order_number = node.get("name", "").lstrip("#") if node.get("name") else ""
    
    # Transform line items
    line_items = []
    total_cost = 0.0
    for item_edge in node.get("lineItems", {}).get("edges", []):
        item_node = item_edge["node"]
        price_data = item_node.get("originalUnitPriceSet", {}).get("shopMoney", {})
        variant = item_node.get("variant", {})
        inventory_item = variant.get("inventoryItem", {}) if variant else {}
        unit_cost_data = inventory_item.get("unitCost", {}) if inventory_item else {}
        unit_cost_amount = unit_cost_data.get("amount") if unit_cost_data else None
        quantity = item_node.get("quantity", 1)
        
        # Calculate cost for this line item (cost per unit * quantity)
        item_cost = 0.0
        if unit_cost_amount is not None:
            try:
                item_cost = float(unit_cost_amount) * quantity
                total_cost += item_cost
            except (ValueError, TypeError):
                pass
        
        line_items.append({
            "id": item_node.get("id", ""),
            "title": item_node.get("title", ""),
            "name": item_node.get("name", ""),
            "quantity": quantity,
            "price": price_data.get("amount", "0"),
            "cost": str(item_cost) if item_cost > 0 else "0"
        })
    
    # Extract customer info
    customer = node.get("customer", {}) or {}
    
    # Extract money amounts
    subtotal = node.get("subtotalPriceSet", {}).get("shopMoney", {}).get("amount", "0")
    tax = node.get("totalTaxSet", {}).get("shopMoney", {}).get("amount", "0")
    total = node.get("totalPriceSet", {}).get("shopMoney", {}).get("amount", "0")
    
    return {
        "id": node.get("id", ""),
        "order_number": order_number,
        "created_at": node.get("createdAt", ""),
        "email": node.get("email", ""),
        "customer": {
            "first_name": customer.get("firstName", ""),
            "last_name": customer.get("lastName", "")
        },
        "line_items": line_items,
        "subtotal_price": subtotal,
        "total_tax": tax,
        "total_price": total,
        "total_cost": str(total_cost),
        "currency": node.get("currencyCode", "USD")
    }


def fetch_orders(shop_domain: str, access_token: str, start_date: str, end_date: str, 
                 api_version: str = "2025-10") -> List[Dict]:
    """
    Fetch orders from Shopify API using GraphQL.
    
    Args:
        shop_domain: Shopify shop domain (e.g., "myshop.myshopify.com")
        access_token: Shopify API access token
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        api_version: Shopify API version
    
    Returns:
        List of order dictionaries
    
    Raises:
        Exception: If API call fails or returns errors
    """
    # If no credentials provided, return dummy data for testing
    if not shop_domain or not access_token:
        return generate_dummy_orders(start_date, end_date, count=15)
    
    # Ensure shop_domain doesn't have https:// prefix
    shop_domain = shop_domain.replace("https://", "").replace("http://", "").rstrip("/")
    
    url = f"https://{shop_domain}/admin/api/{api_version}/graphql.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    
    # GraphQL query with cost data
    query_with_cost = """
    query GetOrders($first: Int!, $query: String!, $after: String) {
      orders(first: $first, query: $query, after: $after) {
        edges {
          node {
            id
            name
            createdAt
            email
            customer {
              firstName
              lastName
            }
            lineItems(first: 250) {
              edges {
                node {
                  id
                  title
                  name
                  quantity
                  originalUnitPriceSet {
                    shopMoney {
                      amount
                      currencyCode
                    }
                  }
                  variant {
                    id
                    inventoryItem {
                      id
                      unitCost {
                        amount
                        currencyCode
                      }
                    }
                  }
                }
              }
            }
            subtotalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            totalTaxSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            totalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            currencyCode
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    
    # GraphQL query without cost data (fallback)
    query_without_cost = """
    query GetOrders($first: Int!, $query: String!, $after: String) {
      orders(first: $first, query: $query, after: $after) {
        edges {
          node {
            id
            name
            createdAt
            email
            customer {
              firstName
              lastName
            }
            lineItems(first: 250) {
              edges {
                node {
                  id
                  title
                  name
                  quantity
                  originalUnitPriceSet {
                    shopMoney {
                      amount
                      currencyCode
                    }
                  }
                  variant {
                    id
                  }
                }
              }
            }
            subtotalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            totalTaxSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            totalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            currencyCode
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    
    all_orders = []
    cursor = None
    has_next_page = True
    
    # Build query string for date filtering
    # Format: created_at:>=2024-01-01 AND created_at:<2024-02-01
    # Use < (next day) instead of <= to exclude orders from the day after end_date
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    end_date_next = (end_date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
    query_string = f"created_at:>={start_date} AND created_at:<{end_date_next}"
    
    # Try with cost first, fallback to without cost if it fails
    use_cost_query = True
    query = query_with_cost
    
    while has_next_page:
        variables = {
            "first": 250,  # Max 250 per page
            "query": query_string
        }
        if cursor:
            variables["after"] = cursor
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Check HTTP status code first
            if response.status_code == 401:
                raise Exception("Access denied: Invalid access token or insufficient permissions. Please check your API credentials.")
            elif response.status_code == 403:
                raise Exception("Access forbidden: Your access token doesn't have the required scopes. Make sure 'read_orders' scope is enabled.")
            elif response.status_code == 404:
                raise Exception(f"Shop not found: Check that your shop domain '{shop_domain}' is correct.")
            elif not response.ok:
                raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")
            
            data = response.json()
            
            # Check for GraphQL errors
            if "errors" in data:
                error_messages = []
                cost_access_error = False
                for err in data["errors"]:
                    msg = err.get("message", str(err))
                    # Check if error is about variant or products access
                    if "read_products" in msg or "variant field" in msg.lower():
                        # Need read_products scope - this is required for variant access
                        error_messages.append("Missing 'read_products' scope. Please add 'read_products' to your app's API scopes and reinstall the app.")
                        continue
                    # Check if error is about inventoryItem/cost access
                    if "inventoryItem" in msg or "unitCost" in msg or ("cost" in msg.lower() and "order" not in msg.lower()):
                        cost_access_error = True
                        # Don't add to error messages - we'll handle this gracefully
                        continue
                    # Check for specific error codes
                    extensions = err.get("extensions", {})
                    if extensions.get("code") == "ACCESS_DENIED":
                        # Check if it's specifically about orders or something else
                        if "order" in msg.lower():
                            error_messages.append("Access denied: Your access token doesn't have permission to access orders. Please check your API scopes.")
                        else:
                            error_messages.append(f"Access denied: {msg}")
                    else:
                        error_messages.append(msg)
                
                # If we have non-cost-related errors, raise them
                if error_messages:
                    raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")
                
                # If only cost-related errors and we're using cost query, retry without cost
                if cost_access_error and use_cost_query:
                    print("Warning: Unable to fetch product costs. Retrying without cost data. Cost will be set to $0.00.")
                    use_cost_query = False
                    query = query_without_cost
                    # Reset pagination and retry
                    cursor = None
                    has_next_page = True
                    all_orders = []
                    continue
                
                # If only cost-related errors and we're already using the fallback, continue
                if cost_access_error:
                    print("Warning: Unable to fetch product costs. Cost data will be set to $0.00.")
            
            if "data" not in data or "orders" not in data["data"]:
                raise Exception("Unexpected response format from Shopify API")
            
            orders_data = data["data"]["orders"]
            edges = orders_data.get("edges", [])
            
            # Transform to expected format
            for edge in edges:
                node = edge["node"]
                transformed_order = transform_order(node)
                all_orders.append(transformed_order)
            
            page_info = orders_data.get("pageInfo", {})
            has_next_page = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Shopify API: {str(e)}")
        except KeyError as e:
            raise Exception(f"Unexpected response structure: missing {str(e)}")
    
    return all_orders


def get_order_line_items(order: Dict) -> List[Dict]:
    """
    Extract line items from an order.
    
    Args:
        order: Order dictionary from Shopify API
    
    Returns:
        List of line item dictionaries with product information
    """
    return order.get("line_items", [])


def get_product_descriptions(order: Dict) -> List[str]:
    """
    Extract product descriptions/titles from an order.
    
    Args:
        order: Order dictionary from Shopify API
    
    Returns:
        List of product description strings
    """
    line_items = get_order_line_items(order)
    descriptions = []
    for item in line_items:
        # Use title/name as description (Shopify API structure)
        description = item.get("name") or item.get("title", "")
        descriptions.append(description)
    return descriptions

