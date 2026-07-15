# -*- coding: utf-8 -*-
"""
@file    models/node.py
@brief   Node 节点数据模型
@details 对应数据库 node 表，封装节点信息的读取、创建、更新、删除操作。
         节点是长征路线地图的核心要素，每个节点对应一个历史事件地点。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

import sqlite3
import json
from datetime import datetime
from flask import g
import config as app_config


def _get_db():
    """
    @brief 获取当前请求的数据库连接
    @details 若在 Flask 请求上下文中，返回 g.db；否则创建临时连接。
             临时连接用于脚本导入等非请求场景。
    @return sqlite3.Connection
    """
    if hasattr(g, 'db') and g.db is not None:
        return g.db
    conn = sqlite3.connect(app_config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _commit(conn):
    """提交并关闭临时连接（仅非请求场景需要手动关闭）"""
    conn.commit()
    in_request = hasattr(g, 'db') and g.db is not None
    if not in_request:
        conn.close()


class Node:
    """
    @class Node
    @brief 长征历史节点模型
    @details 每个节点代表长征途中一个重要的历史事件发生地，
             包含位置信息、历史背景、战役、会义、诗篇等多种信息字段。
    """

    # =========================================================================
    # 字段常量
    # =========================================================================
    ALL_FIELDS = (
        "node_id", "title", "location", "lat", "lng", "time",
        "core_numbers", "famous_battle", "important_meeting",
        "history_event", "core_site", "poem_article", "typical_story",
        "typical_people", "historical_significance", "spark_remains",
        "media_path", "image_list", "audio_path", "video_url",
        "status", "created_at", "updated_at"
    )

    # =========================================================================
    # 工具方法
    # =========================================================================

    @staticmethod
    def to_row_dict(row):
        """
        @brief  将 sqlite3.Row 转换为字典
        @param  row  sqlite3.Row 对象
        @return dict
        """
        if row is None:
            return None
        d = dict(row)
        if d.get("image_list"):
            try:
                d["image_list"] = json.loads(d["image_list"])
            except (ValueError, TypeError):
                d["image_list"] = []
        return d

    # =========================================================================
    # 查询操作
    # =========================================================================

    @classmethod
    def get_all(cls, page=1, per_page=20, search=None, province=None, status=None):
        """
        @brief      分页获取节点列表
        @param      page       页码（从 1 开始）
        @param      per_page   每页数量
        @param      search     模糊搜索关键词（搜索 title / location）
        @param      province   省份过滤
        @param      status     状态过滤，默认只返回 active
        @return     tuple      (节点列表, 总数)
        """
        conn = _get_db()
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)
        else:
            conditions.append("status = 'active'")

        if search:
            conditions.append("(title LIKE ? OR location LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

        if province:
            conditions.append("location LIKE ?")
            params.append(f"%{province}%")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        total = conn.execute(
            f"SELECT COUNT(*) FROM node WHERE {where_clause}", params
        ).fetchone()[0]

        offset = (page - 1) * per_page
        rows = conn.execute(
            f"""SELECT * FROM node
                WHERE {where_clause}
                ORDER BY time ASC
                LIMIT ? OFFSET ?""",
            params + [per_page, offset]
        ).fetchall()

        return [cls.to_row_dict(r) for r in rows], total

    @classmethod
    def get_by_node_id(cls, node_id):
        """
        @brief  通过 node_id 获取单个节点详情
        @param  node_id  节点编号（字符串，如 "001"）
        @return dict     节点数据字典，不存在返回 None
        """
        row = _get_db().execute(
            "SELECT * FROM node WHERE node_id = ?", (node_id,)
        ).fetchone()
        return cls.to_row_dict(row)

    @classmethod
    def get_by_status(cls, status):
        """
        @brief  通过状态获取所有节点
        @param  status  pending | active | archived
        @return list    节点列表
        """
        rows = _get_db().execute(
            "SELECT * FROM node WHERE status = ? ORDER BY time ASC", (status,)
        ).fetchall()
        return [cls.to_row_dict(r) for r in rows]

    @classmethod
    def get_nearby(cls, lat, lng, radius_km=50):
        """
        @brief  获取指定坐标附近的所有节点
        @param  lat        纬度
        @param  lng        经度
        @param  radius_km  搜索半径（公里），默认 50km
        @note   使用简化球面距离公式
        @return list       附近节点列表（按距离升序）
        """
        lat_delta = radius_km / 111.0
        lng_delta = radius_km / (111.0 * max(0.01, abs(lat)))

        rows = _get_db().execute(
            """SELECT * FROM node
               WHERE lat BETWEEN ? AND ?
                 AND lng BETWEEN ? AND ?
                 AND status = 'active'
               ORDER BY ABS(lat - ?) + ABS(lng - ?) ASC""",
            (lat - lat_delta, lat + lat_delta,
             lng - lng_delta, lng + lng_delta,
             lat, lng)
        ).fetchall()
        return [cls.to_row_dict(r) for r in rows]

    # =========================================================================
    # 写入操作
    # =========================================================================

    @classmethod
    def create(cls, data):
        """
        @brief  创建新节点
        @param  data  节点数据字典（包含 node_id, title, location, lat, lng 等）
        @return dict  新创建的节点数据
        """
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        if "image_list" in data and isinstance(data["image_list"], list):
            data["image_list"] = json.dumps(data["image_list"], ensure_ascii=False)

        fields = {k: v for k, v in data.items() if k in cls.ALL_FIELDS}
        fields.setdefault("status", "active")
        fields.setdefault("created_at", now)
        fields.setdefault("updated_at", now)

        columns = ", ".join(fields.keys())
        placeholders = ", ".join(["?"] * len(fields))
        values = list(fields.values())

        conn = _get_db()
        cursor = conn.execute(
            f"INSERT INTO node ({columns}) VALUES ({placeholders})", values
        )
        _commit(conn)
        return cls.get_by_node_id(data["node_id"])

    @classmethod
    def update(cls, node_id, data):
        """
        @brief  更新节点信息
        @param  node_id  节点编号
        @param  data     要更新的字段字典
        @return dict     更新后的节点数据
        """
        if "image_list" in data and isinstance(data["image_list"], list):
            data["image_list"] = json.dumps(data["image_list"], ensure_ascii=False)

        data["updated_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        sets = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [node_id]

        conn = _get_db()
        conn.execute(f"UPDATE node SET {sets} WHERE node_id = ?", values)
        _commit(conn)
        return cls.get_by_node_id(node_id)

    @classmethod
    def delete(cls, node_id):
        """
        @brief  删除节点（软删除，将状态改为 archived）
        @param  node_id  节点编号
        @return bool     成功返回 True
        """
        conn = _get_db()
        conn.execute(
            "UPDATE node SET status = 'archived', updated_at = ? WHERE node_id = ?",
            (datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), node_id)
        )
        _commit(conn)
        return True

    @classmethod
    def hard_delete(cls, node_id):
        """
        @brief  永久删除节点（仅管理员可用）
        @param  node_id  节点编号
        """
        conn = _get_db()
        conn.execute("DELETE FROM node WHERE node_id = ?", (node_id,))
        _commit(conn)
