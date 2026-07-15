# -*- coding: utf-8 -*-
"""
@file    api/spark_api.py
@brief   星火拾遗 REST API
@details 提供星火内容的提交、查询、待审核列表和管理员审核接口。
         已审核内容对所有用户开放，提交需登录，审核需管理员权限。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

from flask import Blueprint, request, jsonify

from services.spark_manager import SparkManager
from services.auth_manager  import AuthManager


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
# 提交接口（需登录）
# =============================================================================

@spark_bp.route("", methods=["POST"])
def submit_spark():
    """
    @fn    submit_spark
    @brief 提交新的星火内容（需登录）
    @req   JSON: { title, content?, node_id?, media_type?, file_path?, source? }
    @res   { code, data: spark }
    """
    manager = AuthManager()
    user = manager.current_user(request)
    if not user:
        return err("请先登录", code=401, status=401)

    data = request.get_json(silent=True) or {}
    if not data.get("title"):
        return err("标题不能为空")

    data["user_id"] = user["id"]

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
