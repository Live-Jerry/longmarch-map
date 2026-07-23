#!/usr/bin/env python3
"""
Gunicorn configuration for production deployment.
Used by deploy.sh and longmarch.service.
"""
import os
import multiprocessing

# Project root (two levels up from 006 build/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(project_root, "001 项目源码")
log_dir = os.path.join(project_root, "logs")

os.makedirs(log_dir, exist_ok=True)

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 2

# Process naming
proc_name = "longmarch_map"

# Logging
loglevel = "info"
accesslog = os.path.join(log_dir, "access.log")
errorlog = os.path.join(log_dir, "error.log")

# Environment
raw_env = [
    "FLASK_ENV=production",
]

# Working directory = Flask app directory
chdir = app_dir
