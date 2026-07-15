# -*- coding: utf-8 -*-
"""
@file    models/media.py
@brief   Media 素材数据模型
@details 对应数据库 media 表，管理节点关联的图片、音频、视频、文档等素材。
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


class Media:
    """
    @class Media
    @brief 素材模型
    @details 素材包括图片（image）、音频（audio）、视频（video）和文本（text）四种类型。
    """

    TYPE_IMAGE = "image"
    TYPE_AUDIO = "audio"
    TYPE_VIDEO = "video"
    TYPE_TEXT  = "text"

    VALID_TYPES  = (TYPE_IMAGE, TYPE_AUDIO, TYPE_VIDEO, TYPE_TEXT)
    VALID_STATUS = ("pending", "approved", "rejected")

    @staticmethod
    def to_dict(row):
        """@brief 将 sqlite3.Row 转换为字典"""
        return dict(row) if row else None

    # =========================================================================
    # 查询操作
    # =========================================================================

    @classmethod
    def get_by_id(cls, media_id):
        """@brief 通过 ID 获取素材"""
        row = _get_db().execute(
            "SELECT * FROM media WHERE id = ?", (media_id,)
        ).fetchone()
        return cls.to_dict(row)

    @classmethod
    def get_by_node(cls, node_id, status=None):
        """@brief 获取指定节点的所有素材"""
        conn = _get_db()
        if status:
            rows = conn.execute(
                "SELECT * FROM media WHERE node_id = ? AND status = ? ORDER BY created_at DESC",
                (node_id, status)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM media WHERE node_id = ? AND status = 'approved' ORDER BY created_at DESC",
                (node_id,)
            ).fetchall()
        return [cls.to_dict(r) for r in rows]

    @classmethod
    def get_all(cls, page=1, per_page=20, media_type=None, status=None):
        """@brief 分页获取素材列表"""
        conn = _get_db()
        conditions = []
        params = []

        if media_type:
            conditions.append("type = ?")
            params.append(media_type)
        if status:
            conditions.append("status = ?")
            params.append(status)

        where = " AND ".join(conditions) if conditions else "1=1"

        total = conn.execute(
            f"SELECT COUNT(*) FROM media WHERE {where}", params
        ).fetchone()[0]

        offset = (page - 1) * per_page
        rows = conn.execute(
            f"SELECT * FROM media WHERE {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [per_page, offset]
        ).fetchall()
        return [cls.to_dict(r) for r in rows], total

    # =========================================================================
    # 写入操作
    # =========================================================================

    @classmethod
    def create(cls, data):
        """@brief 创建素材记录"""
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        data.setdefault("status", "pending")
        data.setdefault("created_at", now)

        valid_fields = {
            "node_id", "type", "title", "description",
            "file_path", "source", "uploader_id", "status", "created_at"
        }
        fields = {k: v for k, v in data.items() if k in valid_fields}

        columns = ", ".join(fields.keys())
        placeholders = ", ".join(["?"] * len(fields))

        conn = _get_db()
        cursor = conn.execute(
            f"INSERT INTO media ({columns}) VALUES ({placeholders})",
            list(fields.values())
        )
        _commit(conn)
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def update_status(cls, media_id, status, admin_comment=None):
        """@brief 更新素材审核状态"""
        if status not in cls.VALID_STATUS:
            raise ValueError(f"无效状态: {status}")
        conn = _get_db()
        if admin_comment:
            conn.execute(
                "UPDATE media SET status = ?, description = COALESCE(?, description) WHERE id = ?",
                (status, admin_comment, media_id)
            )
        else:
            conn.execute("UPDATE media SET status = ? WHERE id = ?", (status, media_id))
        _commit(conn)

    @classmethod
    def delete(cls, media_id):
        """@brief 删除素材记录"""
        conn = _get_db()
        conn.execute("DELETE FROM media WHERE id = ?", (media_id,))
        _commit(conn)
