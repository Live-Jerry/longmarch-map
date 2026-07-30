# -*- coding: utf-8 -*-
"""
@file    models/message.py
@brief   留言板数据模型
@details 对应数据库 message 表，存储用户留言。
@author  长征文化数字地图项目组
@date    2026-07-27
"""

import sqlite3
from datetime import datetime
from flask import g
import config as app_config


def _get_db():
    """获取数据库连接"""
    if hasattr(g, 'db') and g.db is not None:
        return g.db
    conn = sqlite3.connect(app_config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _commit(conn):
    conn.commit()
    if not (hasattr(g, 'db') and g.db is not None):
        conn.close()


class Message:
    """留言板模型"""

    @staticmethod
    def to_dict(row):
        return dict(row) if row else None

    @staticmethod
    def init_table():
        """创建 message 表（如果不存在），用于独立初始化"""
        import sqlite3
        import config as app_config
        conn = sqlite3.connect(app_config.DATABASE_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS message (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                content     TEXT    NOT NULL,
                user_name   TEXT    DEFAULT '',
                user_id     TEXT    DEFAULT '',
                node_id     TEXT    DEFAULT '',
                created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
            )
        """)
        conn.commit()
        conn.close()

    @staticmethod
    def add(content, user_name='', user_id='', node_id=''):
        """添加留言"""
        conn = _get_db()
        conn.execute(
            "INSERT INTO message (content, user_name, user_id, node_id) VALUES (?, ?, ?, ?)",
            (content, user_name, user_id, node_id)
        )
        _commit(conn)
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    @staticmethod
    def get_all(limit=100, offset=0):
        """获取留言列表（最新在前）"""
        conn = _get_db()
        rows = conn.execute(
            "SELECT * FROM message ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def get_count():
        """获取留言总数"""
        conn = _get_db()
        row = conn.execute("SELECT COUNT(*) FROM message").fetchone()
        return row[0] if row else 0

    @staticmethod
    def delete(message_id):
        """删除留言"""
        conn = _get_db()
        conn.execute("DELETE FROM message WHERE id = ?", (message_id,))
        _commit(conn)



