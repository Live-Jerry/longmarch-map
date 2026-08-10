#!/usr/bin/env python3
"""
Gunicorn configuration for 知常轩 dev environment.
"""
import os
import multiprocessing

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(project_root, "001 项目源码")
log_dir = os.path.join(project_root, "logs")

os.makedirs(log_dir, exist_ok=True)

bind = "127.0.0.1:5003"
backlog = 1024

workers = 2
worker_class = "sync"
timeout = 60
graceful_timeout = 30

accesslog = os.path.join(log_dir, "access.log")
errorlog = os.path.join(log_dir, "error.log")
loglevel = "info"

os.chdir(app_dir)
