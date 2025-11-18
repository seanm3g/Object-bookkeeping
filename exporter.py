"""
Export module for CSV and Google Sheets output.
Currently uses dummy/mock for Google Sheets API.
"""

import csv
import json
import re
from typing import List, Dict, Set, Tuple
from datetime import datetime
from collections import defaultdict
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    # Define dummy types for type hints when openpyxl is not available
    Workbook = None  # type: ignore
    Font = None  # type: ignore
    PatternFill = None  # type: ignore
    Alignment = None  # type: ignore


def parse_component_labels(component_breakdown: List[str]) -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Parse component breakdown to extract consigner and investor labels with amounts.
    
    Args:
        component_breakdown: List of component breakdown strings like "Consigner - Label: $amount"
    
    Returns:
        Tuple of (consigners_dict, investors_dict) where keys are labels and values are amounts
    """
    consigners = {}
    investors = {}
    
    for item in component_breakdown:
        # Parse format: "Type - Label: $amount" or "Type: $amount"
        match = re.match(r'^(Consigner|Investor)(?:\s*-\s*([^:]+))?:\s*\$\s*([\d.]+)', item)
        if match:
            comp_type = match.group(1)
            label = match.group(2).strip() if match.group(2) else ""
            amount = float(match.group(3))
            
            if comp_type == "Consigner":
                key = label if label else "Default"
                consigners[key] = consigners.get(key, 0) + amount
            elif comp_type == "Investor":
                key = label if label else "Default"
                investors[key] = investors.get(key, 0) + amount
    
    return consigners, investors


def export_to_csv(breakdowns: List[Dict], output_path: str = "orders_export.csv"):
    """
    Export order breakdowns to CSV file with unique columns for each consigner/investor.
    
    Args:
        breakdowns: List of breakdown dictionaries from rule_engine
        output_path: Path to output CSV file
    """
    if not breakdowns:
        return
    
    # Collect all unique consigner and investor labels
    all_consigner_labels = set()
    all_investor_labels = set()
    breakdowns_with_labels = []
    
    for breakdown in breakdowns:
        component_breakdown = breakdown.get("component_breakdown", [])
        consigners, investors = parse_component_labels(component_breakdown)
        all_consigner_labels.update(consigners.keys())
        all_investor_labels.update(investors.keys())
        breakdowns_with_labels.append({
            'breakdown': breakdown,
            'consigners': consigners,
            'investors': investors
        })
    
    # Build column headers
    base_columns = [
        "Order ID",
        "Order Number",
        "Date",
        "Customer",
        "Products",
        "Order Total",
        "Total Cost",
        "Revenue",
        "State Taxes",
        "Federal Taxes",
    ]
    
    # Add columns for each unique investor (sorted)
    investor_columns = [f"Investor - {label}" if label != "Default" else "Investor" 
                       for label in sorted(all_investor_labels)]
    
    # Add columns for each unique consigner (sorted)
    consigner_columns = [f"Consigner - {label}" if label != "Default" else "Consigner" 
                        for label in sorted(all_consigner_labels)]
    
    # Combine all columns
    fieldnames = base_columns + investor_columns + consigner_columns + [
        "Component Breakdown",
        "Matched Rules"
    ]
    
    # Write CSV
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Track totals for numeric columns
        totals = {col: 0.0 for col in fieldnames if col in [
            "Order Total", "Total Cost", "Revenue", "State Taxes", "Federal Taxes"
        ] + investor_columns + consigner_columns}
        
        # Write data rows
        for item in breakdowns_with_labels:
            breakdown = item['breakdown']
            consigners = item['consigners']
            investors = item['investors']
            
            component_breakdown = breakdown.get("component_breakdown", [])
            breakdown_str = "; ".join(component_breakdown) if component_breakdown else ""
            
            # Build row
            row = {
                "Order ID": breakdown.get("order_id", ""),
                "Order Number": breakdown.get("order_number", ""),
                "Date": breakdown.get("date", ""),
                "Customer": breakdown.get("customer", ""),
                "Products": breakdown.get("products", ""),
                "Order Total": breakdown.get("order_total", 0),
                "Total Cost": breakdown.get("total_cost", 0),
                "Revenue": breakdown.get("revenue", 0),
                "State Taxes": breakdown.get("state_taxes", 0),
                "Federal Taxes": breakdown.get("federal_taxes", 0),
                "Component Breakdown": breakdown_str,
                "Matched Rules": breakdown.get("matched_rules", "")
            }
            
            # Add investor columns
            for label in sorted(all_investor_labels):
                col_name = f"Investor - {label}" if label != "Default" else "Investor"
                amount = investors.get(label, 0)
                row[col_name] = amount
                totals[col_name] = totals.get(col_name, 0) + amount
            
            # Add consigner columns
            for label in sorted(all_consigner_labels):
                col_name = f"Consigner - {label}" if label != "Default" else "Consigner"
                amount = consigners.get(label, 0)
                row[col_name] = amount
                totals[col_name] = totals.get(col_name, 0) + amount
            
            # Update totals for base numeric columns
            for col in ["Order Total", "Total Cost", "Revenue", "State Taxes", "Federal Taxes"]:
                totals[col] += row.get(col, 0) or 0
            
            writer.writerow(row)
        
        # Write totals row
        totals_row = {"Order ID": "TOTAL"}
        for col in fieldnames[1:]:  # Skip Order ID
            if col in totals:
                totals_row[col] = round(totals[col], 2)
            else:
                totals_row[col] = ""
        writer.writerow(totals_row)


def _create_sheet(wb, sheet_name: str, breakdowns: List[Dict], fieldnames: List[str]):
    """Create a sheet with data and totals row."""
    ws = wb.create_sheet(title=sheet_name)
    
    # Header style
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    # Write headers
    for col, field in enumerate(fieldnames, start=1):
        cell = ws.cell(row=1, column=col, value=field)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Write data rows
    numeric_cols = [6, 7, 8, 9, 10, 11, 12]  # Order Total through Consigner columns
    
    for row_idx, breakdown in enumerate(breakdowns, start=2):
        component_breakdown = breakdown.get("component_breakdown", [])
        breakdown_str = "; ".join(component_breakdown) if component_breakdown else ""
        
        values = [
            breakdown.get("order_id", ""),
            breakdown.get("order_number", ""),
            breakdown.get("date", ""),
            breakdown.get("customer", ""),
            breakdown.get("products", ""),
            breakdown.get("order_total", 0),
            breakdown.get("total_cost", 0),
            breakdown.get("revenue", 0),
            breakdown.get("investor", 0),
            breakdown.get("state_taxes", 0),
            breakdown.get("federal_taxes", 0),
            breakdown.get("consigner", 0),
            breakdown_str,
            breakdown.get("matched_rules", "")
        ]
        
        for col, value in enumerate(values, start=1):
            cell = ws.cell(row=row_idx, column=col, value=value)
            if col in numeric_cols:
                cell.number_format = '0.00'
    
    # Add totals row
    totals_row = row_idx + 1
    ws.cell(row=totals_row, column=1, value="TOTAL").font = Font(bold=True)
    
    # Calculate totals for numeric columns
    for col in numeric_cols:
        col_letter = ws.cell(row=1, column=col).column_letter
        formula = f"=SUM({col_letter}2:{col_letter}{row_idx})"
        cell = ws.cell(row=totals_row, column=col, value=formula)
        cell.font = Font(bold=True)
        cell.number_format = '0.00'
        cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    
    # Auto-adjust column widths
    for col in range(1, len(fieldnames) + 1):
        max_length = 0
        column_letter = ws.cell(row=1, column=col).column_letter
        for row in ws[column_letter]:
            try:
                if len(str(row.value)) > max_length:
                    max_length = len(str(row.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width


def _export_to_csv_fallback(breakdowns: List[Dict], output_path: str):
    """Fallback CSV export if openpyxl is not available."""
    fieldnames = [
        "Order ID",
        "Order Number",
        "Date",
        "Customer",
        "Products",
        "Order Total",
        "Total Cost",
        "Revenue",
        "Investor",
        "State Taxes",
        "Federal Taxes",
        "Consigner",
        "Component Breakdown",
        "Matched Rules"
    ]
    
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        totals = {col: 0 for col in fieldnames[5:12]}  # Numeric columns
        
        for breakdown in breakdowns:
            component_breakdown = breakdown.get("component_breakdown", [])
            breakdown_str = "; ".join(component_breakdown) if component_breakdown else ""
            
            row = {
                "Order ID": breakdown.get("order_id", ""),
                "Order Number": breakdown.get("order_number", ""),
                "Date": breakdown.get("date", ""),
                "Customer": breakdown.get("customer", ""),
                "Products": breakdown.get("products", ""),
                "Order Total": breakdown.get("order_total", 0),
                "Total Cost": breakdown.get("total_cost", 0),
                "Revenue": breakdown.get("revenue", 0),
                "Investor": breakdown.get("investor", 0),
                "State Taxes": breakdown.get("state_taxes", 0),
                "Federal Taxes": breakdown.get("federal_taxes", 0),
                "Consigner": breakdown.get("consigner", 0),
                "Component Breakdown": breakdown_str,
                "Matched Rules": breakdown.get("matched_rules", "")
            }
            writer.writerow(row)
            
            # Accumulate totals
            for col in totals.keys():
                totals[col] += row.get(col, 0) or 0
        
        # Write totals row
        totals_row = {"Order ID": "TOTAL"}
        totals_row.update(totals)
        totals_row.update({
            "Order Number": "",
            "Date": "",
            "Customer": "",
            "Products": "",
            "Component Breakdown": "",
            "Matched Rules": ""
        })
        writer.writerow(totals_row)


def export_to_google_sheets(breakdowns: List[Dict], spreadsheet_id: str = None, 
                            credentials_file: str = None):
    """
    Export order breakdowns to Google Sheets with monthly tabs.
    
    Currently uses dummy/mock implementation for MVP.
    Real Google Sheets API integration will be added later.
    
    Args:
        breakdowns: List of breakdown dictionaries from rule_engine
        spreadsheet_id: Google Sheets spreadsheet ID
        credentials_file: Path to Google API credentials JSON file
    """
    # TODO: Replace with real Google Sheets API integration
    # For now, just print what would be exported
    print("Google Sheets Export (Mock)")
    print(f"Would export {len(breakdowns)} orders to spreadsheet: {spreadsheet_id}")
    
    # Group by month
    monthly_data = defaultdict(list)
    for breakdown in breakdowns:
        date_str = breakdown.get("date", "")
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_key = date_obj.strftime("%Y-%m")
            monthly_data[month_key].append(breakdown)
        except (ValueError, TypeError):
            # If date parsing fails, put in "Unknown" month
            monthly_data["Unknown"].append(breakdown)
    
    print("\nMonthly organization:")
    for month, orders in sorted(monthly_data.items()):
        print(f"  {month}: {len(orders)} orders")
    
    # In real implementation, would:
    # 1. Authenticate with Google Sheets API
    # 2. Create/update spreadsheet
    # 3. Create/update monthly tabs
    # 4. Write data to appropriate tabs


def organize_by_month(breakdowns: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Organize breakdowns by month.
    
    Args:
        breakdowns: List of breakdown dictionaries
    
    Returns:
        Dictionary mapping month (YYYY-MM) to list of breakdowns
    """
    monthly_data = defaultdict(list)
    for breakdown in breakdowns:
        date_str = breakdown.get("date", "")
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_key = date_obj.strftime("%Y-%m")
            monthly_data[month_key].append(breakdown)
        except (ValueError, TypeError):
            monthly_data["Unknown"].append(breakdown)
    
    return dict(monthly_data)

