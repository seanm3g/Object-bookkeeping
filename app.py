"""
Web-based GUI application for Shopify Order Categorization.
Simple Flask web interface that runs in your browser.
Supports multi-user authentication for hosted deployment.
"""

from flask import Flask, render_template_string, request, jsonify, send_file, redirect, url_for, session
from flask_login import LoginManager, login_required, current_user
import json
import os
import webbrowser
import threading
import time
import subprocess
import sys
from datetime import datetime, timedelta
from urllib.parse import urlencode

try:
    from google_auth_oauthlib.flow import Flow
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False
    Flow = None
    Credentials = None
    build = None

from shopify_client import fetch_orders
from rule_engine import RuleEngine
from exporter import export_to_csv, export_to_google_sheets
from models import User, UserConfig, UserRule, init_db, get_db_session
from auth import auth_bp

app = Flask(__name__)

# Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Register auth blueprint
app.register_blueprint(auth_bp)

# Initialize database
# Note: We catch exceptions here so the app can start even if database is unavailable
# The app will show errors when trying to use database features
try:
    engine = init_db()
    # Store engine globally for reuse (optional optimization)
    app.config['db_engine'] = engine
except Exception as e:
    print(f"CRITICAL: Database initialization failed: {e}")
    print("The app will continue but data may not persist. Check your DATABASE_URL environment variable.")
    print("If deploying to Render, make sure you:")
    print("  1. Created a PostgreSQL database")
    print("  2. Set DATABASE_URL environment variable in your web service")
    print("  3. Used the 'Internal Database URL' from your PostgreSQL service")
    app.config['db_engine'] = None

CONFIG_PATH = "config.json"  # Fallback for migration


@login_manager.user_loader
def load_user(user_id):
    """Load user from database for Flask-Login."""
    session = get_db_session()
    try:
        return session.query(User).get(int(user_id))
    finally:
        session.close()


def load_config():
    """Load configuration from database for current user, or JSON file as fallback."""
    if current_user.is_authenticated:
        session = get_db_session()
        try:
            user_config = session.query(UserConfig).filter_by(user_id=current_user.id).first()
            if user_config:
                config = user_config.to_dict()
                # Load rules
                rules = session.query(UserRule).filter_by(user_id=current_user.id).all()
                config['product_rules'] = [rule.to_dict() for rule in rules]
                return config
        finally:
            session.close()
    
    # Fallback to JSON file (for migration or non-authenticated)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return get_default_config()
    return get_default_config()


def save_config(config):
    """Save configuration to database for current user, or JSON file as fallback."""
    if current_user.is_authenticated:
        db_session = get_db_session()
        try:
            user_config = db_session.query(UserConfig).filter_by(user_id=current_user.id).first()
            if not user_config:
                user_config = UserConfig(user_id=current_user.id)
                db_session.add(user_config)
            
            # Update config
            shopify = config.get('shopify', {})
            user_config.shop_domain = shopify.get('shop_domain', '')
            user_config.access_token = shopify.get('access_token', '')
            user_config.api_version = shopify.get('api_version', '2025-10')
            user_config.export_path = config.get('export_path', '')
            
            # Update Google Sheets config (but don't overwrite OAuth token if not provided)
            gsheets = config.get('google_sheets', {})
            if 'spreadsheet_id' in gsheets:
                user_config.gsheets_spreadsheet_id = gsheets.get('spreadsheet_id', '')
            # OAuth token is saved separately via OAuth callback
            
            user_config.updated_at = datetime.utcnow()
            
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.close()
    else:
        # Fallback to JSON file
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)


def get_default_config():
    """Get default configuration structure."""
    return {
        "shopify": {
            "shop_domain": "",
            "access_token": "",
            "api_version": "2025-10"
        },
        "google_sheets": {
            "enabled": False,
            "credentials_file": "",
            "spreadsheet_id": ""
        },
        "export_path": "",
        "product_rules": []
    }


# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Shopify Order Categorization</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #333;
            margin-top: 0;
        }
        h2 {
            color: #555;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #333;
        }
        input[type="text"], input[type="password"], input[type="date"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }
        button {
            background: #007AFF;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            margin-right: 10px;
        }
        button:hover {
            background: #0056b3;
        }
        button.secondary {
            background: #6c757d;
        }
        button.danger {
            background: #dc3545;
        }
        button:disabled {
            background: #6c757d;
            cursor: not-allowed;
            opacity: 0.6;
        }
        button.export-yellow {
            background: #ffc107;
            color: #000;
        }
        button.export-yellow:hover {
            background: #e0a800;
        }
        button.export-green {
            background: #28a745;
        }
        button.export-green:hover {
            background: #218838;
        }
        .rules-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        .rules-table th, .rules-table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .rules-table th {
            background: #f8f9fa;
            font-weight: 600;
        }
        .results {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
            max-height: 400px;
            overflow-y: auto;
        }
        .order-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
            border-left: 4px solid #007AFF;
        }
        .success {
            color: #28a745;
            padding: 10px;
            background: #d4edda;
            border-radius: 4px;
            margin: 10px 0;
        }
        .error {
            color: #dc3545;
            padding: 10px;
            background: #f8d7da;
            border-radius: 4px;
            margin: 10px 0;
        }
        .rule-form {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 4px;
            margin: 20px 0;
        }
        .component-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .component-item select, .component-item input {
            flex: 1;
        }
        .component-order {
            font-weight: bold;
            min-width: 30px;
        }
        .move-buttons {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .move-buttons button {
            padding: 5px 10px;
            font-size: 12px;
        }
        .nav {
            background: #333;
            padding: 15px 20px;
            margin: -20px -20px 20px -20px;
            border-radius: 8px 8px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .nav h1 {
            color: white;
            margin: 0;
            font-size: 20px;
        }
        .nav-links {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .nav-links a, .nav-links span {
            color: white;
            text-decoration: none;
            font-size: 14px;
        }
        .nav-links a:hover {
            text-decoration: underline;
        }
        .nav-links .username {
            color: #ccc;
        }
        .dark-mode-toggle {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }
        .dark-mode-toggle:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        /* Dark mode styles */
        body.dark-mode {
            background: #1a1a1a;
            color: #e0e0e0;
        }
        body.dark-mode .container {
            background: #2d2d2d;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        body.dark-mode h1 {
            color: #e0e0e0;
        }
        body.dark-mode h2 {
            color: #d0d0d0;
            border-bottom-color: #444;
        }
        body.dark-mode label {
            color: #d0d0d0;
        }
        body.dark-mode input[type="text"], 
        body.dark-mode input[type="password"], 
        body.dark-mode input[type="date"] {
            background: #3a3a3a;
            border-color: #555;
            color: #e0e0e0;
        }
        body.dark-mode .rules-table th {
            background: #3a3a3a;
            color: #e0e0e0;
        }
        body.dark-mode .rules-table td {
            border-bottom-color: #444;
            color: #e0e0e0;
        }
        body.dark-mode .results {
            background: #3a3a3a;
        }
        body.dark-mode .order-item {
            background: #3a3a3a;
            border-left-color: #007AFF;
        }
        body.dark-mode .rule-form {
            background: #3a3a3a;
        }
        body.dark-mode .component-item {
            background: #2d2d2d;
            border-color: #555;
        }
        body.dark-mode .component-item select,
        body.dark-mode .component-item input {
            background: #3a3a3a;
            border-color: #555;
            color: #e0e0e0;
        }
        body.dark-mode .success {
            background: #1e4620;
            color: #90ee90;
        }
        body.dark-mode .error {
            background: #4a1e1e;
            color: #ff6b6b;
        }
        body.dark-mode small {
            color: #aaa;
        }
        body.dark-mode em {
            color: #888;
        }
        .deduction-sequence-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        body.dark-mode .deduction-sequence-box {
            background: #3a3a3a;
        }
        .deduction-step {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding: 10px;
            background: white;
            border-left: 4px solid #007AFF;
            border-radius: 4px;
        }
        body.dark-mode .deduction-step {
            background: #2d2d2d;
        }
        .deduction-notes {
            background: #e7f3ff;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #007AFF;
        }
        body.dark-mode .deduction-notes {
            background: #1e3a4a;
            border-left-color: #007AFF;
        }
        body.dark-mode .deduction-step div[style*="color: #666"] {
            color: #aaa !important;
        }
        body.dark-mode .deduction-notes ul {
            color: #d0d0d0;
        }
    </style>
</head>
<body>
    <div class="nav">
        <h1>Shopify Order Categorization</h1>
        <div class="nav-links">
            <span class="username">Logged in as: {{ current_user.username }}</span>
            <button class="dark-mode-toggle" onclick="toggleDarkMode()" id="darkModeToggle">🌙 Dark Mode</button>
            {% if current_user.is_admin %}
            <a href="/admin">Admin Panel</a>
            {% endif %}
            <a href="/logout">Logout</a>
        </div>
    </div>
    
    <!-- Fetch Orders Section -->
    <div class="container">
        <h2>Fetch Orders</h2>
        <form id="fetchForm">
            <div class="form-group">
                <label>Start Date:</label>
                <input type="date" name="start_date" id="start_date" value="{{ start_date }}" required>
            </div>
            <div class="form-group">
                <label>End Date:</label>
                <input type="date" name="end_date" id="end_date" value="{{ end_date }}" required>
            </div>
            
            <div class="form-group" style="margin-top: 15px; margin-bottom: 15px;">
                <label style="margin-bottom: 10px; display: block; font-weight: 600;">Quick Date Ranges:</label>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button type="button" onclick="setLastMonth()" style="padding: 8px 16px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; color: #000;">Last Month</button>
                    <button type="button" onclick="setThisMonthToDate()" style="padding: 8px 16px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; color: #000;">This Month to Date</button>
                </div>
            </div>
            
            <div style="display: flex; gap: 10px; align-items: center;">
                <button type="submit">Fetch Orders</button>
                <button onclick="exportCSV()" id="exportBtn" disabled>Export to CSV</button>
                <button onclick="exportGoogleSheets()" id="exportGSheetsBtn" disabled>Export to Google Sheets</button>
            </div>
        </form>
        <div id="results"></div>
    </div>
    
    <!-- Product Rules Section -->
    <div class="container">
        <h2>Product Rules</h2>
        <div class="rule-form">
            <h3 id="ruleFormTitle">Add New Rule</h3>
            <form id="ruleForm">
                <input type="hidden" id="ruleId" name="rule_id" value="">
                <div class="form-group">
                    <label>Description:</label>
                    <input type="text" name="description" id="ruleDescription" required>
                </div>
                <div class="form-group">
                    <label>Keywords (comma-separated):</label>
                    <input type="text" name="keywords" id="ruleKeywords" required placeholder="consignment, consign">
                </div>
                
                <h4>Components (applied in order):</h4>
                <p style="color: #666; font-size: 0.9em; margin-bottom: 10px;">
                    <strong>Note:</strong> Revenue is automatically calculated as the remainder after all other components are applied. Taxes are automatically calculated from Shopify tax data after all deductions.
                </p>
                <div id="componentsList"></div>
                <button type="button" onclick="addComponent()" style="margin-top: 10px;">+ Add Component</button>
                
                <div style="margin-top: 20px; display: flex; gap: 10px;">
                    <button type="submit" id="submitRuleBtn">Add Rule</button>
                    <button type="button" id="cancelEditBtn" onclick="cancelEdit()" style="display: none;" class="secondary">Cancel</button>
                </div>
            </form>
        </div>
        
        <table class="rules-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Description</th>
                    <th>Keywords</th>
                    <th>Components (in order)</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="rulesTableBody">
                {% for rule in config.product_rules %}
                <tr>
                    <td>{{ rule.id }}</td>
                    <td>{{ rule.description }}</td>
                    <td>{{ rule.keywords|join(', ') }}</td>
                    <td>
                        {% if rule.components %}
                            {% for comp in rule.components|sort(attribute='order') %}
                                {{ comp.order }}. {{ comp.type|title }}{% if comp.label %} - {{ comp.label }}{% endif %}: 
                                {% if comp.calc_type == 'flat' %}${{ comp.value }}{% else %}{{ comp.value }}%{% endif %}
                                {% if not loop.last %}<br>{% endif %}
                            {% endfor %}
                            <br><em style="color: #666;">Revenue: (calculated as remainder)</em>
                        {% else %}
                            (Legacy format - please recreate)
                        {% endif %}
                    </td>
                    <td>
                        <button onclick="editRule({{ rule.id }})" data-rule='{{ rule|tojson }}' style="margin-right: 5px;">Edit</button>
                        <button class="danger" onclick="deleteRule({{ rule.id }})">Delete</button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <!-- Configuration Section -->
    <div class="container">
        <h2>Configuration</h2>
        <form id="configForm">
            <div class="form-group">
                <label>Shop Domain:</label>
                <input type="text" name="shop_domain" value="{{ config.shopify.shop_domain }}" placeholder="myshop.myshopify.com">
            </div>
            <div class="form-group">
                <label>Access Token:</label>
                <input type="password" name="access_token" value="{{ config.shopify.access_token }}" placeholder="Leave empty for dummy data">
            </div>
            <div class="form-group">
                <label>API Version:</label>
                <input type="text" name="api_version" value="{{ config.shopify.api_version }}">
            </div>
            <div class="form-group">
                <label>Export Save Location:</label>
                <input type="text" name="export_path" value="{{ config.get('export_path', '') }}" placeholder="Leave empty for browser default (Downloads folder)">
                <small style="color: #666; display: block; margin-top: 5px;">Files will be saved to your browser's default download location if not specified.</small>
            </div>
            
            <h3 style="margin-top: 30px; border-top: 2px solid #eee; padding-top: 20px;">Google Sheets Export</h3>
            <div class="form-group">
                {% if config.google_sheets.get('enabled') and config.google_sheets.get('user_email') %}
                <div style="padding: 10px; background: #d4edda; border-radius: 4px; margin-bottom: 10px;">
                    <strong>✓ Connected as:</strong> {{ config.google_sheets.user_email }}
                    <button onclick="disconnectGoogle()" style="margin-left: 10px; padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">Disconnect</button>
                </div>
                {% else %}
                <div style="padding: 10px; background: #fff3cd; border-radius: 4px; margin-bottom: 10px;">
                    <strong>Not connected.</strong> Click the button below to sign in with Google.
                </div>
                <a href="/auth/google" style="display: inline-block; padding: 10px 20px; background: #4285f4; color: white; text-decoration: none; border-radius: 4px; margin-bottom: 15px;">
                    Sign in with Google
                </a>
                {% endif %}
            </div>
            <div class="form-group">
                <label>Spreadsheet ID (optional):</label>
                <input type="text" name="gsheets_spreadsheet_id" id="gsheets_spreadsheet_id" value="{{ config.google_sheets.get('spreadsheet_id', '') }}" placeholder="Leave empty to create a new spreadsheet each time">
                <small style="color: #666; display: block; margin-top: 5px;">If provided, exports will be added to this spreadsheet. If empty, a new spreadsheet will be created for each export.</small>
            </div>
            
            <button type="submit">Save Configuration</button>
        </form>
    </div>
    
    <!-- Deduction Sequence Reference Section -->
    <div class="container">
        <h2>Deduction Sequence Reference</h2>
        <p style="color: #666; margin-bottom: 20px;">
            This shows the order of operations for calculating financial breakdowns from sale price. Each step works on the remaining amount from the previous step.
        </p>
        
        <div class="deduction-sequence-box">
            <div class="deduction-step" style="border-left-color: #007AFF;">
                <div style="flex: 0 0 30px; text-align: center; font-weight: bold; color: #007AFF;">1</div>
                <div style="flex: 1;">
                    <strong>Original Sale Price</strong>
                    <div style="color: #666; font-size: 0.9em; margin-top: 5px;">Sum of all line item prices × quantities</div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 10px 0; color: #666;">↓</div>
            
            <div class="deduction-step" style="border-left-color: #dc3545;">
                <div style="flex: 0 0 30px; text-align: center; font-weight: bold; color: #dc3545;">2</div>
                <div style="flex: 1;">
                    <strong>Subtract Refunds (if any)</strong>
                    <div style="color: #666; font-size: 0.9em; margin-top: 5px;">Partial refunds only (fully refunded orders are excluded)</div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 10px 0; color: #666;">↓</div>
            
            <div class="deduction-step" style="border-left-color: #28a745;">
                <div style="flex: 0 0 30px; text-align: center; font-weight: bold; color: #28a745;">3</div>
                <div style="flex: 1;">
                    <strong>Subtract Discounts</strong>
                    <div style="color: #666; font-size: 0.9em; margin-top: 5px;">Percentage discounts and/or fixed amount discounts</div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 10px 0; color: #666;">↓</div>
            
            <div class="deduction-step" style="border-left-color: #ffc107;">
                <div style="flex: 0 0 30px; text-align: center; font-weight: bold; color: #ffc107;">4</div>
                <div style="flex: 1;">
                    <strong>Subtract Total Cost</strong>
                    <div style="color: #666; font-size: 0.9em; margin-top: 5px;">Inventory costs from line items</div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 10px 0; color: #666;">↓</div>
            
            <div class="deduction-step" style="border-left-color: #6f42c1;">
                <div style="flex: 0 0 30px; text-align: center; font-weight: bold; color: #6f42c1;">5</div>
                <div style="flex: 1;">
                    <strong>Apply Allocation Components</strong>
                    <div style="color: #666; font-size: 0.9em; margin-top: 5px;">Applied sequentially in rule order: Investor → Consigner → Vendor (each calculated from remaining amount)</div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 10px 0; color: #666;">↓</div>
            
            <div class="deduction-step" style="border-left-color: #e83e8c;">
                <div style="flex: 0 0 30px; text-align: center; font-weight: bold; color: #e83e8c;">6</div>
                <div style="flex: 1;">
                    <strong>Calculate Taxes</strong>
                    <div style="color: #666; font-size: 0.9em; margin-top: 5px;">
                        Applied sequentially from Shopify tax data:
                        <div style="margin-top: 5px; padding-left: 15px;">
                            • State Taxes (first tax line)<br>
                            • Federal Taxes (second tax line, if present)<br>
                            • Additional Taxes (if any)
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 10px 0; color: #666;">↓</div>
            
            <div class="deduction-step" style="border-left-color: #17a2b8;">
                <div style="flex: 0 0 30px; text-align: center; font-weight: bold; color: #17a2b8;">7</div>
                <div style="flex: 1;">
                    <strong>Revenue</strong>
                    <div style="color: #666; font-size: 0.9em; margin-top: 5px;">Final remaining amount after all deductions</div>
                </div>
            </div>
        </div>
        
        <div class="deduction-notes">
            <strong>Important Notes:</strong>
            <ul style="margin: 10px 0 0 20px; color: #666;">
                <li>Refunds are applied <strong>first</strong>, before discounts and all other deductions</li>
                <li>Fully refunded orders are <strong>excluded</strong> from calculations entirely</li>
                <li>Partially refunded orders are processed with the refund amount subtracted from the sale price</li>
                <li>Discounts are calculated on the sale price <strong>after refunds</strong></li>
                <li>Allocation components are applied <strong>sequentially</strong> in the order specified by your rules</li>
                <li>Each component is calculated from the <strong>remaining amount</strong> after previous deductions</li>
                <li>Taxes are calculated from Shopify's tax data and applied to the remaining amount</li>
                <li>Revenue is automatically calculated as the <strong>residual</strong> after all deductions</li>
            </ul>
        </div>
    </div>
    
    <script>
        // Dark mode functionality
        function initDarkMode() {
            const darkMode = localStorage.getItem('darkMode') === 'true';
            if (darkMode) {
                document.body.classList.add('dark-mode');
                updateDarkModeButton(true);
            }
        }
        
        function toggleDarkMode() {
            const isDark = document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', isDark);
            updateDarkModeButton(isDark);
        }
        
        function updateDarkModeButton(isDark) {
            const button = document.getElementById('darkModeToggle');
            if (button) {
                button.textContent = isDark ? '☀️ Light Mode' : '🌙 Dark Mode';
            }
        }
        
        // Initialize dark mode on page load
        initDarkMode();
        
        let ordersData = [];  // Unmatched orders for display
        let allOrdersData = [];  // All orders for export
        
        document.getElementById('configForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            // Add Google Sheets spreadsheet_id
            data.gsheets_spreadsheet_id = document.getElementById('gsheets_spreadsheet_id').value;
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.success) {
                alert('Configuration saved!');
                location.reload();
            }
        });
        
        // Check for OAuth callback messages
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('google_auth') === 'success') {
            alert('Successfully connected to Google! You can now export to Google Sheets.');
            // Remove query params from URL
            window.history.replaceState({}, document.title, window.location.pathname);
        } else if (urlParams.get('error')) {
            const error = urlParams.get('error');
            alert('Error: ' + error);
            window.history.replaceState({}, document.title, window.location.pathname);
        }
        
        let componentCounter = 0;
        const componentTypes = ['revenue', 'investor', 'consigner', 'vendor'];
        
        function addComponent(type = '', calcType = 'percentage', value = 0, order = null, label = '') {
            const list = document.getElementById('componentsList');
            const compId = componentCounter++;
            const compOrder = order !== null ? order : (list.children.length + 1);
            
            const div = document.createElement('div');
            div.className = 'component-item';
            div.id = `component-${compId}`;
            div.innerHTML = `
                <span class="component-order">${compOrder}</span>
                <select name="comp_type_${compId}" required>
                    <option value="investor" ${type === 'investor' ? 'selected' : ''}>Investor</option>
                    <option value="consigner" ${type === 'consigner' ? 'selected' : ''}>Consigner</option>
                    <option value="vendor" ${type === 'vendor' ? 'selected' : ''}>Vendor</option>
                </select>
                <input type="text" name="label_${compId}" value="${label || ''}" placeholder="Label (optional)" style="flex: 1;" title="Optional label to distinguish multiple components of the same type (e.g., 'Bank A', 'Vendor 1')">
                <select name="calc_type_${compId}" required>
                    <option value="percentage" ${calcType === 'percentage' ? 'selected' : ''}>Percentage</option>
                    <option value="flat" ${calcType === 'flat' ? 'selected' : ''}>Flat Amount</option>
                </select>
                <input type="number" name="value_${compId}" step="0.01" value="${value}" required placeholder="Value">
                <input type="hidden" name="order_${compId}" value="${compOrder}">
                <div class="move-buttons">
                    <button type="button" onclick="moveComponent(${compId}, -1)">↑</button>
                    <button type="button" onclick="moveComponent(${compId}, 1)">↓</button>
                </div>
                <button type="button" onclick="removeComponent(${compId})" class="danger">Remove</button>
            `;
            list.appendChild(div);
            updateComponentOrders();
        }
        
        function removeComponent(compId) {
            document.getElementById(`component-${compId}`).remove();
            updateComponentOrders();
        }
        
        function moveComponent(compId, direction) {
            const list = document.getElementById('componentsList');
            const items = Array.from(list.children);
            const currentIndex = items.findIndex(item => item.id === `component-${compId}`);
            if (currentIndex === -1) return;
            
            const newIndex = currentIndex + direction;
            if (newIndex < 0 || newIndex >= items.length) return;
            
            if (direction < 0) {
                list.insertBefore(items[currentIndex], items[newIndex]);
            } else {
                list.insertBefore(items[currentIndex], items[newIndex].nextSibling);
            }
            updateComponentOrders();
        }
        
        function updateComponentOrders() {
            const list = document.getElementById('componentsList');
            const items = Array.from(list.children);
            items.forEach((item, index) => {
                const orderInput = item.querySelector('input[type="hidden"]');
                const orderSpan = item.querySelector('.component-order');
                const order = index + 1;
                if (orderInput) orderInput.value = order;
                if (orderSpan) orderSpan.textContent = order;
            });
        }
        
        // Add default components on page load
        // Note: Revenue is automatically calculated as remainder, not a component
        // Note: Taxes are calculated from Shopify data after all deductions, not as components
        document.addEventListener('DOMContentLoaded', () => {
            addComponent('investor', 'percentage', 0);
            addComponent('consigner', 'percentage', 0);
        });
        
        document.getElementById('ruleForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const components = [];
            
            // Collect all components
            const componentItems = document.querySelectorAll('.component-item');
            componentItems.forEach((item, index) => {
                const compId = item.id.split('-')[1];
                components.push({
                    type: formData.get(`comp_type_${compId}`),
                    label: formData.get(`label_${compId}`) || '',
                    calc_type: formData.get(`calc_type_${compId}`),
                    value: parseFloat(formData.get(`value_${compId}`)),
                    order: parseInt(formData.get(`order_${compId}`))
                });
            });
            
            const ruleId = formData.get('rule_id');
            const data = {
                description: formData.get('description'),
                keywords: formData.get('keywords').split(',').map(k => k.trim()),
                components: components
            };
            
            const url = ruleId ? `/api/rules/${ruleId}` : '/api/rules';
            const method = ruleId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.success) {
                alert(ruleId ? 'Rule updated!' : 'Rule added!');
                location.reload();
            } else {
                alert('Error: ' + (result.error || 'Unknown error'));
            }
        });
        
        function editRule(id) {
            // Find the button that was clicked and get rule data from data attribute
            const buttons = document.querySelectorAll(`button[onclick="editRule(${id})"]`);
            const button = buttons[0];
            const ruleJson = button.getAttribute('data-rule');
            const rule = JSON.parse(ruleJson);
            
            // Populate form with rule data
            document.getElementById('ruleId').value = id;
            document.getElementById('ruleDescription').value = rule.description || '';
            document.getElementById('ruleKeywords').value = (rule.keywords || []).join(', ');
            
            // Clear existing components
            document.getElementById('componentsList').innerHTML = '';
            
            // Add components from rule
            if (rule.components && rule.components.length > 0) {
                // Sort components by order
                const sortedComponents = [...rule.components].sort((a, b) => (a.order || 0) - (b.order || 0));
                sortedComponents.forEach(comp => {
                    addComponent(comp.type, comp.calc_type, comp.value, comp.order, comp.label || '');
                });
            } else {
                // Add default empty components if none exist
                addComponent('investor', 'percentage', 0);
                addComponent('consigner', 'percentage', 0);
            }
            
            // Update form title and button
            document.getElementById('ruleFormTitle').textContent = 'Edit Rule';
            document.getElementById('submitRuleBtn').textContent = 'Update Rule';
            document.getElementById('cancelEditBtn').style.display = 'inline-block';
            
            // Scroll to form
            document.querySelector('.rule-form').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        function cancelEdit() {
            // Reset form
            document.getElementById('ruleForm').reset();
            document.getElementById('ruleId').value = '';
            document.getElementById('componentsList').innerHTML = '';
            
            // Reset form title and button
            document.getElementById('ruleFormTitle').textContent = 'Add New Rule';
            document.getElementById('submitRuleBtn').textContent = 'Add Rule';
            document.getElementById('cancelEditBtn').style.display = 'none';
            
            // Add default components
            addComponent('investor', 'percentage', 0);
            addComponent('consigner', 'percentage', 0);
        }
        
        async function deleteRule(id) {
            if (!confirm('Are you sure you want to delete this rule?')) return;
            const response = await fetch(`/api/rules/${id}`, {method: 'DELETE'});
            const result = await response.json();
            if (result.success) {
                location.reload();
            }
        }
        
        // Quick date range functions
        function setLast30Days() {
            const today = new Date();
            const startDate = new Date(today);
            startDate.setDate(today.getDate() - 30);
            document.getElementById('start_date').value = formatDate(startDate);
            document.getElementById('end_date').value = formatDate(today);
        }
        
        function setLastMonth() {
            const today = new Date();
            // First day of current month
            const firstDayCurrent = new Date(today.getFullYear(), today.getMonth(), 1);
            // Last day of previous month
            const lastDayPrevious = new Date(firstDayCurrent);
            lastDayPrevious.setDate(0);
            // First day of previous month
            const firstDayPrevious = new Date(lastDayPrevious.getFullYear(), lastDayPrevious.getMonth(), 1);
            
            document.getElementById('start_date').value = formatDate(firstDayPrevious);
            document.getElementById('end_date').value = formatDate(lastDayPrevious);
        }
        
        function setLastWeek() {
            const today = new Date();
            const startDate = new Date(today);
            startDate.setDate(today.getDate() - 7);
            document.getElementById('start_date').value = formatDate(startDate);
            document.getElementById('end_date').value = formatDate(today);
        }
        
        function setThisMonthToDate() {
            const today = new Date();
            const firstDayMonth = new Date(today.getFullYear(), today.getMonth(), 1);
            document.getElementById('start_date').value = formatDate(firstDayMonth);
            document.getElementById('end_date').value = formatDate(today);
        }
        
        function formatDate(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }
        
        document.getElementById('fetchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const response = await fetch('/api/fetch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    start_date: formData.get('start_date'),
                    end_date: formData.get('end_date')
                })
            });
            const result = await response.json();
            if (result.success) {
                ordersData = result.breakdowns;  // Unmatched orders for display
                allOrdersData = result.all_breakdowns || result.breakdowns;  // All orders for export
                displayResults(result.breakdowns, result.stats);
                updateExportButton(result.stats);
            } else {
                document.getElementById('results').innerHTML = `<div class="error">${result.error}</div>`;
                // Reset export button on error
                const exportBtn = document.getElementById('exportBtn');
                exportBtn.disabled = true;
                exportBtn.className = '';
                ordersData = [];
                allOrdersData = [];
            }
        });
        
        function updateExportButton(stats) {
            const exportBtn = document.getElementById('exportBtn');
            const exportGSheetsBtn = document.getElementById('exportGSheetsBtn');
            
            // Remove all state classes
            exportBtn.classList.remove('export-yellow', 'export-green');
            
            if (!stats || stats.total === 0) {
                // No orders fetched or no orders
                exportBtn.disabled = true;
                exportBtn.className = '';
                exportGSheetsBtn.disabled = true;
            } else if (stats.unmatched > 0) {
                // There are unmatched orders - yellow
                exportBtn.disabled = false;
                exportBtn.className = 'export-yellow';
                exportGSheetsBtn.disabled = false;
                exportGSheetsBtn.className = 'export-yellow';
            } else {
                // All orders matched - green
                exportBtn.disabled = false;
                exportBtn.className = 'export-green';
                exportGSheetsBtn.disabled = false;
                exportGSheetsBtn.className = 'export-green';
            }
        }
        
        function displayResults(breakdowns, stats) {
            const resultsDiv = document.getElementById('results');
            let html = '';
            
            // Display statistics
            if (stats) {
                // Set background color based on unmatched count
                const bgColor = stats.unmatched > 0 ? '#fff3cd' : '#d4edda'; // Yellow if unmatched, green if 0
                const textColor = stats.unmatched > 0 ? '#856404' : '#28a745'; // Dark yellow text if unmatched, green if 0
                html += `<div class="success" style="margin-bottom: 20px; background: ${bgColor}; color: ${textColor};">
                    <strong>Order Statistics:</strong><br>
                    Total Orders: ${stats.total}<br>
                    Matched Rules: ${stats.matched}<br>
                    Unmatched (shown below): ${stats.unmatched}
                </div>`;
            }
            
            if (breakdowns.length === 0) {
                html += '<div class="success">All orders matched a rule! No unmatched orders to display.</div>';
            } else {
                html += '<div class="results">';
                breakdowns.forEach(b => {
                    let breakdownHtml = '';
                    if (b.component_breakdown && b.component_breakdown.length > 0) {
                        breakdownHtml = '<br>Breakdown: ' + b.component_breakdown.join(' | ') + '<br>';
                    }
                    let metadataHtml = '';
                    if (b.vendor || b.product_type || b.tags || b.collections) {
                        metadataHtml = '<br><small style="color: #666;">';
                        if (b.vendor) metadataHtml += `Vendor: ${b.vendor} | `;
                        if (b.product_type) metadataHtml += `Type: ${b.product_type} | `;
                        if (b.tags) metadataHtml += `Tags: ${b.tags} | `;
                        if (b.collections) metadataHtml += `Collections: ${b.collections}`;
                        metadataHtml = metadataHtml.replace(/\s*\|\s*$/, ''); // Remove trailing |
                        metadataHtml += '</small>';
                    }
                    let shopifyTaxHtml = '';
                    if (b.shopify_tax_breakdown && b.shopify_tax_breakdown.length > 0) {
                        const taxBreakdown = Array.isArray(b.shopify_tax_breakdown) 
                            ? b.shopify_tax_breakdown.join(' | ') 
                            : b.shopify_tax_breakdown;
                        shopifyTaxHtml = `<br><small style="color: #0066cc;"><strong>Shopify Taxes:</strong> ${taxBreakdown}</small>`;
                    }
                    
                    // Only show financial breakdown for matched orders
                    const isMatched = b.matched_rules && b.matched_rules !== "No match";
                    let financialBreakdownHtml = '';
                    if (isMatched) {
                        financialBreakdownHtml = `<br>Revenue: $${b.revenue.toFixed(2)} | Investor: $${b.investor.toFixed(2)} | State Taxes: $${b.state_taxes.toFixed(2)} | Federal Taxes: $${b.federal_taxes.toFixed(2)} | Consigner: $${b.consigner.toFixed(2)} | Vendor: $${(b.vendor || 0).toFixed(2)}${breakdownHtml}`;
                    }
                    
                    html += `<div class="order-item">
                        <strong>Order #${b.order_number}</strong> - ${b.date}<br>
                        Customer: ${b.customer}<br>
                        Products: ${b.products}${metadataHtml}<br>
                        Total: $${b.order_total.toFixed(2)} | Cost: $${(b.total_cost || 0).toFixed(2)}${shopifyTaxHtml}${financialBreakdownHtml}
                    </div>`;
                });
                html += '</div>';
            }
            
            resultsDiv.innerHTML = html;
        }
        
        async function exportCSV() {
            // Use all orders for export (matched + unmatched)
            const ordersToExport = allOrdersData.length > 0 ? allOrdersData : ordersData;
            
            if (ordersToExport.length === 0) {
                alert('No orders to export');
                return;
            }
            // Get date range from form
            const startDate = document.getElementById('start_date').value;
            const endDate = document.getElementById('end_date').value;
            
            console.log('Export dates:', startDate, endDate); // Debug
            
            const response = await fetch('/api/export', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    breakdowns: ordersToExport,
                    start_date: startDate,
                    end_date: endDate
                })
            });
            if (response.ok) {
                // Get filename from Content-Disposition header
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'PAYOUTS-export.CSV';
                
                if (contentDisposition) {
                    // Try different patterns for filename extraction
                    let filenameMatch = contentDisposition.match(/filename="(.+)"/);
                    if (!filenameMatch) {
                        filenameMatch = contentDisposition.match(/filename=([^;]+)/);
                    }
                    if (filenameMatch) {
                        filename = filenameMatch[1].trim().replace(/^["']|["']$/g, '');
                    }
                }
                
                // If we still have the default and we have dates, generate filename client-side as fallback
                if (filename === 'PAYOUTS-export.CSV' && startDate && endDate) {
                    try {
                        const start = new Date(startDate);
                        const end = new Date(endDate);
                        
                        // Check if it's a full month
                        if (start.getDate() === 1 && 
                            start.getMonth() === end.getMonth() && 
                            start.getFullYear() === end.getFullYear()) {
                            // Check if end is last day of month
                            const lastDay = new Date(start.getFullYear(), start.getMonth() + 1, 0).getDate();
                            if (end.getDate() === lastDay) {
                                const monthNames = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
                                filename = `PAYOUTS-${monthNames[start.getMonth()]}-${start.getFullYear()}.CSV`;
                            } else {
                                filename = `PAYOUTS-${startDate}_to_${endDate}.CSV`;
                            }
                        } else {
                            filename = `PAYOUTS-${startDate}_to_${endDate}.CSV`;
                        }
                    } catch (e) {
                        console.error('Error generating filename:', e);
                    }
                }
                
                // Ensure filename ends with .CSV
                if (!filename.toUpperCase().endsWith('.CSV')) {
                    filename = filename.replace(/\.[^.]*$/, '') + '.CSV';
                }
                
                console.log('Using filename:', filename); // Debug
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                window.URL.revokeObjectURL(url);
            } else {
                const result = await response.json();
                alert('Export failed: ' + (result.error || 'Unknown error'));
            }
        }
        
        async function disconnectGoogle() {
            if (!confirm('Are you sure you want to disconnect your Google account? You will need to sign in again to export to Google Sheets.')) {
                return;
            }
            const response = await fetch('/api/disconnect-google', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            });
            const result = await response.json();
            if (result.success) {
                alert('Google account disconnected successfully');
                location.reload();
            } else {
                alert('Error: ' + (result.error || 'Failed to disconnect'));
            }
        }
        
        async function exportGoogleSheets() {
            // Use all orders for export (matched + unmatched)
            const ordersToExport = allOrdersData.length > 0 ? allOrdersData : ordersData;
            
            if (ordersToExport.length === 0) {
                alert('No orders to export');
                return;
            }
            
            // Get spreadsheet ID from config form (optional)
            const spreadsheetId = document.getElementById('gsheets_spreadsheet_id').value.trim() || null;
            
            // Disable button during export
            const exportBtn = document.getElementById('exportGSheetsBtn');
            const originalText = exportBtn.textContent;
            exportBtn.disabled = true;
            exportBtn.textContent = 'Exporting...';
            
            try {
                const response = await fetch('/api/export-google-sheets', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        breakdowns: ordersToExport,
                        spreadsheet_id: spreadsheetId
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    const message = result.message || 'Successfully exported to Google Sheets!';
                    const url = result.spreadsheet_url;
                    if (url) {
                        if (confirm(message + '\\n\\nOpen spreadsheet in new tab?')) {
                            window.open(url, '_blank');
                        }
                    } else {
                        alert(message);
                    }
                } else {
                    alert('Export failed: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                alert('Export failed: ' + error.message);
            } finally {
                exportBtn.disabled = false;
                exportBtn.textContent = originalText;
            }
        }
    </script>
</body>
</html>
"""


@app.route('/health')
def health():
    """Health check endpoint for Render and other hosting platforms."""
    try:
        # Test database connection
        session = get_db_session()
        session.close()
        return jsonify({'status': 'ok', 'database': 'connected'}), 200
    except Exception as e:
        # App is running but database might not be connected
        return jsonify({'status': 'degraded', 'database': 'disconnected', 'error': str(e)}), 200


@app.route('/')
@login_required
def index():
    """Main page."""
    config = load_config()
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    return render_template_string(HTML_TEMPLATE, config=config, start_date=start_date, end_date=end_date, current_user=current_user)


@app.route('/api/config', methods=['POST'])
@login_required
def save_config_api():
    """Save configuration."""
    try:
        config = load_config()
        data = request.json
        config['shopify']['shop_domain'] = data.get('shop_domain', '')
        config['shopify']['access_token'] = data.get('access_token', '')
        config['shopify']['api_version'] = data.get('api_version', '2025-10')
        config['export_path'] = data.get('export_path', '')
        # Update Google Sheets spreadsheet_id
        if 'google_sheets' not in config:
            config['google_sheets'] = {}
        config['google_sheets']['spreadsheet_id'] = data.get('gsheets_spreadsheet_id', '')
        save_config(config)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/rules', methods=['POST'])
@login_required
def add_rule():
    """Add a new rule."""
    try:
        session = get_db_session()
        try:
            # Get max rule_id for this user
            max_rule = session.query(UserRule).filter_by(user_id=current_user.id).order_by(UserRule.rule_id.desc()).first()
            new_id = (max_rule.rule_id + 1) if max_rule else 1
            
            data = request.json
            
            # Validate components
            components = data.get('components', [])
            if not components:
                return jsonify({'success': False, 'error': 'At least one component is required'}), 400
            
            # Ensure all components have required fields
            for comp in components:
                if 'type' not in comp or 'calc_type' not in comp or 'value' not in comp or 'order' not in comp:
                    return jsonify({'success': False, 'error': 'All components must have type, calc_type, value, and order'}), 400
            
            # Create new rule
            rule = UserRule(
                user_id=current_user.id,
                rule_id=new_id,
                description=data['description'],
                keywords=data['keywords'],
                components=components
            )
            session.add(rule)
            session.commit()
            return jsonify({'success': True})
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/rules/<int:rule_id>', methods=['PUT', 'DELETE'])
@login_required
def update_or_delete_rule(rule_id):
    """Update or delete a rule."""
    try:
        session = get_db_session()
        try:
            # Find rule for this user
            rule = session.query(UserRule).filter_by(user_id=current_user.id, rule_id=rule_id).first()
            
            if request.method == 'DELETE':
                if not rule:
                    return jsonify({'success': False, 'error': 'Rule not found'}), 404
                session.delete(rule)
                session.commit()
                return jsonify({'success': True})
            else:
                # Update rule
                if not rule:
                    return jsonify({'success': False, 'error': 'Rule not found'}), 404
                
                data = request.json
                
                # Validate components
                components = data.get('components', [])
                if not components:
                    return jsonify({'success': False, 'error': 'At least one component is required'}), 400
                
                # Ensure all components have required fields
                for comp in components:
                    if 'type' not in comp or 'calc_type' not in comp or 'value' not in comp or 'order' not in comp:
                        return jsonify({'success': False, 'error': 'All components must have type, calc_type, value, and order'}), 400
                
                # Update the rule
                rule.description = data['description']
                rule.keywords = data['keywords']
                rule.components = components
                rule.updated_at = datetime.utcnow()
                session.commit()
                return jsonify({'success': True})
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/fetch', methods=['POST'])
@login_required
def fetch_orders_api():
    """Fetch orders."""
    try:
        data = request.json
        config = load_config()
        
        shop_domain = config['shopify']['shop_domain']
        access_token = config['shopify']['access_token']
        api_version = config['shopify']['api_version']
        
        orders = fetch_orders(shop_domain, access_token, data['start_date'], data['end_date'], api_version)
        
        # Load rules from database
        rules = config.get('product_rules', [])
        # Convert to format expected by RuleEngine
        rule_list = []
        for rule in rules:
            rule_list.append({
                'id': rule.get('id'),
                'keywords': rule.get('keywords', []),
                'description': rule.get('description', ''),
                'components': rule.get('components', [])
            })
        engine = RuleEngine(rule_list)
        breakdowns = engine.process_orders(orders)
        
        # Calculate statistics: matched vs unmatched
        total_orders = len(breakdowns)
        matched_orders = [b for b in breakdowns if b.get('matched_rules', 'No match') != 'No match']
        unmatched_orders = [b for b in breakdowns if b.get('matched_rules', 'No match') == 'No match']
        
        stats = {
            'total': total_orders,
            'matched': len(matched_orders),
            'unmatched': len(unmatched_orders)
        }
        
        # Return unmatched orders for display, but also all orders for export
        return jsonify({
            'success': True, 
            'breakdowns': unmatched_orders,
            'all_breakdowns': breakdowns,  # All orders for export
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/export', methods=['POST'])
@login_required
def export_csv_api():
    """Export to CSV."""
    try:
        data = request.json
        breakdowns = data['breakdowns']
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        
        # Debug logging
        print(f"Export request - start_date: {start_date}, end_date: {end_date}")
        
        # Generate filename with date range
        # If it's a full month, use: PAYOUTS-MON-YYYY.CSV
        # Otherwise use: PAYOUTS-YYYY-MM-DD_to_YYYY-MM-DD.CSV
        filename = "PAYOUTS-export.CSV"  # Default fallback
        
        if start_date and end_date:
            try:
                from datetime import datetime
                from calendar import monthrange
                
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                
                # Check if it's a full month (first day of month to last day of month)
                if (start_dt.day == 1 and 
                    end_dt.month == start_dt.month and 
                    end_dt.year == start_dt.year):
                    # Check if end_date is the last day of the month
                    last_day = monthrange(start_dt.year, start_dt.month)[1]
                    if end_dt.day == last_day:
                        # It's a full month - use month name format
                        month_name = start_dt.strftime("%b").upper()  # OCT, NOV, etc.
                        year = start_dt.year
                        filename = f"PAYOUTS-{month_name}-{year}.CSV"
                    else:
                        # Not a full month
                        filename = f"PAYOUTS-{start_date}_to_{end_date}.CSV"
                else:
                    # Not a full month
                    filename = f"PAYOUTS-{start_date}_to_{end_date}.CSV"
            except (ValueError, AttributeError) as e:
                # If date parsing fails, use date range format if we have dates
                if start_date and end_date:
                    filename = f"PAYOUTS-{start_date}_to_{end_date}.CSV"
                # Otherwise keep default
        
        import tempfile
        import os
        config = load_config()
        export_path = config.get('export_path', '')
        
        # If export_path is set, use it; otherwise use temp file (browser will download)
        if export_path and os.path.isdir(export_path):
            # Save to specified directory
            filepath = os.path.join(export_path, filename)
            export_to_csv(breakdowns, filepath)
            return send_file(filepath, as_attachment=True, download_name=filename, mimetype='text/csv')
        else:
            # Use temp file (browser download)
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
                # Need to close and reopen for export_to_csv to work
                temp_path = f.name
            export_to_csv(breakdowns, temp_path)
            return send_file(temp_path, as_attachment=True, download_name=filename, mimetype='text/csv')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


def get_oauth_config():
    """Get OAuth client configuration from environment or config."""
    client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    
    # Try to load from config.json as fallback
    if not client_id or not client_secret:
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r") as f:
                    config = json.load(f)
                    oauth_config = config.get('google_oauth', {})
                    client_id = client_id or oauth_config.get('client_id', '')
                    client_secret = client_secret or oauth_config.get('client_secret', '')
        except:
            pass
    
    return client_id, client_secret


@app.route('/auth/google')
@login_required
def google_auth():
    """Initiate Google OAuth flow."""
    if not OAUTH_AVAILABLE:
        return jsonify({'success': False, 'error': 'OAuth libraries not installed'}), 400
    
    client_id, client_secret = get_oauth_config()
    if not client_id or not client_secret:
        return jsonify({'success': False, 'error': 'Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.'}), 400
    
    # OAuth scopes
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/userinfo.email'
    ]
    
    # Create OAuth flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [request.url_root.rstrip('/') + '/auth/google/callback']
            }
        },
        scopes=SCOPES
    )
    
    # Determine redirect URI
    redirect_uri = request.url_root.rstrip('/') + '/auth/google/callback'
    flow.redirect_uri = redirect_uri
    
    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Force consent to get refresh token
    )
    
    # Store state in session
    session['oauth_state'] = state
    session['oauth_user_id'] = current_user.id
    
    return redirect(authorization_url)


@app.route('/auth/google/callback')
@login_required
def google_auth_callback():
    """Handle Google OAuth callback."""
    if not OAUTH_AVAILABLE:
        return redirect(url_for('index') + '?error=oauth_not_available')
    
    # Verify state
    state = session.get('oauth_state')
    if not state or state != request.args.get('state'):
        return redirect(url_for('index') + '?error=invalid_state')
    
    # Verify user
    user_id = session.get('oauth_user_id')
    if not user_id or user_id != current_user.id:
        return redirect(url_for('index') + '?error=invalid_user')
    
    client_id, client_secret = get_oauth_config()
    if not client_id or not client_secret:
        return redirect(url_for('index') + '?error=oauth_not_configured')
    
    try:
        # Create OAuth flow
        SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/userinfo.email'
        ]
        redirect_uri = request.url_root.rstrip('/') + '/auth/google/callback'
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=SCOPES,
            state=state
        )
        flow.redirect_uri = redirect_uri
        
        # Fetch token
        flow.fetch_token(authorization_response=request.url)
        
        # Get credentials
        creds = flow.credentials
        
        # Get user info (optional - for display purposes)
        user_email = ''
        try:
            service = build('oauth2', 'v2', credentials=creds)
            user_info = service.userinfo().get().execute()
            user_email = user_info.get('email', '')
        except Exception as e:
            # If we can't get email, continue anyway - it's just for display
            print(f"Warning: Could not fetch user email: {e}")
            user_email = ''
        
        # Save token to database
        db_session = get_db_session()
        try:
            user_config = db_session.query(UserConfig).filter_by(user_id=current_user.id).first()
            if not user_config:
                user_config = UserConfig(user_id=current_user.id)
                db_session.add(user_config)
            
            # Convert credentials to dict for storage
            # Note: Google may add 'openid' scope automatically - this is normal
            token_dict = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes  # May include 'openid' which is fine
            }
            
            user_config.gsheets_oauth_token = json.dumps(token_dict)
            user_config.gsheets_user_email = user_email
            user_config.updated_at = datetime.utcnow()
            
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            return redirect(url_for('index') + '?error=save_failed')
        finally:
            db_session.close()
        
        # Clean up session
        session.pop('oauth_state', None)
        session.pop('oauth_user_id', None)
        
        return redirect(url_for('index') + '?google_auth=success')
        
    except Exception as e:
        return redirect(url_for('index') + f'?error={str(e)}')


@app.route('/api/disconnect-google', methods=['POST'])
@login_required
def disconnect_google():
    """Disconnect Google OAuth by clearing stored tokens."""
    try:
        db_session = get_db_session()
        try:
            user_config = db_session.query(UserConfig).filter_by(user_id=current_user.id).first()
            if user_config:
                user_config.gsheets_oauth_token = None
                user_config.gsheets_user_email = None
                user_config.updated_at = datetime.utcnow()
                db_session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db_session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            db_session.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/export-google-sheets', methods=['POST'])
@login_required
def export_google_sheets_api():
    """Export to Google Sheets."""
    try:
        if not OAUTH_AVAILABLE:
            return jsonify({'success': False, 'error': 'OAuth libraries not installed. Please install: pip install google-auth-oauthlib'}), 400
        
        data = request.json
        breakdowns = data.get('breakdowns', [])
        spreadsheet_id = data.get('spreadsheet_id', '') or None
        
        # Get user's OAuth token
        db_session = get_db_session()
        try:
            user_config = db_session.query(UserConfig).filter_by(user_id=current_user.id).first()
            if not user_config or not user_config.gsheets_oauth_token:
                return jsonify({'success': False, 'error': 'Not authenticated with Google. Please sign in with Google first.'}), 400
            
            oauth_token_json = user_config.gsheets_oauth_token
            if spreadsheet_id is None:
                spreadsheet_id = user_config.gsheets_spreadsheet_id or None
        finally:
            db_session.close()
        
        # Get OAuth client credentials for token refresh
        client_id, client_secret = get_oauth_config()
        
        # Call export function
        result = export_to_google_sheets(
            breakdowns=breakdowns,
            oauth_token_json=oauth_token_json,
            spreadsheet_id=spreadsheet_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # If export succeeded, check if we need to update stored token (e.g., scopes changed)
        if result.get('success'):
            # Check if token was updated (e.g., scopes changed to include openid)
            updated_token = result.get('updated_token')
            if updated_token:
                db_session = get_db_session()
                try:
                    user_config = db_session.query(UserConfig).filter_by(user_id=current_user.id).first()
                    if user_config:
                        user_config.gsheets_oauth_token = json.dumps(updated_token)
                        db_session.commit()
                finally:
                    db_session.close()
            
            # If export succeeded and we got a new spreadsheet_id, save it
            if result.get('spreadsheet_id'):
                db_session = get_db_session()
                try:
                    user_config = db_session.query(UserConfig).filter_by(user_id=current_user.id).first()
                    if user_config and not user_config.gsheets_spreadsheet_id:
                        user_config.gsheets_spreadsheet_id = result['spreadsheet_id']
                        db_session.commit()
                finally:
                    db_session.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


def open_browser():
    """Open the browser after a short delay to ensure server is ready."""
    time.sleep(1.5)  # Wait for server to start
    url = "http://127.0.0.1:5001"
    
    # Try multiple methods to open browser (PyInstaller executables sometimes have issues)
    try:
        # Method 1: Use webbrowser module (works in most cases)
        webbrowser.open(url)
        print(f"Browser opened at {url}")
    except Exception as e:
        try:
            # Method 2: Use platform-specific command (more reliable in executables)
            if sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', url])
                print(f"Browser opened at {url} (via 'open' command)")
            elif sys.platform == 'win32':  # Windows
                subprocess.Popen(['start', url], shell=True)
                print(f"Browser opened at {url} (via 'start' command)")
            else:  # Linux
                subprocess.Popen(['xdg-open', url])
                print(f"Browser opened at {url} (via 'xdg-open' command)")
        except Exception as e2:
            print(f"Could not automatically open browser. Please manually navigate to: {url}")
            print(f"Error: {e2}")


if __name__ == '__main__':
    # Check if running in production (e.g., on a hosting platform)
    is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('PORT')
    
    if is_production:
        # Production mode - use environment port or default to 5000
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'  # Listen on all interfaces
        print(f"\nStarting production server on port {port}...")
        app.run(debug=False, host=host, port=port)
    else:
        # Development mode - localhost with auto-open browser
        print("\n" + "="*60)
        print("Shopify Order Categorization App")
        print("="*60)
        print("\nStarting web server...")
        print("The browser will open automatically...")
        print("If it doesn't, go to: http://127.0.0.1:5001")
        print("\nPress Ctrl+C to stop the server\n")
        
        # Open browser in a separate thread
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Run Flask app (set debug=False for production builds)
        app.run(debug=False, host='127.0.0.1', port=5001, use_reloader=False)

