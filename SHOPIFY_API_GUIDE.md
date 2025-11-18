# Shopify GraphQL Admin API - What You Need

## Overview
Based on your application requirements, you need to fetch **orders** from Shopify with specific fields for categorization and export.

## Required API Endpoint

**Endpoint:** `https://{shop_domain}.myshopify.com/admin/api/2025-10/graphql.json`

**Method:** POST

**Headers:**
- `Content-Type: application/json`
- `X-Shopify-Access-Token: {your_access_token}`

## Required GraphQL Query

### Basic Order Query Structure

You'll need to query the `orders` field from the GraphQL Admin API. Here's the query structure you need:

```graphql
query GetOrders($first: Int!, $query: String!) {
  orders(first: $first, query: $query) {
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
```

### Date Range Filtering

Use the `query` parameter to filter by date range:

```python
# Example query string for date filtering
query_string = f"created_at:>={start_date} AND created_at:<={end_date}"
```

## Field Mapping

Here's how the GraphQL response maps to your current data structure:

| Your Code Expects | GraphQL Field | Notes |
|------------------|---------------|-------|
| `order["id"]` | `node.id` | Global ID (e.g., "gid://shopify/Order/123456") |
| `order["order_number"]` | `node.name` | Order number (e.g., "#1001") |
| `order["created_at"]` | `node.createdAt` | ISO 8601 format |
| `order["email"]` | `node.email` | Customer email |
| `order["customer"]["first_name"]` | `node.customer.firstName` | May be null |
| `order["customer"]["last_name"]` | `node.customer.lastName` | May be null |
| `order["line_items"][]["name"]` | `node.lineItems.edges[].node.name` | Product name |
| `order["line_items"][]["title"]` | `node.lineItems.edges[].node.title` | Product title |
| `order["line_items"][]["price"]` | `node.lineItems.edges[].node.originalUnitPriceSet.shopMoney.amount` | String format |
| `order["line_items"][]["quantity"]` | `node.lineItems.edges[].node.quantity` | Integer |
| `order["subtotal_price"]` | `node.subtotalPriceSet.shopMoney.amount` | String format |
| `order["total_tax"]` | `node.totalTaxSet.shopMoney.amount` | String format |
| `order["total_price"]` | `node.totalPriceSet.shopMoney.amount` | String format |
| `order["currency"]` | `node.currencyCode` | Currency code (e.g., "USD") |

## Pagination

Shopify uses cursor-based pagination. You'll need to handle pagination to get all orders:

```python
has_next_page = True
cursor = None
all_orders = []

while has_next_page:
    # Build query with cursor if available
    variables = {
        "first": 250,  # Max 250 per page
        "query": f"created_at:>={start_date} AND created_at:<={end_date}"
    }
    if cursor:
        variables["after"] = cursor
    
    # Make API call...
    
    # Process response
    orders = response["data"]["orders"]["edges"]
    all_orders.extend([edge["node"] for edge in orders])
    
    # Check for next page
    page_info = response["data"]["orders"]["pageInfo"]
    has_next_page = page_info["hasNextPage"]
    cursor = page_info["endCursor"]
```

## Rate Limits

- **Default rate limit:** 40 points per second
- **Burst capacity:** 1000 points
- **Query cost:** Each order query costs approximately 1-3 points depending on complexity
- **Recommendation:** Use bulk operations for large date ranges (100+ orders)

## Required Scopes

Your Shopify app needs these OAuth scopes:
- `read_orders` - Required to fetch orders
- `read_customers` - Required to get customer information (optional, but recommended)

## Implementation Notes

1. **API Version:** Update your `config.json` to use `"2025-10"` (latest stable) or `"2024-01"` if you prefer
2. **Error Handling:** GraphQL returns HTTP 200 even for errors - check the `errors` field in the response
3. **Data Transformation:** You'll need to transform the GraphQL response structure to match your current dummy data format
4. **Authentication:** Use the access token from your config in the `X-Shopify-Access-Token` header

## Example Python Implementation

```python
import requests
import json

def fetch_orders_graphql(shop_domain: str, access_token: str, 
                         start_date: str, end_date: str) -> List[Dict]:
    """
    Fetch orders using GraphQL Admin API.
    """
    url = f"https://{shop_domain}/admin/api/2025-10/graphql.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    
    query = """
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
    
    while has_next_page:
        variables = {
            "first": 250,
            "query": f"created_at:>={start_date} AND created_at:<={end_date}"
        }
        if cursor:
            variables["after"] = cursor
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for GraphQL errors
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        
        orders_data = data["data"]["orders"]
        edges = orders_data["edges"]
        
        # Transform to your expected format
        for edge in edges:
            node = edge["node"]
            transformed_order = transform_order(node)
            all_orders.append(transformed_order)
        
        page_info = orders_data["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        cursor = page_info["endCursor"]
    
    return all_orders

def transform_order(node: Dict) -> Dict:
    """
    Transform GraphQL order node to your expected format.
    """
    # Extract order number from name (e.g., "#1001" -> "1001")
    order_number = node["name"].lstrip("#") if node.get("name") else ""
    
    # Transform line items
    line_items = []
    for item_edge in node.get("lineItems", {}).get("edges", []):
        item_node = item_edge["node"]
        line_items.append({
            "id": item_node["id"],
            "title": item_node.get("title", ""),
            "name": item_node.get("name", ""),
            "quantity": item_node.get("quantity", 1),
            "price": item_node.get("originalUnitPriceSet", {})
                          .get("shopMoney", {})
                          .get("amount", "0")
        })
    
    # Extract customer info
    customer = node.get("customer", {})
    
    # Extract money amounts
    subtotal = node.get("subtotalPriceSet", {}).get("shopMoney", {}).get("amount", "0")
    tax = node.get("totalTaxSet", {}).get("shopMoney", {}).get("amount", "0")
    total = node.get("totalPriceSet", {}).get("shopMoney", {}).get("amount", "0")
    
    return {
        "id": node["id"],
        "order_number": order_number,
        "created_at": node["createdAt"],
        "email": node.get("email", ""),
        "customer": {
            "first_name": customer.get("firstName", ""),
            "last_name": customer.get("lastName", "")
        },
        "line_items": line_items,
        "subtotal_price": subtotal,
        "total_tax": tax,
        "total_price": total,
        "currency": node.get("currencyCode", "USD")
    }
```

## Alternative: REST API

If you prefer REST over GraphQL, you can use:
- `GET /admin/api/2025-10/orders.json?created_at_min={start_date}&created_at_max={end_date}&limit=250`

However, GraphQL is recommended because:
- More efficient (fetch only needed fields)
- Better pagination handling
- Single request for nested data (customer, line items)

## Resources

- [GraphQL Admin API Reference](https://shopify.dev/docs/api/admin-graphql/latest)
- [Orders Query Documentation](https://shopify.dev/docs/api/admin-graphql/latest/queries/orders)
- [Rate Limits Guide](https://shopify.dev/concepts/about-apis/rate-limits)
- [GraphiQL Explorer](https://shopify.dev/tools/graphiql-admin-api) - Test queries interactively

