# -*- coding: utf-8 -*-
"""
@file    api/auth_api.py
@brief   认证相关 REST API
@details 提供用户注册、登录、当前用户信息获取等接口。
         所有令牌通过 Authorization: Bearer <token> 头传递。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

from flask import Blueprint, request, jsonify

from services.auth_manager import AuthManager


auth_bp = Blueprint("auth", __name__)


# =============================================================================
# 工具函数
# =============================================================================

def ok(data=None, message="success"):
    """@brief 统一成功响应格式"""
    return jsonify({"code": 0, "message": message, "data": data}), 200


def err(message, code=1, status=400):
    """@brief 统一错误响应格式"""
    return jsonify({"code": code, "message": message}), status


# =============================================================================
# 路由
# =============================================================================

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    @fn    register
    @brief 用户注册接口
    @req   JSON: { username, password }
    @res   { code, message, data: { user, token } }
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return err("用户名和密码不能为空")

    try:
        manager = AuthManager()
        user, token = manager.register(username, password)
        return ok({
            "user":  user,
            "token": token,
        })
    except ValueError as e:
        return err(str(e))


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    @fn    login
    @brief 用户登录接口
    @req   JSON: { username, password }
    @res   { code, message, data: { user, token } }
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    try:
        manager = AuthManager()
        user, token = manager.login(username, password)
        return ok({
            "user":  user,
            "token": token,
        })
    except ValueError:
        return err("用户名或密码错误", code=401, status=401)


@auth_bp.route("/me", methods=["GET"])
def me():
    """
    @fn    me
    @brief 获取当前登录用户信息
    @req   Header: Authorization: Bearer <token>
    @res   { code, message, data: user }
    """
    manager = AuthManager()
    user = manager.current_user(request)
    if not user:
        return err("未登录或令牌无效", code=401)
    return ok(user)


@auth_bp.route("/token/verify", methods=["POST"])
def verify_token():
    """
    @fn    verify_token
    @brief 验证令牌有效性
    @req   JSON: { token }
    @res   { code, message, data: payload }
    """
    data = request.get_json(silent=True) or {}
    token = data.get("token", "")
    if not token:
        # 尝试从 header 获取
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]

    manager = AuthManager()
    payload = manager.verify_token(token)
    if not payload:
        return err("令牌无效或已过期", code=401)
    return ok(payload)
