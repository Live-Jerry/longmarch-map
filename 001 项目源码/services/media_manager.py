# -*- coding: utf-8 -*-
"""
@file    services/media_manager.py
@brief   素材管理服务
@details 处理文件上传、素材审核、素材与节点的关联等业务逻辑。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

import os
import uuid
import mimetypes
from datetime import datetime

import config
from models.media import Media


class MediaManager:
    """
    @class MediaManager
    @brief 素材管理器
    @details 负责处理用户上传的文件（图片、音频、视频），进行存储、
             格式校验、关联写入数据库等操作。
    """

    # 允许的文件类型
    ALLOWED_MIME = {
        "image": ["image/jpeg", "image/png", "image/gif", "image/webp"],
        "audio": ["audio/mpeg", "audio/wav", "audio/ogg", "audio/webm"],
        "video": ["video/mp4", "video/webm"],
        "text":  ["text/plain", "application/pdf"],
    }

    @staticmethod
    def get_upload_dir(media_type):
        """
        @brief  获取指定类型素材的存储目录
        @param  media_type  素材类型
        @return str         目录路径
        """
        upload_dir = os.path.join(config.UPLOAD_DIR, media_type)
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    @staticmethod
    def save_file(file_obj, media_type):
        """
        @brief  保存上传的文件并返回相对路径
        @param  file_obj    Flask FileStorage 对象
        @param  media_type  素材类型（image/audio/video/text）
        @return str         保存后的相对路径
        @raises ValueError  文件类型不支持
        """
        if not file_obj or not file_obj.filename:
            raise ValueError("未提供文件")

        # 检查 MIME 类型
        mime = file_obj.content_type or "application/octet-stream"
        allowed = MediaManager.ALLOWED_MIME.get(media_type, [])
        if allowed and mime not in allowed:
            raise ValueError(f"不支持的文件类型: {mime}，允许: {allowed}")

        # 生成唯一文件名
        ext = os.path.splitext(file_obj.filename)[1].lower()
        unique_name = f"{uuid.uuid4().hex}{ext}"

        upload_dir = MediaManager.get_upload_dir(media_type)
        file_path = os.path.join(upload_dir, unique_name)

        file_obj.save(file_path)

        # 返回相对路径（相对于 static/uploads）
        return os.path.join("uploads", media_type, unique_name)

    @staticmethod
    def create_media(data, file_obj=None):
        """
        @brief  创建素材记录（可带文件）
        @param  data      素材数据字典
        @param  file_obj  可选的 Flask FileStorage 对象
        @return dict      创建的素材数据
        """
        media_type = data.get("type")
        if not media_type:
            raise ValueError("缺少素材类型 type")

        # 如果有文件，先保存
        if file_obj:
            try:
                rel_path = MediaManager.save_file(file_obj, media_type)
                data["file_path"] = rel_path
            except ValueError:
                raise

        return Media.create(data)

    @staticmethod
    def get_media_list(page=1, per_page=20, media_type=None, status=None):
        """
        @brief  分页获取素材列表
        @return dict  包含 items, total, page, per_page, pages
        """
        items, total = Media.get_all(page, per_page, media_type, status)
        return {
            "items":    items,
            "total":    total,
            "page":     page,
            "per_page": per_page,
            "pages":    (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_node_media(node_id, status=None):
        """
        @brief  获取指定节点的所有素材
        @param  node_id  节点编号
        @param  status   状态过滤（默认只返回 approved）
        @return list     素材列表
        """
        return Media.get_by_node(node_id, status)

    @staticmethod
    def review_media(media_id, status, admin_comment=None):
        """
        @brief  审核素材
        @param  media_id       素材 ID
        @param  status         approved | rejected
        @param  admin_comment  审核意见
        """
        return Media.update_status(media_id, status, admin_comment)
