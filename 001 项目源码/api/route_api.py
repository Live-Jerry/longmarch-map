# -*- coding: utf-8 -*-
"""
@file    api/route_api.py
@brief   路线相关 REST API
@details 提供长征路线的 GeoJSON 数据、按军队分组的路线、
         自动漫游路径计算等接口。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

from flask import Blueprint, request, jsonify

from services.route_engine import RouteEngine


route_bp = Blueprint("routes", __name__)


def ok(data=None, message="success"):
    return jsonify({"code": 0, "message": message, "data": data}), 200


def err(msg, code=1, status=400):
    return jsonify({"code": code, "message": msg}), status


@route_bp.route("", methods=["GET"])
def list_routes():
    """
    @fn    list_routes
    @brief 获取所有军队的路线数据
    @res   { code, data: { armies: [...] } }
    """
    routes = RouteEngine.get_all_routes()
    armies = list(routes.values())
    return ok({"armies": armies})


@route_bp.route("/<int:army>", methods=["GET"])
def get_route(army):
    """
    @fn    get_route
    @brief 获取指定军队的路线
    @param army  军队编号（1/2/4/25）
    @res   { code, data: route }
    """
    if army not in RouteEngine.ARMY_NAMES:
        return err(f"无效的军队编号: {army}", code=400)

    return ok(RouteEngine.get_route_by_army(army))


@route_bp.route("/geojson", methods=["GET"])
def get_geojson():
    """
    @fn    get_geojson
    @brief 获取路线 GeoJSON（供 Leaflet 直接加载）
    @query army  军队编号（可选，不传则返回所有）
    @res   GeoJSON FeatureCollection
    """
    army = request.args.get("army", type=int)
    geojson = RouteEngine.get_route_geojson(army if army else None)
    return jsonify(geojson)


@route_bp.route("/autowalk", methods=["GET"])
def autowalk():
    """
    @fn    autowalk
    @brief 获取自动漫游路径数据
    @query army         军队编号（必填）
    @query speed_kmh    移动速度（公里/小时），默认 30
    @res   { code, data: { army, segments, total_km, total_hours } }
    """
    army = request.args.get("army", type=int)
    if not army:
        return err("缺少 army 参数")

    speed = request.args.get("speed_kmh", 30.0, type=float)
    return ok(RouteEngine.get_autowalk_path(army, speed))


@route_bp.route("/armies", methods=["GET"])
def list_armies():
    """
    @fn    list_armies
    @brief 获取所有军队列表（编号和名称）
    @res   { code, data: [ { army, name } ] }
    """
    armies = [
        {"army": a, "name": n}
        for a, n in RouteEngine.ARMY_NAMES.items()
    ]
    return ok(armies)
