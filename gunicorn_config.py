"""
Gunicorn configuration for production deployment.
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes
# Use 2-4 workers for small apps, adjust based on your needs
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
worker_class = "sync"
worker_connections = 1000
timeout = 30  # Increase if database connections are slow
keepalive = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.environ.get("LOG_LEVEL", "info")

# Process naming
proc_name = "shopify-order-app"

# Graceful timeout for worker shutdown
graceful_timeout = 30

# Preload app for better performance
preload_app = False  # Set to True if you have memory issues, but False is safer for database connections

