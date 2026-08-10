# -*- coding: utf-8 -*-
"""知常轩 WSGI 入口（gunicorn 用）"""
from app import app

if __name__ == '__main__':
    app.run()
