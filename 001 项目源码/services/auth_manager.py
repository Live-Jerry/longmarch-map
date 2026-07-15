# -*- coding: utf-8 -*-
"""
@file    services/auth_manager.py
@brief   用户认证服务
@details 提供注册、登录、JWT 令牌生成与验证、权限检查等认证相关业务逻辑。
         基于 SHA-256 密码哈希，实现简单的基于 HMAC 的令牌认证机制。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

import hmac
import hashlib
import base64
import json
import time
from datetime import datetime, timedelta

import config
from models.user import User


class AuthManager:
    """
    @class AuthManager
    @brief 认证管理器
    @details 负责用户注册、登录、令牌签发与验证、会话管理。
             令牌采用 HMAC-SHA256 签名，有效期 7 天。
    """

    def __init__(self):
        self.secret_key = config.Config.SECRET_KEY.encode()
        self.expiration = config.Config.JWT_EXPIRATION_SECONDS

    # =========================================================================
    # 令牌管理
    # =========================================================================

    def generate_token(self, user):
        """
        @brief  为用户生成认证令牌
        @param  user  用户数据字典（包含 id, username, role）
        @return str   Base64 编码的令牌字符串
        """
        payload = {
            "user_id":  user["id"],
            "username": user["username"],
            "role":     user["role"],
            "exp":      int(time.time()) + self.expiration,
            "iat":      int(time.time()),
        }
        # 第一部分：payload JSON
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(payload, ensure_ascii=False).encode()
        ).decode()

        # 第二部分：HMAC 签名
        sig = hmac.new(
            self.secret_key,
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()

        return f"{payload_b64}.{sig}"

    def verify_token(self, token):
        """
        @brief  验证令牌有效性
        @param  token  令牌字符串
        @return dict|None  成功返回 payload，失败返回 None
        """
        try:
            parts = token.split(".")
            if len(parts) != 2:
                return None
            payload_b64, sig = parts

            # 校验签名
            expected_sig = hmac.new(
                self.secret_key,
                payload_b64.encode(),
                hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(sig, expected_sig):
                return None

            # 解析 payload
            payload = json.loads(
                base64.urlsafe_b64decode(payload_b64.encode()).decode()
            )

            # 检查过期
            if payload.get("exp", 0) < int(time.time()):
                return None

            return payload

        except (ValueError, KeyError, json.JSONDecodeError):
            return None

    def token_from_request(self, request):
        """
        @brief  从 Flask 请求中提取令牌
        @param  request  Flask Request 对象
        @return str|None  令牌字符串
        """
        # 优先从 Authorization: Bearer <token> 头获取
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]

        # 其次从 URL query 参数获取
        return request.args.get("token")

    def current_user(self, request):
        """
        @brief  获取当前请求的登录用户
        @param  request  Flask Request 对象
        @return dict|None  用户数据，未登录返回 None
        """
        token = self.token_from_request(request)
        if not token:
            return None
        payload = self.verify_token(token)
        if not payload:
            return None
        # 重新从数据库获取最新用户信息
        return User.get_by_id(payload["user_id"])

    # =========================================================================
    # 认证操作
    # =========================================================================

    def register(self, username, password):
        """
        @brief  用户注册
        @param  username  用户名
        @param  password  密码
        @return tuple     (user, token)  成功返回用户数据和令牌
        @raises ValueError 用户名已存在或密码不合规
        """
        if not username or len(username) < 3:
            raise ValueError("用户名至少需要 3 个字符")
        if not password or len(password) < 6:
            raise ValueError("密码至少需要 6 个字符")

        user = User.create(username, password)
        token = self.generate_token(user)
        return user, token

    def login(self, username, password):
        """
        @brief  用户登录
        @param  username  用户名
        @param  password  密码
        @return tuple     (user, token)  成功返回用户数据和令牌
        @raises ValueError 用户名或密码错误
        """
        user = User.authenticate(username, password)
        if not user:
            raise ValueError("用户名或密码错误")
        token = self.generate_token(user)
        return user, token

    # =========================================================================
    # 权限检查
    # =========================================================================

    @staticmethod
    def require_login(request):
        """
        @brief  要求用户已登录，否则抛出异常
        @raises PermissionError 未登录时抛出
        """
        manager = AuthManager()
        user = manager.current_user(request)
        if not user:
            raise PermissionError("请先登录")
        return user

    @staticmethod
    def require_admin(request):
        """
        @brief  要求用户具有管理员权限
        @raises PermissionError 权限不足时抛出
        """
        user = AuthManager.require_login(request)
        if not User.is_admin(user):
            raise PermissionError("需要管理员权限")
        return user

    @staticmethod
    def require_super(request):
        """
        @brief  要求用户具有超级管理员权限
        @raises PermissionError 权限不足时抛出
        """
        user = AuthManager.require_login(request)
        if not User.is_super(user):
            raise PermissionError("需要超级管理员权限")
        return user
