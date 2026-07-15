# -*- coding: utf-8 -*-
"""
@file    interfaces/route_interface.py
@brief   路线接口定义
@details 定义长征路线查询、GeoJSON 获取、自动漫游路径的 API 规范。
@author  长征文化数字地图项目组
@date    2026-07-15

基础 URL: /api/v1/routes
"""

# =============================================================================
# GET /routes — 获取所有军队路线
# =============================================================================
"""
GET /routes

描述: 获取所有军队的长征路线数据。

响应 (200):
{
    "code": 0,
    "data": {
        "armies": [
            {
                "army": 1,
                "name": "中央红军（红一方面军）",
                "points": [...],
                "geojson": { "type": "LineString", "coordinates": [...] }
            },
            ...
        ]
    }
}
"""


# =============================================================================
# GET /routes/<army> — 获取指定军队路线
# =============================================================================
"""
GET /routes/<army>

描述: 获取指定军队的路线详情。

路径参数:
    army    int   军队编号（1/2/4/25）

响应 (200): 返回单个 army 的路线对象
错误 (400): 无效的军队编号
"""


# =============================================================================
# GET /routes/geojson — 获取路线 GeoJSON
# =============================================================================
"""
GET /routes/geojson

描述: 获取 GeoJSON FeatureCollection（供 Leaflet 直接加载）。

Query 参数:
    army    int   可选，指定军队编号，不传则返回所有

响应 (200): 直接返回 GeoJSON 对象（不是 JSON 包装）
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": { "army": 1, "name": "中央红军（红一方面军）" },
            "geometry": { "type": "LineString", "coordinates": [...] }
        }
    ]
}
"""


# =============================================================================
# GET /routes/autowalk — 自动漫游路径
# =============================================================================
"""
GET /routes/autowalk

描述: 获取自动漫游路径数据（含时间估算）。

Query 参数:
    army        int     军队编号，必填
    speed_kmh   float   移动速度（km/h），默认 30

响应 (200):
{
    "code": 0,
    "data": {
        "army": 1,
        "name": "中央红军（红一方面军）",
        "segments": [
            {
                "index": 0,
                "node_id": "001",
                "title": "瑞金",
                "lat": 25.8833,
                "lng": 116.0200,
                "dist_km": 0,
                "duration_h": 0
            },
            {
                "index": 1,
                "node_id": "002",
                "title": "湘江",
                "lat": 25.6,
                "lng": 110.5,
                "dist_km": 412.5,
                "duration_h": 13.75
            }
        ],
        "total_km": 12500,
        "total_hours": 416.67,
        "speed_kmh": 30
    }
}
"""
