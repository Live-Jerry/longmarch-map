# -*- coding: utf-8 -*-
"""
@file    config.py
@brief   应用配置文件 — 包含所有可调整的运行时参数
@details 定义 Flask 密钥、数据库路径、静态资源路径、上传限制等配置项。
         支持开发/生产环境切换，默认使用 SQLite 作为开发数据库。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

import os

# =============================================================================
# 基础路径配置
# =============================================================================

# 项目根目录（__file__ 为 config.py 所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据库路径（SQLite）
DATABASE_PATH = os.path.join(BASE_DIR, "data", "longmarch.db")

# 静态资源目录
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 模板目录
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

# 上传文件存放目录
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

# 节点初始数据 JSON 路径
NODE_DATA_JSON = os.path.join(BASE_DIR, "data", "node_data.json")

# =============================================================================
# Flask 配置
# =============================================================================

class Config:
    """Flask 全局配置基类"""
    # Flask 密钥（生产环境请使用随机字符串）
    SECRET_KEY = os.environ.get("SECRET_KEY") or "longmarch-secret-key-2026"

    # 数据库 URI（SQLite）
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"

    # 关闭 Flask-SQLAlchemy 警告（我们使用原生 sqlite3）
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 上传文件大小限制（字节），默认 16 MB
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # 上传文件允许的扩展名
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp3", "mp4", "wav", "webm"}

    # 分页默认每页数量
    DEFAULT_PER_PAGE = 20

    # JWT 令牌有效期（秒），默认 7 天
    JWT_EXPIRATION_SECONDS = 7 * 24 * 3600

    # 管理员初始用户名（首次运行自动创建）
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"  # 生产环境请修改！

    # 百度地图 AK（可选，用于地理编码）
    BAIDU_MAP_AK = os.environ.get("BAIDU_MAP_AK") or ""

    # 星火系统待审核提醒阈值
    SPARK_PENDING_THRESHOLD = 10


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    # SECRET_KEY 应通过环境变量注入


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    DATABASE_PATH = os.path.join(BASE_DIR, "data", "test_longmarch.db")


# 配置字典，按环境切换
config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}


def get_config(env=None):
    """获取指定环境的配置类"""
    if env is None:
        env = os.environ.get("FLASK_ENV", "default")
    return config_dict.get(env, DevelopmentConfig)
