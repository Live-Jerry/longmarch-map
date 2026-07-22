# -*- coding: utf-8 -*-
"""
@file    run.py
@brief   项目启动脚本
@details 通过 Flask 开发服务器启动应用，支持指定端口和环境。
         生产部署建议使用 gunicorn：gunicorn -w 4 -b 0.0.0.0:5000 app:app
@author  长征文化数字地图项目组
@date    2026-07-15
@version 2.0.0
"""

__version__ = "2.0.0"

import os
import sys

import app as application


def main():
    """主启动函数"""
    # 允许通过环境变量或命令行参数指定端口和环境
    port = int(os.environ.get("PORT", 5000))
    env  = os.environ.get("FLASK_ENV", "development")

    # 可选：python run.py --port 8080 --env production
    args = sys.argv[1:]
    if "--port" in args:
        port = int(args[args.index("--port") + 1])
    if "--env" in args:
        env = args[args.index("--env") + 1]

    print(f"[长征文化] 启动应用 ... 环境={env}, 端口={port}")
    print(f"[长征文化] 访问地址: http://127.0.0.1:{port}")
    print(f"[长征文化] API 前缀: http://127.0.0.1:{port}/api/v1")
    print(f"[长征文化] 默认管理员: admin / admin123")

    flask_app = application.create_app(env)
    flask_app.run(host="0.0.0.0", port=port, debug=(env == "development"))


if __name__ == "__main__":
    main()
