# -*- coding: utf-8 -*-
"""
@file    services/spark_manager.py
@brief   星火拾遗服务
@details 处理星火内容的提交、查询、审核、统计等业务逻辑。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

from models.spark import Spark
import config


class SparkManager:
    """
    @class SparkManager
    @brief 星火系统管理器
    @details "星火拾遗"模块的核心业务逻辑封装。
             负责内容提交、待审核列表查询、审核操作和统计。
    """

    @staticmethod
    def get_sparks(page=1, per_page=None, node_id=None):
        """
        @brief  获取已审核通过的星火列表（供公众访问）
        @return dict  分页数据
        """
        if per_page is None:
            per_page = config.Config.DEFAULT_PER_PAGE

        items, total = Spark.get_all(page=page, per_page=per_page,
                                      status="approved", node_id=node_id)
        return {
            "items":    items,
            "total":    total,
            "page":     page,
            "per_page": per_page,
            "pages":    (total + per_page - 1) // per_page,
        }

    @staticmethod
    def submit_spark(data):
        """
        @brief  提交新的星火内容
        @param  data  包含 title, content, node_id, user_id, media_type, file_path, source
        @return dict  创建的星火数据
        """
        required = ("title",)
        for field in required:
            if not data.get(field):
                raise ValueError(f"缺少必填字段: {field}")

        return Spark.create(data)

    @staticmethod
    def get_pending_sparks():
        """
        @brief  获取所有待审核星火（供管理员）
        @return list  待审核星火列表
        """
        return Spark.get_pending()

    @staticmethod
    def review_spark(spark_id, status, admin_comment=None):
        """
        @brief  审核星火内容
        @param  spark_id       星火 ID
        @param  status         approved | rejected
        @param  admin_comment  审核意见
        @return dict           审核后的星火数据
        """
        return Spark.review(spark_id, status, admin_comment)

    @staticmethod
    def get_user_sparks(user_id, page=1, per_page=None):
        """
        @brief  获取指定用户提交的星火列表
        @return dict  分页数据
        """
        if per_page is None:
            per_page = config.Config.DEFAULT_PER_PAGE

        items, total = Spark.get_by_user(user_id, page, per_page)
        return {
            "items":    items,
            "total":    total,
            "page":     page,
            "per_page": per_page,
            "pages":    (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_stats():
        """
        @brief  获取星火系统统计信息
        @return dict  pending / approved / rejected / total 数量
        """
        return Spark.get_stats()
