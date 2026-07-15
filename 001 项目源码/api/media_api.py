# -*- coding: utf-8 -*-
"""
@file    api/media_api.py
@brief   素材管理 REST API
@details 提供素材上传、列表查询、审核等接口。
         上传需要登录用户，审核需要管理员权限。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

import os
from flask import Blueprint, request, jsonify, current_app

from services.media_manager import MediaManager
from services.auth_manager  import AuthManager
import config


media_bp = Blueprint("media", __name__)


def ok(data=None, message="success"):
    return jsonify({"code": 0, "message": message, "data": data}), 200


def err(msg, code=1, status=400):
    return jsonify({"code": code, "message": msg}), status


# =============================================================================
# 查询接口（公开）
# =============================================================================

@media_bp.route("", methods=["GET"])
def list_media():
    """
    @fn    list_media
    @brief 分页获取素材列表（仅返回已审核通过的）
    @query page       页码
    @query per_page   每页数量
    @query type       素材类型过滤（image/audio/video/text）
    @res   { code, data: paginated_media }
    """
    page     = request.args.get("page",     1,  type=int)
    per_page = request.args.get("per_page", 20, type=int)
    media_type = request.args.get("type", "").strip() or None

    data = MediaManager.get_media_list(page, per_page, media_type, status="approved")
    return ok(data)


@media_bp.route("/<int:media_id>", methods=["GET"])
def get_media(media_id):
    """
    @fn    get_media
    @brief 获取单个素材详情
    @param media_id  素材 ID
    @res   { code, data: media }
    """
    from models.media import Media
    media = Media.get_by_id(media_id)
    if not media:
        return err("素材不存在", code=404, status=404)
    return ok(media)


@media_bp.route("/node/<node_id>", methods=["GET"])
def node_media(node_id):
    """
    @fn    node_media
    @brief 获取指定节点的所有已审核素材
    @param node_id  节点编号
    @res   { code, data: [media] }
    """
    return ok(MediaManager.get_node_media(node_id, status="approved"))


# =============================================================================
# 上传接口（需登录）
# =============================================================================

@media_bp.route("/upload", methods=["POST"])
def upload_media():
    """
    @fn    upload_media
    @brief 上传素材文件（需登录）
    @req   multipart/form-data: file, type, title, description, node_id
    @res   { code, data: media }
    """
    user = _require_login()
    if isinstance(user, tuple):
        return user

    if "file" not in request.files:
        return err("未上传文件")

    file_obj    = request.files["file"]
    media_type  = request.form.get("type", "image")
    title       = request.form.get("title", file_obj.filename or "未命名")
    description = request.form.get("description", "")
    node_id     = request.form.get("node_id", "")

    data = {
        "type":        media_type,
        "title":       title,
        "description": description,
        "node_id":     node_id,
        "uploader_id": user["id"],
    }

    try:
        media = MediaManager.create_media(data, file_obj)
        return ok(media), 201
    except ValueError as e:
        return err(str(e))


# =============================================================================
# 审核接口（管理员）
# =============================================================================

@media_bp.route("/<int:media_id>/review", methods=["PUT"])
def review_media(media_id):
    """
    @fn    review_media
    @brief 审核素材（管理员）
    @req   JSON: { status: "approved"|"rejected", admin_comment? }
    @res   { code, data: media }
    """
    admin = _require_admin()
    if isinstance(admin, tuple):
        return admin

    data = request.get_json(silent=True) or {}
    status = data.get("status", "")
    if status not in ("approved", "rejected"):
        return err("status 必须是 approved 或 rejected")

    try:
        media = MediaManager.review_media(
            media_id, status,
            admin_comment=data.get("admin_comment")
        )
        return ok(media)
    except Exception as e:
        return err(str(e), code=500)


# =============================================================================
# 辅助函数
# =============================================================================

def _require_login():
    """检查登录，返回 user 或错误响应"""
    manager = AuthManager()
    user = manager.current_user(request)
    if not user:
        return err("请先登录", code=401, status=401)
    return user


def _require_admin():
    """检查管理员权限，返回 admin user 或错误响应"""
    try:
        return AuthManager.require_admin(request)
    except PermissionError as e:
        return err(str(e), code=403, status=403)
