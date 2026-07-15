# -*- coding: utf-8 -*-
"""
@file    services/node_manager.py
@brief   节点管理服务
@details 提供节点 CRUD、分页查询、附近节点搜索、节点导入导出等业务逻辑。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

import json
import os
from datetime import datetime

import config
from models.node import Node


class NodeManager:
    """
    @class NodeManager
    @brief 节点管理服务
    @details 封装节点相关的复杂业务逻辑，如批量导入、附近节点排序、
             节点搜索等，供 API 层调用。
    """

    @staticmethod
    def get_nodes(page=1, per_page=None, search=None, province=None, status=None):
        """
        @brief  获取节点列表（带分页）
        @param  page       页码
        @param  per_page   每页数量（默认取配置值）
        @param  search     搜索关键词
        @param  province   省份过滤
        @param  status     状态过滤
        @return dict       包含 items, total, page, per_page, pages
        """
        if per_page is None:
            per_page = config.Config.DEFAULT_PER_PAGE

        nodes, total = Node.get_all(
            page=page, per_page=per_page,
            search=search, province=province, status=status
        )

        return {
            "items":    nodes,
            "total":    total,
            "page":     page,
            "per_page": per_page,
            "pages":    (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_node_detail(node_id):
        """
        @brief  获取节点详情
        @param  node_id  节点编号
        @return dict     节点数据，不存在返回 None
        """
        return Node.get_by_node_id(node_id)

    @staticmethod
    def create_node(data):
        """
        @brief  创建新节点（需要管理员权限，由调用方检查）
        @param  data  节点数据
        @return dict  创建后的节点
        """
        required = ("node_id", "title", "location", "lat", "lng", "time")
        for field in required:
            if not data.get(field):
                raise ValueError(f"缺少必填字段: {field}")

        # 检查 node_id 是否已存在
        existing = Node.get_by_node_id(data["node_id"])
        if existing:
            raise ValueError(f"节点编号 '{data['node_id']}' 已存在")

        return Node.create(data)

    @staticmethod
    def update_node(node_id, data):
        """
        @brief  更新节点
        @param  node_id  节点编号
        @param  data     更新的字段
        @return dict     更新后的节点
        """
        existing = Node.get_by_node_id(node_id)
        if not existing:
            raise ValueError(f"节点 '{node_id}' 不存在")

        return Node.update(node_id, data)

    @staticmethod
    def remove_node(node_id, hard=False):
        """
        @brief  删除节点
        @param  node_id  节点编号
        @param  hard     True 为永久删除，False 为软删除（默认）
        """
        existing = Node.get_by_node_id(node_id)
        if not existing:
            raise ValueError(f"节点 '{node_id}' 不存在")

        if hard:
            Node.hard_delete(node_id)
        else:
            Node.delete(node_id)

    @staticmethod
    def get_nearby_nodes(lat, lng, radius_km=50):
        """
        @brief  获取指定坐标附近的节点
        @param  lat        纬度
        @param  lng        经度
        @param  radius_km  半径（公里）
        @return list       附近节点列表
        """
        return Node.get_nearby(lat, lng, radius_km)

    @staticmethod
    def import_from_json(json_path=None):
        """
        @brief  从 JSON 文件批量导入节点初始数据
        @param  json_path  JSON 文件路径（默认使用配置的初始数据路径）
        @return dict       导入结果统计
        """
        if json_path is None:
            json_path = config.NODE_DATA_JSON

        if not os.path.exists(json_path):
            raise FileNotFoundError(f"节点数据文件不存在: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            nodes_data = json.load(f)

        imported = 0
        skipped = 0
        errors = []

        for item in nodes_data:
            try:
                node_id = item.get("node_id")
                if not node_id:
                    errors.append(f"缺少 node_id: {item}")
                    skipped += 1
                    continue

                existing = Node.get_by_node_id(node_id)
                if existing:
                    skipped += 1
                    continue

                Node.create(item)
                imported += 1
            except Exception as e:
                errors.append(f"导入失败 {item.get('node_id', '?')}: {str(e)}")
                skipped += 1

        return {
            "imported": imported,
            "skipped":  skipped,
            "errors":   errors,
        }

    @staticmethod
    def export_to_json(json_path=None):
        """
        @brief  将所有节点导出为 JSON 文件
        @param  json_path  导出路径（默认覆盖初始数据文件）
        @return int        导出的节点数量
        """
        if json_path is None:
            json_path = config.NODE_DATA_JSON

        nodes, _ = Node.get_all(page=1, per_page=10000, status=None)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(nodes, f, ensure_ascii=False, indent=2)

        return len(nodes)

    @staticmethod
    def get_timeline():
        """
        @brief  获取完整时间线（所有节点按时间排序）
        @return list  节点列表（仅含关键字段）的时间线
        """
        nodes, _ = Node.get_all(page=1, per_page=1000, status="active")
        timeline = []
        for n in nodes:
            timeline.append({
                "node_id":  n["node_id"],
                "title":    n["title"],
                "location": n["location"],
                "time":     n["time"],
                "lat":      n["lat"],
                "lng":      n["lng"],
            })
        return sorted(timeline, key=lambda x: x["time"])
