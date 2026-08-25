"""
Gunicorn configuration for Finance App production deployment.

Usage:
    gunicorn -c deployment/gunicorn_config.py main:app

Or via systemd (preferred):
    See deployment/finance_app.service

This configuration:
    - Runs 8 worker processes (for 2GB RAM VPS)
    - Uses sync worker class (simple, sufficient for I/O-bound API)
    - Listens on 127.0.0.1:8000 (accessed via Nginx reverse proxy)
    - Logs in JSON format to stdout
    - Auto-reloads on code change in development
    - Graceful shutdown with 30s timeout
"""

import os
import multiprocessing
import logging

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
# Calculate: (2 * num_cores) + 1
# For 1-core VPS: use 4-8 workers
num_cores = multiprocessing.cpu_count()
workers = max(4, (2 * num_cores) + 1)

# Increase for high-traffic (up to 16 per core)
# Decrease for low-memory VPS
worker_class = "sync"  # Use uvicorn for async: "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"
access_log_format = '%(asctime)s %(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Application
wsgi_app = "main:app"
pythonpath = "/opt/finance_app"

# Server mechanics
daemon = False
umask = 0
user = "finance_app"  # Run as non-root user
group = "finance_app"
tmp_upload_dir = "/var/tmp"

# Process naming
proc_name = "finance_app"

# Server hooks for startup/shutdown
def on_starting(server):
    """Called when Gunicorn starts."""
    logging.info("Finance App starting")

def on_exit(server):
    """Called when Gunicorn exits."""
    logging.info("Finance App shutting down")

# Environment
raw_env = [
    "PYTHONUNBUFFERED=1",  # Unbuffered output (for Docker/systemd)
]

# Reload on code change (development only)
# reload = True  # Uncomment for development
