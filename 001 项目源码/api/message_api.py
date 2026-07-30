# -*- coding: utf-8 -*-
"""
@file    api/message_api.py
@brief   留言板 REST API
@author  长征文化数字地图项目组
@date    2026-07-27
"""

from flask import Blueprint, request, jsonify
from models.message import Message

message_bp = Blueprint("message", __name__)


@message_bp.route("", methods=["GET"])
def list_messages():
    """获取留言列表（公开）"""
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)
    messages = Message.get_all(limit=limit, offset=offset)
    count = Message.get_count()
    return jsonify({"code": 0, "data": messages, "total": count})


@message_bp.route("", methods=["POST"])
def add_message():
    """提交留言（公开）"""
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"code": 1, "message": "内容不能为空"}), 400
    user_name = (data.get("user_name") or "").strip()
    user_id = (data.get("user_id") or "").strip()
    node_id = (data.get("node_id") or "").strip()
    msg_id = Message.add(content, user_name, user_id, node_id)
    return jsonify({"code": 0, "data": {"id": msg_id}, "message": "留言成功"})


@message_bp.route("/admin", methods=["GET"])
def admin_list():
    """获取留言列表（管理后台使用，完整字段）"""
    limit = request.args.get("limit", 200, type=int)
    offset = request.args.get("offset", 0, type=int)
    messages = Message.get_all(limit=limit, offset=offset)
    count = Message.get_count()
    return jsonify({"code": 0, "data": messages, "total": count})


@message_bp.route("/<int:msg_id>", methods=["DELETE"])
def delete_message(msg_id):
    """删除留言"""
    Message.delete(msg_id)
    return jsonify({"code": 0, "message": "已删除"})
