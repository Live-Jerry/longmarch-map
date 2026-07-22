# -*- coding: utf-8 -*-
"""
@file    api/spark_api.py
@brief   星火拾遗 REST API
@details 提供星火内容的提交、查询、待审核列表和管理员审核接口。
         已审核内容对所有用户开放，公开提交（无需登录），审核需管理员权限。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

import os
from flask import Blueprint, request, jsonify

from services.spark_manager import SparkManager
from services.auth_manager  import AuthManager
import config as app_config


spark_bp = Blueprint("sparks", __name__)


def ok(data=None, message="success"):
    return jsonify({"code": 0, "message": message, "data": data}), 200


def err(msg, code=1, status=400):
    return jsonify({"code": code, "message": msg}), status


# =============================================================================
# 公开查询接口
# =============================================================================

@spark_bp.route("", methods=["GET"])
def list_sparks():
    """
    @fn    list_sparks
    @brief 获取已审核通过的星火列表（公众可见）
    @query page     页码
    @query per_page 每页数量
    @query node_id  节点编号过滤
    @res   { code, data: paginated_sparks }
    """
    page     = request.args.get("page",     1,  type=int)
    per_page = request.args.get("per_page", 20, type=int)
    node_id  = request.args.get("node_id", "").strip() or None

    return ok(SparkManager.get_sparks(page, per_page, node_id))


@spark_bp.route("/<int:spark_id>", methods=["GET"])
def get_spark(spark_id):
    """
    @fn    get_spark
    @brief 获取单个星火内容详情
    @param spark_id  星火 ID
    @res   { code, data: spark }
    """
    from models.spark import Spark
    spark = Spark.get_by_id(spark_id)
    if not spark:
        return err("星火内容不存在", code=404, status=404)
    # 非管理员只能看 approved
    manager = AuthManager()
    user = manager.current_user(request)
    if spark["status"] != "approved" and not (user and user.get("role") in ("admin", "super")):
        return err("该内容暂不可见", code=403, status=403)
    return ok(spark)


@spark_bp.route("/stats", methods=["GET"])
def spark_stats():
    """
    @fn    spark_stats
    @brief 获取星火系统统计信息
    @res   { code, data: { pending, approved, rejected, total } }
    """
    return ok(SparkManager.get_stats())


# =============================================================================
# 提交接口（无需登录）
# =============================================================================

@spark_bp.route("", methods=["POST"])
def submit_spark():
    """
    @fn    submit_spark
    @brief 提交新的星火内容（无需登录）
    @req   JSON: { title, content?, node_id?, media_type?, file_path?, source? }
    @res   { code, data: spark }
    """
    data = request.get_json(silent=True) or {}
    if not data.get("title"):
        return err("标题不能为空")

    # 登录用户取 user_id，未登录用户存提交者信息
    manager = AuthManager()
    user = manager.current_user(request)
    data["user_id"] = user["id"] if user else None

    try:
        spark = SparkManager.submit_spark(data)
        return ok(spark), 201
    except ValueError as e:
        return err(str(e))


@spark_bp.route("/my", methods=["GET"])
def my_sparks():
    """
    @fn    my_sparks
    @brief 获取当前用户提交的所有星火
    @res   { code, data: paginated_sparks }
    """
    manager = AuthManager()
    user = manager.current_user(request)
    if not user:
        return err("请先登录", code=401, status=401)

    page     = request.args.get("page",     1,  type=int)
    per_page = request.args.get("per_page", 20, type=int)
    return ok(SparkManager.get_user_sparks(user["id"], page, per_page))


# =============================================================================
# 管理员接口
# =============================================================================

@spark_bp.route("/pending", methods=["GET"])
def pending_sparks():
    """
    @fn    pending_sparks
    @brief 获取所有待审核星火（管理员）
    @res   { code, data: [sparks] }
    """
    try:
        AuthManager.require_admin(request)
    except PermissionError as e:
        return err(str(e), code=403, status=403)

    return ok(SparkManager.get_pending_sparks())


@spark_bp.route("/<int:spark_id>/review", methods=["PUT"])
def review_spark(spark_id):
    """
    @fn    review_spark
    @brief 审核星火内容（管理员）
    @param spark_id  星火 ID
    @req   JSON: { status: "approved"|"rejected", admin_comment? }
    @res   { code, data: spark }
    """
    try:
        AuthManager.require_admin(request)
    except PermissionError as e:
        return err(str(e), code=403, status=403)

    data = request.get_json(silent=True) or {}
    status = data.get("status", "")
    if status not in ("approved", "rejected"):
        return err("status 必须是 approved 或 rejected")

    try:
        spark = SparkManager.review_spark(
            spark_id, status,
            admin_comment=data.get("admin_comment")
        )
        return ok(spark)
    except ValueError as e:
        return err(str(e), code=404, status=404)


@spark_bp.route("/<int:spark_id>", methods=["DELETE"])
def delete_spark(spark_id):
    """
    @fn    delete_spark
    @brief 删除星火内容（管理员）
    @param spark_id  星火 ID
    """
    try:
        AuthManager.require_admin(request)
    except PermissionError as e:
        return err(str(e), code=403, status=403)

    from models.spark import Spark
    Spark.delete(spark_id)
    return ok(message="星火内容已删除")


@spark_bp.route("/full", methods=["POST"])
def create_full_spark():
    """
    @fn    create_full_spark
    @brief 提交完整节点维度星火（包含全部节点字段 + 文件上传）
    @details 用户通过前端弹窗提交，支持新建节点和补充既有节点两种模式。
             无需登录即可提交，提交者信息（姓名/电话）可选填写。
             文件上传至 002 项目资源/星火上传/ 目录。
             数据以 JSON 格式存入 spark 表的 content 字段。
    @request JSON/form-data
    @response JSON
    """
    manager = AuthManager()
    user = manager.current_user(request)

    # 收集表单数据
    submission_type = request.form.get("submission_type", "new-node")
    node_id = request.form.get("node_id", "")
    target_node_id = request.form.get("target_node_id", "")

    if submission_type == "update-node" and not target_node_id:
        return err("补充模式请选择目标节点", code=400, status=400)
    if submission_type == "new-node" and not node_id:
        return err("新建模式请填写节点编号", code=400, status=400)

    # 构建内容 JSON
    fields = [
        "title", "location", "time", "core_numbers",
        "famous_battle", "important_meeting", "history_event",
        "core_site", "poem_article", "typical_story",
        "typical_people", "historical_significance"
    ]
    content = {"type": submission_type}
    if submission_type == "new-node":
        content["node_id"] = node_id
        content["lat"] = request.form.get("lat", "")
        content["lng"] = request.form.get("lng", "")
    else:
        content["target_node_id"] = target_node_id

    for f in fields:
        val = request.form.get(f, "")
        if val:
            content[f] = val

    # 上传者信息
    submitter = {}
    for key in ["submitter_name", "submitter_phone", "source"]:
        val = request.form.get(key, "")
        if val:
            submitter[key.replace("submitter_", "")] = val
    if submitter:
        content["submitter"] = submitter

    # 处理文件上传
    from werkzeug.utils import secure_filename
    project_root = os.path.dirname(app_config.BASE_DIR)
    upload_dir = os.path.join(project_root, "002 项目资源", "星火上传")
    os.makedirs(upload_dir, exist_ok=True)

    uploads = {"images": [], "videos": [], "audios": [], "documents": []}
    allowed_exts = {
        "images": (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"),
        "videos": (".mp4", ".avi", ".mov", ".wmv", ".flv"),
        "audios": (".mp3", ".wav", ".ogg", ".aac", ".wma"),
        "documents": (".pdf", ".doc", ".docx", ".txt")
    }

    for field_name in uploads:
        files = request.files.getlist(field_name)
        for f in files:
            if f and f.filename:
                ext = os.path.splitext(f.filename)[1].lower()
                if ext in allowed_exts.get(field_name, ()):
                    safe_name = secure_filename(f.filename)
                    # 添加时间戳防止重名
                    import time
                    stamp = str(int(time.time()))
                    safe_name = stamp + "_" + safe_name
                    save_path = os.path.join(upload_dir, safe_name)
                    f.save(save_path)
                    uploads[field_name].append(safe_name)

    if any(uploads.values()):
        content["uploads"] = uploads

    # 保存到数据库
    from models.spark import Spark
    import json as jsonlib
    import datetime
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # 尝试获取节点名称
    node_name = node_id or target_node_id or ""
    if submission_type == "update-node" and target_node_id:
        from services.node_manager import NodeManager
        nm = NodeManager()
        n = nm.get_by_id(target_node_id)
        if n:
            node_name = n.get("title") or n.get("location") or target_node_id

    spark_data = {
        "node_id": node_name,
        "user_id": user["id"] if user else None,
        "title": request.form.get("title", "星火拾遗投稿") or "星火拾遗投稿",
        "content": jsonlib.dumps(content, ensure_ascii=False),
        "media_type": "text",
        "source": request.form.get("source", ""),
        "status": "pending",
        "created_at": now
    }

    result = Spark.create(spark_data)
    return ok(data={"id": result["id"]}, message="星火提交成功，等待审核")

