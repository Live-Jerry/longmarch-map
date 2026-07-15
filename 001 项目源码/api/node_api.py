# -*- coding: utf-8 -*-
"""
@file    api/node_api.py
@brief   节点管理 REST API
@details 提供节点的增删改查和批量导入导出接口。
         GET 接口对所有用户开放，POST/PUT/DELETE 需要管理员权限。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

from flask import Blueprint, request, jsonify

from services.node_manager import NodeManager
from services.auth_manager import AuthManager


node_bp = Blueprint("nodes", __name__)


def ok(data=None, message="success"):
    """@brief 统一成功响应"""
    return jsonify({"code": 0, "message": message, "data": data}), 200


def err(msg, code=1, status=400):
    """@brief 统一错误响应"""
    return jsonify({"code": code, "message": msg}), status


# =============================================================================
# GET 接口（公开）
# =============================================================================

@node_bp.route("", methods=["GET"])
def list_nodes():
    """
    @fn    list_nodes
    @brief 获取节点列表（分页、搜索、省份过滤）
    @query page      页码，默认 1
    @query per_page  每页数量，默认 20
    @query search    关键词（搜索 title / location）
    @query province  省份过滤
    @res   { code, data: { items, total, page, per_page, pages } }
    """
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    search   = request.args.get("search", "").strip() or None
    province = request.args.get("province", "").strip() or None

    data = NodeManager.get_nodes(
        page=page, per_page=per_page,
        search=search, province=province
    )
    return ok(data)


@node_bp.route("/<node_id>", methods=["GET"])
def get_node(node_id):
    """
    @fn    get_node
    @brief 获取单个节点详情
    @param node_id  节点编号
    @res   { code, data: node }
    """
    node = NodeManager.get_node_detail(node_id)
    if not node:
        return err("节点不存在", code=404, status=404)
    return ok(node)


@node_bp.route("/nearby", methods=["GET"])
def nearby_nodes():
    """
    @fn    nearby_nodes
    @brief 获取指定坐标附近的节点
    @query lat       纬度
    @query lng       经度
    @query radius_km 半径（公里），默认 50
    @res   { code, data: [nodes] }
    """
    lat  = request.args.get("lat", type=float)
    lng  = request.args.get("lng", type=float)
    if lat is None or lng is None:
        return err("缺少 lat 或 lng 参数")

    radius = request.args.get("radius_km", 50, type=float)
    nodes  = NodeManager.get_nearby_nodes(lat, lng, radius)
    return ok(nodes)


@node_bp.route("/timeline", methods=["GET"])
def timeline():
    """
    @fn    timeline
    @brief 获取按时间排序的节点时间线
    @res   { code, data: [timeline_items] }
    """
    return ok(NodeManager.get_timeline())


# =============================================================================
# POST 接口（管理员）
# =============================================================================

@node_bp.route("", methods=["POST"])
def create_node():
    """
    @fn    create_node
    @brief 创建新节点（需管理员权限）
    @req   JSON 节点数据
    @res   { code, data: node }
    """
    try:
        AuthManager.require_admin(request)
    except PermissionError as e:
        return err(str(e), code=403, status=403)

    data = request.get_json(silent=True) or {}
    if not data:
        return err("请求体不能为空")

    try:
        node = NodeManager.create_node(data)
        return ok(node), 201
    except ValueError as e:
        return err(str(e))


@node_bp.route("/import", methods=["POST"])
def import_nodes():
    """
    @fn    import_nodes
    @brief 从 JSON 文件批量导入节点（需管理员权限）
    @req   JSON: { json_path }（可选，默认使用配置的初始数据路径）
    @res   { code, data: { imported, skipped, errors } }
    """
    try:
        AuthManager.require_admin(request)
    except PermissionError as e:
        return err(str(e), code=403, status=403)

    data = request.get_json(silent=True) or {}
    json_path = data.get("json_path")

    try:
        result = NodeManager.import_from_json(json_path)
        return ok(result)
    except (FileNotFoundError, ValueError) as e:
        return err(str(e))


@node_bp.route("/export", methods=["POST"])
def export_nodes():
    """
    @fn    export_nodes
    @brief 导出所有节点到 JSON 文件（需管理员权限）
    @res   { code, data: { count } }
    """
    try:
        AuthManager.require_admin(request)
    except PermissionError as e:
        return err(str(e), code=403, status=403)

    count = NodeManager.export_to_json()
    return ok({"count": count})


# =============================================================================
# PUT 接口（管理员）
# =============================================================================

@node_bp.route("/<node_id>", methods=["PUT"])
def update_node(node_id):
    """
    @fn    update_node
    @brief 更新节点信息（需管理员权限）
    @param node_id  节点编号
    @req   JSON  更新字段
    @res   { code, data: node }
    """
    try:
        AuthManager.require_admin(request)
    except PermissionError as e:
        return err(str(e), code=403, status=403)

    data = request.get_json(silent=True) or {}
    if not data:
        return err("请求体不能为空")

    try:
        node = NodeManager.update_node(node_id, data)
        return ok(node)
    except ValueError as e:
        return err(str(e), code=404, status=404)


# =============================================================================
# DELETE 接口（管理员）
# =============================================================================

@node_bp.route("/<node_id>", methods=["DELETE"])
def delete_node(node_id):
    """
    @fn    delete_node
    @brief 删除节点（软删除，管理员）
    @query hard  是否永久删除，默认 false
    @res   { code, message }
    """
    try:
        AuthManager.require_admin(request)
    except PermissionError as e:
        return err(str(e), code=403, status=403)

    hard = request.args.get("hard", "false").lower() == "true"

    try:
        NodeManager.remove_node(node_id, hard=hard)
        return ok(message="节点已删除")
    except ValueError as e:
        return err(str(e), code=404, status=404)
