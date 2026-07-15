# -*- coding: utf-8 -*-
"""
@file    app.py
@brief   Flask 应用主入口文件
@details 负责应用工厂、蓝图注册、数据库初始化和请求钩子设置。
         所有路由前缀统一使用 /api/v1，静态资源由 Nginx 或 Flask 提供。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

import os
import sqlite3
import hashlib
from datetime import datetime

from flask import Flask, g, jsonify, request

import config


# =============================================================================
# 应用工厂
# =============================================================================

def create_app(env=None):
    """
    @brief  Flask 应用工厂函数
    @param  env     环境名称，可选 "development" | "production" | "testing"
    @return Flask   已配置完整的 Flask 应用实例
    """
    app = Flask(__name__)

    # 加载配置
    cfg = config.get_config(env)
    app.config.from_object(cfg)

    # 确保必要目录存在
    _ensure_directories()

    # 初始化数据库
    _init_database(app)

    # 注册请求钩子
    _register_hooks(app)

    # 注册蓝图
    _register_blueprints(app)
    _register_page_routes(app)

    return app


def _ensure_directories():
    """确保所有必要目录存在"""
    dirs = [
        os.path.dirname(config.DATABASE_PATH),
        config.UPLOAD_DIR,
        os.path.join(config.STATIC_DIR, "css"),
        os.path.join(config.STATIC_DIR, "js"),
        os.path.join(config.STATIC_DIR, "images"),
    ]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)


# =============================================================================
# 数据库初始化
# =============================================================================

def _init_database(app):
    """
    @brief 初始化 SQLite 数据库结构
    @details 首次运行时创建所有表，并插入管理员账户和节点初始数据。
    """
    db_path = config.DATABASE_PATH
    schema_sql = _get_schema_sql()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()

        # 插入默认管理员（若不存在）
        _ensure_admin(cursor)
        conn.commit()


def _get_schema_sql():
    """
    @brief 返回完整的建表 SQL
    @return str  SQL 语句
    """
    return """
    -- 用户表
    CREATE TABLE IF NOT EXISTS user (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        username    TEXT    UNIQUE NOT NULL,
        password_hash TEXT  NOT NULL,
        role        TEXT    NOT NULL DEFAULT 'user',
        created_at  TEXT    NOT NULL
    );

    -- 节点表（核心数据）
    CREATE TABLE IF NOT EXISTS node (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id            TEXT    UNIQUE NOT NULL,
        title              TEXT    NOT NULL,
        location           TEXT    NOT NULL,
        lat                REAL    NOT NULL,
        lng                REAL    NOT NULL,
        time               TEXT    NOT NULL,
        core_numbers       TEXT,
        famous_battle      TEXT,
        important_meeting  TEXT,
        history_event      TEXT,
        core_site          TEXT,
        poem_article       TEXT,
        typical_story      TEXT,
        typical_people     TEXT,
        historical_significance TEXT,
        spark_remains      TEXT,
        media_path         TEXT,
        image_list         TEXT,
        audio_path         TEXT,
        video_url          TEXT,
        active_sections    TEXT,
        status             TEXT    NOT NULL DEFAULT 'active',
        created_at         TEXT    NOT NULL,
        updated_at         TEXT    NOT NULL
    );

    -- 素材表
    CREATE TABLE IF NOT EXISTS media (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id      TEXT,
        type         TEXT    NOT NULL,
        title        TEXT    NOT NULL,
        description  TEXT,
        file_path    TEXT,
        source       TEXT,
        uploader_id  INTEGER,
        status       TEXT    NOT NULL DEFAULT 'pending',
        created_at   TEXT    NOT NULL,
        FOREIGN KEY (node_id) REFERENCES node(node_id),
        FOREIGN KEY (uploader_id) REFERENCES user(id)
    );

    -- 星火拾遗表
    CREATE TABLE IF NOT EXISTS spark (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id        TEXT,
        user_id        INTEGER,
        title          TEXT    NOT NULL,
        content        TEXT,
        media_type     TEXT,
        file_path      TEXT,
        source         TEXT,
        status         TEXT    NOT NULL DEFAULT 'pending',
        admin_comment  TEXT,
        created_at     TEXT    NOT NULL,
        FOREIGN KEY (node_id) REFERENCES node(node_id),
        FOREIGN KEY (user_id) REFERENCES user(id)
    );

    -- 评论表
    CREATE TABLE IF NOT EXISTS comment (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        content    TEXT    NOT NULL,
        node_id    TEXT,
        created_at TEXT    NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id),
        FOREIGN KEY (node_id) REFERENCES node(node_id)
    );

    -- 路线点表（各支军队的行军路线）
    CREATE TABLE IF NOT EXISTS route_point (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        army        INTEGER NOT NULL,
        stage       TEXT,
        lat         REAL    NOT NULL,
        lng         REAL    NOT NULL,
        order_index INTEGER NOT NULL,
        is_node     INTEGER NOT NULL DEFAULT 0,
        node_id     TEXT,
        FOREIGN KEY (node_id) REFERENCES node(node_id)
    );

    -- 确保索引存在
    CREATE INDEX IF NOT EXISTS idx_node_status  ON node(status);
    CREATE INDEX IF NOT EXISTS idx_node_location ON node(lat, lng);
    CREATE INDEX IF NOT EXISTS idx_media_node   ON media(node_id);
    CREATE INDEX IF NOT EXISTS idx_spark_status ON spark(status);
    CREATE INDEX IF NOT EXISTS idx_route_army   ON route_point(army);
    """


def _ensure_admin(cursor):
    """插入默认管理员账户（若不存在）"""
    cursor.execute("SELECT id FROM user WHERE username = ?", (config.Config.ADMIN_USERNAME,))
    if not cursor.fetchone():
        pw_hash = hashlib.sha256(config.Config.ADMIN_PASSWORD.encode()).hexdigest()
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        cursor.execute(
            "INSERT INTO user (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (config.Config.ADMIN_USERNAME, pw_hash, "admin", now)
        )


# =============================================================================
# 请求钩子
# =============================================================================

def _register_hooks(app):
    """注册请求前后钩子"""

    @app.before_request
    def before_request():
        """每个请求前打开数据库连接"""
        g.db = sqlite3.connect(config.DATABASE_PATH)
        g.db.row_factory = sqlite3.Row

    @app.teardown_request
    def teardown_request(exception):
        """每个请求结束后关闭数据库连接"""
        db = getattr(g, "db", None)
        if db:
            db.close()

    @app.errorhandler(404)
    def not_found(error):
        """统一 404 响应格式"""
        return jsonify({"error": "Not Found", "message": "请求的资源不存在"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """统一 500 响应格式"""
        return jsonify({"error": "Internal Server Error", "message": "服务器内部错误"}), 500


# =============================================================================
# 蓝图注册
# =============================================================================

def _register_blueprints(app):
    """注册所有 API 蓝图"""
    from api.auth_api   import auth_bp
    from api.node_api   import node_bp
    from api.route_api  import route_bp
    from api.media_api  import media_bp
    from api.spark_api  import spark_bp

    # 所有 API 路由统一前缀 /api/v1
    app.register_blueprint(auth_bp,  url_prefix="/api/v1/auth")
    app.register_blueprint(node_bp,  url_prefix="/api/v1/nodes")
    app.register_blueprint(route_bp, url_prefix="/api/v1/routes")
    app.register_blueprint(media_bp, url_prefix="/api/v1/media")
    app.register_blueprint(spark_bp, url_prefix="/api/v1/sparks")


# =============================================================================
# 主入口
# =============================================================================

def _register_blueprints(app):
    """注册所有 API 蓝图"""
    from api.auth_api   import auth_bp
    from api.node_api   import node_bp
    from api.route_api  import route_bp
    from api.media_api  import media_bp
    from api.spark_api  import spark_bp

    # 所有 API 路由统一前缀 /api/v1
    app.register_blueprint(auth_bp,  url_prefix="/api/v1/auth")
    app.register_blueprint(node_bp,  url_prefix="/api/v1/nodes")
    app.register_blueprint(route_bp, url_prefix="/api/v1/routes")
    app.register_blueprint(media_bp, url_prefix="/api/v1/media")
    app.register_blueprint(spark_bp, url_prefix="/api/v1/sparks")


def _register_page_routes(app):
    """注册页面路由（HTML 模板）"""
    from flask import render_template, send_from_directory

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")

    @app.route("/admin")
    def admin_page():
        return render_template("admin/index.html")

    @app.route("/admin/nodes")
    def admin_nodes_page():
        return render_template("admin/nodes.html")

    @app.route("/admin/users")
    def admin_users_page():
        return render_template("admin/users.html")

    @app.route("/admin/sparks")
    def admin_sparks_page():
        return render_template("admin/sparks.html")

    # 静态文件（生产环境由 Nginx 提供）
    @app.route("/static/<path:filename>")
    def static_files(filename):
        return send_from_directory(app.config.get("STATIC_DIR", "static"), filename)

    # 节点图片（从 002 项目资源 目录加载）
    @app.route("/node-image/<node_id>")
    def node_image(node_id):
        import os as _os
        project_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        resource_dir = _os.path.join(project_root, "002 项目资源")
        if _os.path.isdir(resource_dir):
            for folder in sorted(_os.listdir(resource_dir)):
                if folder.startswith(node_id):
                    folder_path = _os.path.join(resource_dir, folder)
                    if _os.path.isdir(folder_path):
                        for f in sorted(_os.listdir(folder_path)):
                            if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                                return send_from_directory(folder_path, f)
        # 无图片时返回军旗SVG
        return send_from_directory(
            _os.path.join(config.STATIC_DIR, "images"),
            "flag-placeholder.svg"
        ) if _os.path.exists(_os.path.join(config.STATIC_DIR, "images", "flag-placeholder.svg")) else ("", 404)


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
