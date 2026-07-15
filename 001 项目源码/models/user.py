# -*- coding: utf-8 -*-
"""
@file    models/user.py
@brief   User 用户数据模型
@details 对应数据库 user 表，封装用户注册、认证、角色管理操作。
         密码使用 SHA-256 哈希存储，不保存明文。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

import hashlib
import sqlite3
from datetime import datetime
from flask import g
import config as app_config


def _get_db():
    """获取数据库连接（请求上下文或临时连接）"""
    if hasattr(g, 'db') and g.db is not None:
        return g.db
    conn = sqlite3.connect(app_config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _commit(conn):
    """提交并关闭临时连接"""
    conn.commit()
    if not (hasattr(g, 'db') and g.db is not None):
        conn.close()


class User:
    """
    @class User
    @brief 用户模型
    @details 支持 guest / user / admin / super 四种角色。
    """

    ROLE_GUEST = "guest"
    ROLE_USER  = "user"
    ROLE_ADMIN = "admin"
    ROLE_SUPER = "super"

    VALID_ROLES = (ROLE_GUEST, ROLE_USER, ROLE_ADMIN, ROLE_SUPER)

    # =========================================================================
    # 工具方法
    # =========================================================================

    @staticmethod
    def hash_password(password):
        """@brief 对密码进行 SHA-256 哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def to_dict(row):
        """@brief 将 sqlite3.Row 转换为用户字典（移除 password_hash）"""
        if row is None:
            return None
        d = dict(row)
        d.pop("password_hash", None)
        return d

    # =========================================================================
    # 查询操作
    # =========================================================================

    @classmethod
    def get_by_id(cls, user_id):
        """@brief 通过 ID 获取用户"""
        row = _get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        return cls.to_dict(row)

    @classmethod
    def get_by_username(cls, username):
        """@brief 通过用户名获取用户"""
        row = _get_db().execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()
        return cls.to_dict(row)

    @classmethod
    def get_by_username_with_hash(cls, username):
        """@brief 通过用户名获取用户（含 password_hash）"""
        return _get_db().execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

    @classmethod
    def get_all(cls, page=1, per_page=20):
        """@brief 分页获取所有用户列表"""
        conn = _get_db()
        offset = (page - 1) * per_page
        total = conn.execute("SELECT COUNT(*) FROM user").fetchone()[0]
        rows = conn.execute(
            "SELECT * FROM user ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (per_page, offset)
        ).fetchall()
        return [cls.to_dict(r) for r in rows], total

    @classmethod
    def authenticate(cls, username, password):
        """@brief 用户登录认证"""
        row = cls.get_by_username_with_hash(username)
        if not row:
            return None
        pw_hash = cls.hash_password(password)
        if row["password_hash"] != pw_hash:
            return None
        return cls.to_dict(row)

    # =========================================================================
    # 写入操作
    # =========================================================================

    @classmethod
    def create(cls, username, password, role=None):
        """@brief 创建新用户"""
        if role is None:
            role = cls.ROLE_USER
        if role not in cls.VALID_ROLES:
            raise ValueError(f"无效的角色: {role}")

        pw_hash = cls.hash_password(password)
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        conn = _get_db()
        try:
            cursor = conn.execute(
                """INSERT INTO user (username, password_hash, role, created_at)
                   VALUES (?, ?, ?, ?)""",
                (username, pw_hash, role, now)
            )
            _commit(conn)
        except sqlite3.IntegrityError:
            raise ValueError(f"用户名 '{username}' 已存在")

        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def update_role(cls, user_id, new_role):
        """@brief 更新用户角色"""
        if new_role not in cls.VALID_ROLES:
            raise ValueError(f"无效的角色: {new_role}")
        conn = _get_db()
        conn.execute("UPDATE user SET role = ? WHERE id = ?", (new_role, user_id))
        _commit(conn)

    @classmethod
    def delete(cls, user_id):
        """@brief 删除用户"""
        conn = _get_db()
        conn.execute("DELETE FROM user WHERE id = ?", (user_id,))
        _commit(conn)

    # =========================================================================
    # 权限检查
    # =========================================================================

    @staticmethod
    def is_admin(user):
        """@brief 判断用户是否为管理员（admin 或 super）"""
        if not user:
            return False
        return user.get("role") in (User.ROLE_ADMIN, User.ROLE_SUPER)

    @staticmethod
    def is_super(user):
        """@brief 判断用户是否为超级管理员"""
        if not user:
            return False
        return user.get("role") == User.ROLE_SUPER
