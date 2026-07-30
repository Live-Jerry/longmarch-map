# -*- coding: utf-8 -*-
"""
@file    api/__init__.py
@brief   API 蓝图包初始化
@details 导出所有 REST API 蓝图，统一前缀 /api/v1。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

from api.auth_api  import auth_bp
from api.node_api  import node_bp
from api.route_api import route_bp
from api.media_api import media_bp
from api.spark_api import spark_bp
from api.message_api import message_bp

__all__ = ["auth_bp", "node_bp", "route_bp", "media_bp", "spark_bp", "message_bp"]
