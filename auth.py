"""
Authentication routes and user management.
"""

from flask import Blueprint, render_template_string, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, UserConfig, get_db_session, init_db
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

# Login template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Shopify Order Categorization</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 400px;
            margin: 100px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-top: 0;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #333;
        }
        input[type="text"], input[type="password"], input[type="email"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            background: #007AFF;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
        }
        button:hover {
            background: #0056b3;
        }
        .error {
            color: #dc3545;
            padding: 10px;
            background: #f8d7da;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .success {
            color: #28a745;
            padding: 10px;
            background: #d4edda;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .links {
            text-align: center;
            margin-top: 20px;
        }
        .links a {
            color: #007AFF;
            text-decoration: none;
        }
        .links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Shopify Order Categorization</h1>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        {% if message %}
        <div class="success">{{ message }}</div>
        {% endif %}
        <form method="POST" action="/login">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
        <div class="links">
            <a href="/register">Don't have an account? Register</a>
        </div>
    </div>
</body>
</html>
"""

# Register template
REGISTER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Register - Shopify Order Categorization</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 400px;
            margin: 100px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-top: 0;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
            color: #333;
        }
        input[type="text"], input[type="password"], input[type="email"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            background: #007AFF;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
        }
        button:hover {
            background: #0056b3;
        }
        .error {
            color: #dc3545;
            padding: 10px;
            background: #f8d7da;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .links {
            text-align: center;
            margin-top: 20px;
        }
        .links a {
            color: #007AFF;
            text-decoration: none;
        }
        .links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Create Account</h1>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST" action="/register">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label>Email:</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required minlength="6">
            </div>
            <div class="form-group">
                <label>Confirm Password:</label>
                <input type="password" name="confirm_password" required>
            </div>
            <button type="submit">Register</button>
        </form>
        <div class="links">
            <a href="/login">Already have an account? Login</a>
        </div>
    </div>
</body>
</html>
"""


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            error = 'Please enter both username and password'
        else:
            session = get_db_session()
            try:
                user = session.query(User).filter_by(username=username).first()
                if user and user.check_password(password):
                    login_user(user, remember=True)
                    session.close()
                    return redirect(url_for('index'))
                else:
                    error = 'Invalid username or password'
            except Exception as e:
                error = f'Login error: {str(e)}'
            finally:
                session.close()
    
    return render_template_string(LOGIN_TEMPLATE, error=error)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not email or not password:
            error = 'All fields are required'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters'
        elif password != confirm_password:
            error = 'Passwords do not match'
        else:
            session = get_db_session()
            try:
                # Check if username or email already exists
                existing_user = session.query(User).filter(
                    (User.username == username) | (User.email == email)
                ).first()
                
                if existing_user:
                    error = 'Username or email already exists'
                else:
                    # Create new user
                    user = User(username=username, email=email)
                    user.set_password(password)
                    session.add(user)
                    session.commit()
                    
                    # Create default config for user
                    user_config = UserConfig(user_id=user.id)
                    session.add(user_config)
                    session.commit()
                    
                    # Log in the new user
                    login_user(user, remember=True)
                    session.close()
                    return redirect(url_for('index'))
            except Exception as e:
                session.rollback()
                error = f'Registration error: {str(e)}'
            finally:
                session.close()
    
    return render_template_string(REGISTER_TEMPLATE, error=error)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout handler."""
    logout_user()
    return redirect(url_for('auth.login'))

