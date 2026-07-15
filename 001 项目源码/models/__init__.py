# -*- coding: utf-8 -*-
"""
@file    models/__init__.py
@brief   数据模型包初始化
@details 导出所有数据模型类，统一通过 Flask g.db 访问 SQLite。
         每个模型的 CRUD 操作封装为静态方法，便于 service 层调用。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

from models.node  import Node
from models.user  import User
from models.media import Media
from models.spark import Spark

__all__ = ["Node", "User", "Media", "Spark"]
