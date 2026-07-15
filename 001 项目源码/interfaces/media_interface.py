# -*- coding: utf-8 -*-
"""
@file    interfaces/media_interface.py
@brief   素材接口定义
@details 定义文件上传、素材查询、素材审核的 API 规范。
@author  长征文化数字地图项目组
@date    2026-07-15

基础 URL: /api/v1/media
"""

# =============================================================================
# GET /media — 素材列表
# =============================================================================
"""
GET /media

描述: 分页获取已审核通过的素材列表（公众可见）。

Query: page, per_page, type(image/audio/video/text)
响应: { code, data: paginated_media }
"""


# =============================================================================
# GET /media/node/<node_id> — 节点素材
# =============================================================================
"""
GET /media/node/<node_id>

描述: 获取指定节点的所有已审核素材。

响应: { code, data: [media_items] }
"""


# =============================================================================
# POST /media/upload — 上传素材
# =============================================================================
"""
POST /media/upload

描述: 上传文件（需登录）。

Content-Type: multipart/form-data

表单字段:
    file        File    必填，支持 jpg/png/gif/mp3/mp4/wav/webm
    type        str     素材类型：image/audio/video/text
    title       str     素材标题
    description str     素材描述
    node_id     str     关联节点编号（可选）

权限: 需要登录用户

响应 (201):
{
    "code": 0,
    "data": {
        "id": 1,
        "type": "image",
        "title": "湘江战役旧址",
        "file_path": "uploads/image/abc123.jpg",
        "status": "pending",
        "created_at": "..."
    }
}
"""


# =============================================================================
# PUT /media/<id>/review — 审核素材（管理员）
# =============================================================================
"""
PUT /media/<id>/review

描述: 审核素材（通过/拒绝）。

权限: admin/super

请求体:
{
    "status":        "approved" | "rejected",
    "admin_comment": "审核意见（可选）"
}
"""
