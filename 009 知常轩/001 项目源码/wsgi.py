# -*- coding: utf-8 -*-
"""知常轩 WSGI 入口（gunicorn 用）
测试版挂载在 /zcx/ 前缀下（dev.zhichangxuan.com/zcx/），
通过 SCRIPT_NAME 让 Flask 生成的链接自动带前缀。
"""
import os
from app import app

# 环境变量 ZCX_PREFIX 设置挂载前缀（如 /zcx），生产正式版可不设（根路径）
_prefix = os.environ.get('ZCX_PREFIX', '').strip('/')
if _prefix:
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    # 将应用挂载到 /zcx，根路径返回 404（避免误访问）
    app.wsgi_app = DispatcherMiddleware(lambda e, s: s('404 Not Found', [('Content-Type', 'text/plain')], [b'Not Found']), {
        '/' + _prefix: app.wsgi_app
    })

if __name__ == '__main__':
    app.run()
