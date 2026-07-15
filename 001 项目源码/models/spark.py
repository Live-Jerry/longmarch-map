# -*- coding: utf-8 -*-
"""
@file    models/spark.py
@brief   Spark 星火拾遗数据模型
@details 对应数据库 spark 表，存储用户提交的民间史料、回忆、口述历史等星火内容。
@author  长征文化数字地图项目组
@date    2026-07-15
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


class Spark:
    """
    @class Spark
    @brief 星火拾遗模型
    @details "星火拾遗"是长征文化数字地图的公民历史项目，
             允许普通用户上传历史照片、老故事、口述回忆等民间史料。
    """

    VALID_STATUS = ("pending", "approved", "rejected")
    VALID_TYPES  = ("text", "image", "audio", "video", "document")

    @staticmethod
    def to_dict(row):
        """@brief 将 sqlite3.Row 转换为字典"""
        return dict(row) if row else None

    # =========================================================================
    # 查询操作
    # =========================================================================

    @classmethod
    def get_by_id(cls, spark_id):
        """@brief 通过 ID 获取星火内容"""
        row = _get_db().execute(
            "SELECT * FROM spark WHERE id = ?", (spark_id,)
        ).fetchone()
        return cls.to_dict(row)

    @classmethod
    def get_all(cls, page=1, per_page=20, status=None, node_id=None):
        """@brief 分页获取星火列表"""
        conn = _get_db()
        conditions = []
        params = []

        if status:
            conditions.append("s.status = ?")
            params.append(status)
        else:
            conditions.append("s.status = 'approved'")

        if node_id:
            conditions.append("s.node_id = ?")
            params.append(node_id)

        where = " AND ".join(conditions) if conditions else "1=1"

        total = conn.execute(
            f"SELECT COUNT(*) FROM spark s WHERE {where}", params
        ).fetchone()[0]

        offset = (page - 1) * per_page
        rows = conn.execute(
            f"""SELECT s.*, u.username
                FROM spark s
                LEFT JOIN user u ON s.user_id = u.id
                WHERE {where}
                ORDER BY s.created_at DESC
                LIMIT ? OFFSET ?""",
            params + [per_page, offset]
        ).fetchall()
        return [cls.to_dict(r) for r in rows], total

    @classmethod
    def get_pending(cls):
        """@brief 获取所有待审核星火"""
        conn = _get_db()
        rows = conn.execute(
            """SELECT s.*, u.username
               FROM spark s
               LEFT JOIN user u ON s.user_id = u.id
               WHERE s.status = 'pending'
               ORDER BY s.created_at ASC"""
        ).fetchall()
        return [cls.to_dict(r) for r in rows]

    @classmethod
    def get_by_user(cls, user_id, page=1, per_page=20):
        """@brief 获取指定用户提交的所有星火"""
        conn = _get_db()
        total = conn.execute(
            "SELECT COUNT(*) FROM spark WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
        offset = (page - 1) * per_page
        rows = conn.execute(
            """SELECT s.*, u.username
               FROM spark s
               LEFT JOIN user u ON s.user_id = u.id
               WHERE s.user_id = ?
               ORDER BY s.created_at DESC
               LIMIT ? OFFSET ?""",
            (user_id, per_page, offset)
        ).fetchall()
        return [cls.to_dict(r) for r in rows], total

    @classmethod
    def get_stats(cls):
        """@brief 获取星火系统统计信息"""
        conn = _get_db()
        stats = {}
        for s in ("pending", "approved", "rejected"):
            count = conn.execute(
                "SELECT COUNT(*) FROM spark WHERE status = ?", (s,)
            ).fetchone()[0]
            stats[s] = count
        stats["total"] = sum(stats.values())
        return stats

    # =========================================================================
    # 写入操作
    # =========================================================================

    @classmethod
    def create(cls, data):
        """@brief 提交新的星火内容"""
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        data.setdefault("status", "pending")
        data.setdefault("created_at", now)

        valid_fields = {
            "node_id", "user_id", "title", "content", "media_type",
            "file_path", "source", "status", "created_at"
        }
        fields = {k: v for k, v in data.items() if k in valid_fields}

        columns = ", ".join(fields.keys())
        placeholders = ", ".join(["?"] * len(fields))

        conn = _get_db()
        cursor = conn.execute(
            f"INSERT INTO spark ({columns}) VALUES ({placeholders})",
            list(fields.values())
        )
        _commit(conn)
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def review(cls, spark_id, status, admin_comment=None):
        """@brief 管理员审核星火内容"""
        if status not in ("approved", "rejected"):
            raise ValueError("审核状态必须为 approved 或 rejected")

        conn = _get_db()
        if admin_comment:
            conn.execute(
                "UPDATE spark SET status = ?, admin_comment = ? WHERE id = ?",
                (status, admin_comment, spark_id)
            )
        else:
            conn.execute(
                "UPDATE spark SET status = ? WHERE id = ?",
                (status, spark_id)
            )
        _commit(conn)
        return cls.get_by_id(spark_id)

    @classmethod
    def delete(cls, spark_id):
        """@brief 删除星火内容"""
        conn = _get_db()
        conn.execute("DELETE FROM spark WHERE id = ?", (spark_id,))
        _commit(conn)
