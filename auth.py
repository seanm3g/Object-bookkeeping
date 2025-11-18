"""
Authentication routes and user management.
"""

from flask import Blueprint, render_template_string, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from models import User, UserConfig, get_db_session, init_db
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)


def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

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
                    # Check if this is the first user (make them admin)
                    user_count = session.query(User).count()
                    is_first_user = user_count == 0
                    
                    # Create new user
                    user = User(username=username, email=email, is_admin=is_first_user)
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


# Admin panel template
ADMIN_PANEL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel - User Management</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            margin: 0;
            color: #333;
        }
        .nav {
            margin-top: 10px;
        }
        .nav a {
            color: #007AFF;
            text-decoration: none;
            margin-right: 15px;
        }
        .nav a:hover {
            text-decoration: underline;
        }
        .users-table {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-admin {
            background: #007AFF;
            color: white;
        }
        .badge-user {
            background: #6c757d;
            color: white;
        }
        .danger {
            background: #dc3545;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .danger:hover {
            background: #c82333;
        }
        .message {
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .empty {
            padding: 40px;
            text-align: center;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Admin Panel - User Management</h1>
        <div class="nav">
            <a href="/">← Back to App</a>
            <a href="/logout">Logout</a>
        </div>
    </div>
    
    {% if message %}
    <div class="message {{ message_type }}">{{ message }}</div>
    {% endif %}
    
    <div class="users-table">
        {% if users %}
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                <tr>
                    <td>{{ user.id }}</td>
                    <td>{{ user.username }}</td>
                    <td>{{ user.email }}</td>
                    <td>
                        {% if user.is_admin %}
                        <span class="badge badge-admin">Admin</span>
                        {% else %}
                        <span class="badge badge-user">User</span>
                        {% endif %}
                    </td>
                    <td>{{ user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'N/A' }}</td>
                    <td>
                        {% if not user.is_admin %}
                        <button class="danger" onclick="deleteUser({{ user.id }}, '{{ user.username }}')">Delete</button>
                        {% else %}
                        <span style="color: #6c757d;">Admin account</span>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div class="empty">No users found.</div>
        {% endif %}
    </div>
    
    <script>
        function deleteUser(userId, username) {
            if (!confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
                return;
            }
            
            fetch(`/admin/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('User deleted successfully');
                    location.reload();
                } else {
                    alert('Error: ' + (data.error || 'Failed to delete user'));
                }
            })
            .catch(error => {
                alert('Error: ' + error.message);
            });
        }
    </script>
</body>
</html>
"""


@auth_bp.route('/admin')
@admin_required
def admin_panel():
    """Admin panel to view and manage users."""
    session = get_db_session()
    try:
        users = session.query(User).order_by(User.created_at.desc()).all()
        message = request.args.get('message')
        message_type = request.args.get('type', 'success')
        return render_template_string(ADMIN_PANEL_TEMPLATE, users=users, message=message, message_type=message_type)
    finally:
        session.close()


@auth_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user account."""
    session = get_db_session()
    try:
        user = session.query(User).get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Prevent deleting yourself
        if user.id == current_user.id:
            return jsonify({'success': False, 'error': 'Cannot delete your own account'}), 400
        
        # Prevent deleting other admins
        if user.is_admin:
            return jsonify({'success': False, 'error': 'Cannot delete admin accounts'}), 400
        
        # Delete user (cascade will delete config and rules)
        session.delete(user)
        session.commit()
        return jsonify({'success': True})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()

