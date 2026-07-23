# -*- coding: utf-8 -*-
"""
WSGI entry point for production deployment with Gunicorn.
Usage: gunicorn -c ../006 build/gunicorn_config.py wsgi:app
"""
import os
import sys

# Ensure the application directory is on the path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import create_app

# Create the application instance for WSGI servers
env = os.environ.get("FLASK_ENV", "production")
app = create_app(env)
