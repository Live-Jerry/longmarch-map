# -*- coding: utf-8 -*-
"""
@file    services/route_engine.py
@brief   路线引擎服务
@details 负责长征路线的查询、按军队分组、自动漫游路径计算等逻辑。
         路线数据存储在 route_point 表，各支军队分开记录。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

import sqlite3
from flask import g

import config


class RouteEngine:
    """
    @class RouteEngine
    @brief 路线引擎
    @details 提供长征路线数据查询、路线可视化数据生成、自动漫游路径计算。
             支持按军队（1/2/4/25）分组查询。
    """

    # 军队常量
    ARMY_1  = 1   # 中央红军（红一方面军）
    ARMY_2  = 2   # 红二方面军
    ARMY_4  = 4   # 红四方面军
    ARMY_25 = 25  # 红二十五军

    ARMY_NAMES = {
        ARMY_1:  "中央红军（红一方面军）",
        ARMY_2:  "红二方面军",
        ARMY_4:  "红四方面军",
        ARMY_25: "红二十五军",
    }

    @staticmethod
    def get_all_routes():
        """
        @brief  获取所有军队的路线数据
        @return dict  按 army 分组的路线点列表
        """
        conn = g.db
        rows = conn.execute(
            """SELECT rp.*, n.title as node_title, n.location
               FROM route_point rp
               LEFT JOIN node n ON rp.node_id = n.node_id
               ORDER BY rp.army, rp.order_index"""
        ).fetchall()

        routes = {}
        for row in rows:
            army = row["army"]
            if army not in routes:
                routes[army] = {
                    "army":     army,
                    "name":     RouteEngine.ARMY_NAMES.get(army, f"红军{army}军"),
                    "points":   [],
                    "geojson":  None,
                }
            routes[army]["points"].append(dict(row))

        # 生成 GeoJSON LineString
        for army_data in routes.values():
            points = army_data["points"]
            if points:
                coords = [[p["lng"], p["lat"]] for p in points]
                army_data["geojson"] = {
                    "type":        "LineString",
                    "coordinates": coords,
                }

        return routes

    @staticmethod
    def get_route_by_army(army):
        """
        @brief  获取指定军队的路线
        @param  army  军队编号（1/2/4/25）
        @return dict  路线数据（含 GeoJSON）
        """
        conn = g.db
        rows = conn.execute(
            """SELECT rp.*, n.title as node_title, n.location
               FROM route_point rp
               LEFT JOIN node n ON rp.node_id = n.node_id
               WHERE rp.army = ?
               ORDER BY rp.order_index""",
            (army,)
        ).fetchall()

        points = [dict(r) for r in rows]
        coords = [[p["lng"], p["lat"]] for p in points]

        return {
            "army":    army,
            "name":    RouteEngine.ARMY_NAMES.get(army, f"红军{army}军"),
            "points":  points,
            "geojson": {
                "type":        "LineString",
                "coordinates": coords,
            } if coords else None,
        }

    @staticmethod
    def get_route_geojson(army=None):
        """
        @brief  获取路线的 GeoJSON 格式数据（供 Leaflet 地图直接使用）
        @param  army  军队编号（None 表示所有军队）
        @return dict  GeoJSON FeatureCollection
        """
        if army:
            routes = [RouteEngine.get_route_by_army(army)]
        else:
            all_routes = RouteEngine.get_all_routes()
            routes = list(all_routes.values())

        features = []
        for r in routes:
            if r["geojson"]:
                # 收集路线点的标题（用于地图上的文字标注）
                pt_labels = []
                for p in r["points"]:
                    title = p.get("node_title") or p.get("name") or p.get("location", "")
                    pt_labels.append({
                        "lat": p["lat"],
                        "lng": p["lng"],
                        "title": title,
                    })

                features.append({
                    "type": "Feature",
                    "properties": {
                        "army": r["army"],
                        "name": r["name"],
                        "points": pt_labels,
                    },
                    "geometry": r["geojson"],
                })

        return {
            "type":     "FeatureCollection",
            "features": features,
        }

    @staticmethod
    def get_autowalk_path(army, speed_kmh=30.0):
        """
        @brief  计算自动漫游路径（带时间估算）
        @param  army         军队编号
        @param  speed_kmh    假设移动速度（公里/小时），默认 30 km/h（乘车）
        @return dict         路径数据，含每个节点的时间估算
        """
        route = RouteEngine.get_route_by_army(army)
        points = route["points"]

        if not points:
            return {"army": army, "segments": [], "total_km": 0, "total_hours": 0}

        import math
        total_km = 0.0
        segments = []

        for i, point in enumerate(points):
            if i == 0:
                seg = {
                    "index":      i,
                    "node_id":    point.get("node_id"),
                    "title":      point.get("node_title") or point.get("name", point.get("location", "")),
                    "lat":        point["lat"],
                    "lng":        point["lng"],
                    "dist_km":    0,
                    "duration_h": 0,
                }
            else:
                prev = points[i - 1]
                dist = RouteEngine._haversine_km(
                    prev["lat"], prev["lng"],
                    point["lat"], point["lng"]
                )
                total_km += dist
                duration = dist / speed_kmh

                seg = {
                    "index":      i,
                    "node_id":    point.get("node_id"),
                    "title":      point.get("node_title") or point.get("name", point.get("location", "")),
                    "lat":        point["lat"],
                    "lng":        point["lng"],
                    "dist_km":    round(dist, 2),
                    "duration_h": round(duration, 2),
                }
            segments.append(seg)

        total_hours = total_km / speed_kmh

        return {
            "army":         army,
            "name":         route["name"],
            "segments":     segments,
            "total_km":     round(total_km, 2),
            "total_hours":  round(total_hours, 2),
            "speed_kmh":    speed_kmh,
        }

    @staticmethod
    def _haversine_km(lat1, lng1, lat2, lng2):
        """
        @brief  计算两点间的球面距离（公里）
        @param  lat1, lng1  第一个点的纬度和经度
        @param  lat2, lng2  第二个点的纬度和经度
        @return float       距离（公里）
        """
        import math
        R = 6371.0  # 地球半径（公里）

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lng2 - lng1)

        a = math.sin(dphi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    @staticmethod
    def init_route_points(army, points):
        """
        @brief  批量插入路线点（初始化用）
        @param  army   军队编号
        @param  points list of dict，含 lat, lng, order_index, is_node, node_id, stage
        """
        conn = g.db
        # 先删除旧数据
        conn.execute("DELETE FROM route_point WHERE army = ?", (army,))

        for p in points:
            conn.execute(
                """INSERT INTO route_point
                   (army, stage, lat, lng, order_index, is_node, node_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (army, p.get("stage"), p["lat"], p["lng"],
                 p["order_index"], int(p.get("is_node", False)), p.get("node_id"))
            )
        conn.commit()
