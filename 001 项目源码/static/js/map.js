/* -*- coding: utf-8 -*- */
/**
 * @file    map.js
 * @brief   Leaflet 地图初始化模块
 * @details 负责地图创建、底图加载、节点标记、路线绘制、点击事件绑定。
 *          使用 ArcGIS 卫星影像作为底图，支持全屏展示和底图切换。
 * @author  长征文化数字地图项目组
 * @date    2026-07-15
 */

const map = {};
const nodeMarkers = {};
const nodeArmies = {};  // army -> [nodeId, ...]
const routeLayers = {};
let currentBaseLayer = "satellite";

const armyColors = {
    1:  "#e74c3c",   // 中央红军 — 红色
    2:  "#27ae60",   // 红二方面军 — 绿色
    4:  "#2980b9",   // 红四方面军 — 蓝色
    25: "#8e44ad",   // 红二十五军 — 紫色
};

const armyNames = {
    1:  "中央红军（红一方面军）",
    2:  "红二方面军",
    4:  "红四方面军",
    25: "红二十五军",
};

/**
 * @function initMap
 * @brief 初始化 Leaflet 地图
 * @details ArcGIS 卫星影像作为默认底图，备选 CartoDB 轻量/深色地图。
 */
function initMap() {
    // 卫星底图
    const satellite = L.tileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        { attribution: "&copy; Esri", maxZoom: 18 }
    );
    // OSM 标准地图
    const osm = L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
        { subdomains: ["a","b","c","d"], attribution: "&copy; OSM", maxZoom: 19 }
    );
    // 深色地图
    const dark = L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
        { subdomains: ["a","b","c","d"], attribution: "&copy; OSM", maxZoom: 19 }
    );

    map.instance = L.map("map", {
        center: [31.5, 108.5],
        zoom: 5,
        minZoom: 4,
        maxZoom: 18,
        zoomControl: false,
        attributionControl: false,
        layers: [satellite],
    });

    // 底图层引用
    map.layers = { satellite, osm, dark };

    L.control.zoom({ position: "bottomright" }).addTo(map.instance);

    // 节点图层组
    map.nodeGroup = L.layerGroup().addTo(map.instance);
    // 路线图层组
    map.routeGroup = L.layerGroup().addTo(map.instance);

    // 加载节点，然后从节点数据生成预置边界
    loadNodes().then(function(nodesData) {
        if (nodesData && nodesData.length > 0) {
            var boundsAll = L.latLngBounds();
            nodesData.forEach(function(n) {
                if (n.lat && n.lng) {
                    boundsAll.extend([parseFloat(n.lat), parseFloat(n.lng)]);
                }
            });
            if (boundsAll.isValid()) {
                // 加一点缓冲（10%），确保节点不贴边
                map.instance.fitBounds(boundsAll, { padding: [100, 100] });
                console.log("[Map] 缩放到全路线 +40% 缓冲");
            }
        }
    });
    loadRoutes();
    console.log("[Map] 地图初始化完成 (ArcGIS卫星)");
}

/**
 * @function loadNodes
 * @brief 从 API 加载节点标记
 */
async function loadNodes() {
    try {
        const resp = await fetch("/api/v1/nodes?per_page=1000");
        const json = await resp.json();
        if (json.code !== 0) return [];
        const nodes = json.data?.items || json.data?.nodes || [];
        nodes.forEach(addNodeMarker);
        // 全局暴露，供其他模块（如星火拾遗）使用
        window.allNodes = nodes;
        console.log(`[Map]  节点: ${nodes.length} 个`);
        return nodes;
    } catch (e) {
        console.error("[Map] 节点加载失败", e);
        return [];
    }
}

/**
 * @function getShortName
 * @brief 从节点数据中提取简洁显示名（去掉省份前缀、括号备注等）
 */
function getShortName(node) {
    var name = node.title || node.location || "";
    // 去掉常见省份前缀
    var provinces = ["江西", "福建", "贵州", "云南", "四川", "湖南", "广西",
                     "甘肃", "陕西", "宁夏", "重庆", "湖北", "河南", "广东"];
    for (var i = 0; i < provinces.length; i++) {
        if (name.indexOf(provinces[i]) === 0) {
            name = name.substring(provinces[i].length);
            break;
        }
    }
    // 去掉括号及括号内内容
    var parenIdx = name.indexOf("（");
    if (parenIdx > 0) name = name.substring(0, parenIdx);
    parenIdx = name.indexOf("(");
    if (parenIdx > 0) name = name.substring(0, parenIdx);
    // 去掉箭头分隔（取后半段更常用的地名）
    var arrowIdx = name.indexOf("→");
    if (arrowIdx > 0) name = name.substring(0, arrowIdx).trim();
    // 去掉顿号分隔（取第一项）
    var commaIdx = name.indexOf("、");
    if (commaIdx > 0) name = name.substring(0, commaIdx).trim();
    return name.trim() || (node.title || "");
}

/**
 * @function buildFlagSvg
 * @brief 生成红一方面军军旗 SVG（16×13px）
 */
function buildFlagSvg() {
    return '<svg class="flag-marker-svg" width="16" height="13" viewBox="0 0 16 13" xmlns="http://www.w3.org/2000/svg">' +
        '<rect x="0.5" y="0.5" width="14.5" height="11.5" rx="0.8" ' +
        'fill="#c0392b" stroke="rgba(255,255,255,0.6)" stroke-width="0.6"/>' +
        '<polygon points="2.5,2.0 2.9,3.0 4.0,3.0 3.1,3.7 3.4,4.8 2.5,4.1 1.6,4.8 1.9,3.7 1.0,3.0 2.1,3.0" ' +
        'fill="#ffd700"/>' +
        '</svg>';
}

/**
 * @function addNodeMarker
 * @brief 添加单个节点标记（红一方面军军旗形）
 */
function addNodeMarker(node) {
    if (!node.lat || !node.lng) return;

    var displayName = getShortName(node);
    var flagSvg = buildFlagSvg();

    var icon = L.divIcon({
        html: '<div class="flag-marker-wrapper">' +
              '<div class="flag-marker-label">' + displayName + '</div>' +
              flagSvg +
              '</div>',
        className: "",
        iconSize: [16, 26],
        iconAnchor: [8, 26],
        popupAnchor: [0, -28],
    });

    var marker = L.marker([node.lat, node.lng], { icon: icon });
    var title = node.title || "";
    var loc = node.location || "";
    var time = node.time || "";

    marker.bindPopup(
        '<div class="popup-mini">' +
        '<div class="popup-mini-title">' + title + '</div>' +
        '<div class="popup-mini-sub">' + time + ' · ' + loc + '</div>' +
        '<div class="popup-mini-hint">点击查看详情 →</div></div>',
        { maxWidth: 280, className: "node-popup" }
    );

    marker.on("click", function() {
        // 如果漫游激活，跳转到该节点继续漫游
        if (window.autowalkState && window.autowalkState.active) {
            if (typeof jumpAutowalkToNode === "function") {
                jumpAutowalkToNode(node.node_id);
                return;
            }
        }
        if (typeof showNodePanel === "function") showNodePanel(node);
    });

    marker.addTo(map.nodeGroup);
    nodeMarkers[node.node_id] = marker;

    // 按军队分组记录节点
    var army = node.army || "中央红军（红一方面军）";
    var armyMap = {"中央红军（红一方面军）":1,"中央红军":1,"红二方面军":2,"红四方面军":4,"红25军":25};
    var aNum = armyMap[army] || 1;
    if (!nodeArmies[aNum]) nodeArmies[aNum] = [];
    nodeArmies[aNum].push(node.node_id);
}

/**
 * @function filterNodesByArmy
 * @brief 显示/隐藏节点标记，按军队筛选
 * @param {number} army  0=全部显示, 1/2/4/25=只显示该军
 */
function filterNodesByArmy(army) {
    if (army === 0) {
        // 全部显示
        for (var nid in nodeMarkers) {
            map.nodeGroup.addLayer(nodeMarkers[nid]);
        }
        return;
    }

    // 先隐藏所有节点
    for (var nid in nodeMarkers) {
        map.nodeGroup.removeLayer(nodeMarkers[nid]);
    }

    // 再显示选中军队的节点
    var ids = nodeArmies[army] || [];
    ids.forEach(function(nid) {
        var m = nodeMarkers[nid];
        if (m) map.nodeGroup.addLayer(m);
    });
}

/**
 * @function loadRoutes
 * @brief 加载路线 GeoJSON 并绘制平滑曲线
 */
async function loadRoutes() {
    try {
        const resp = await fetch("/api/v1/routes/geojson");
        const geojson = await resp.json();
        if (!geojson.features) return;

        geojson.features.forEach(function(feature) {
            const army = feature.properties?.army;
            const color = armyColors[army] || "#e74c3c";

            // 用 Catmull-Rom 样条平滑：对原始坐标点按 8x 密度插值
            var coords = feature.geometry.coordinates;
            var smoothCoords = smoothCurve(coords, 8);

            var layer = L.polyline(smoothCoords, {
                color: color,
                weight: 3.5,
                opacity: 0.85,
                smoothFactor: 1.5,
            });

            layer.addTo(map.routeGroup);
            routeLayers[army] = layer;

            // 起点/终点标记
            var first = smoothCoords[0];
            var last = smoothCoords[smoothCoords.length - 1];
            L.circleMarker([first[1], first[0]], {
                radius: 6, color: color, fillColor: "#fff", fillOpacity: 1, weight: 3
            }).addTo(map.routeGroup);
            L.circleMarker([last[1], last[0]], {
                radius: 6, color: color, fillColor: color, fillOpacity: 1, weight: 3
            }).addTo(map.routeGroup);
        });

        console.log("[Map]  路线绘制完成（平滑曲线）");
    } catch (e) {
        console.error("[Map] 路线加载失败", e);
    }
}

/**
 * @function smoothCurve
 * @brief Catmull-Rom 样条插值，将折线变为平滑曲线
 * @param {Array} coords  [[lng,lat], ...] 原始坐标
 * @param {number} segments  每段之间的插值点数
 * @returns {Array} [[lat,lng], ...] 平滑后的坐标
 */
function smoothCurve(coords, segments) {
    if (!coords || coords.length < 2) return (coords || []).map(c => [c[1], c[0]]);
    var result = [];

    function lerp(a, b, t) { return a + (b - a) * t; }

    for (var i = 0; i < coords.length - 1; i++) {
        var p0 = coords[Math.max(0, i - 1)];
        var p1 = coords[i];
        var p2 = coords[i + 1];
        var p3 = coords[Math.min(coords.length - 1, i + 2)];

        for (var j = 0; j < segments; j++) {
            var t = j / segments;
            // Catmull-Rom
            var t2 = t * t, t3 = t2 * t;
            var x = 0.5 * (
                (2 * p1[0]) +
                (-p0[0] + p2[0]) * t +
                (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
            );
            var y = 0.5 * (
                (2 * p1[1]) +
                (-p0[1] + p2[1]) * t +
                (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
            );
            result.push([y, x]);  // Leaflet 需要 [lat, lng]
        }
    }
    // 最后一个点
    var last = coords[coords.length - 1];
    result.push([last[1], last[0]]);

    return result;
}

/**
 * @function switchBaseLayer
 * @brief 切换底图
 * @param {string} type 'satellite' | 'osm' | 'dark'
 */
function switchBaseLayer(type) {
    if (!map.instance || !map.layers[type]) return;
    for (var k in map.layers) {
        if (map.instance.hasLayer(map.layers[k])) {
            map.instance.removeLayer(map.layers[k]);
        }
    }
    map.layers[type].addTo(map.instance);
    currentBaseLayer = type;
}

/**
 * @function flyToNode
 * @brief 地图飞到指定节点
 */
function flyToNode(nodeId) {
    var marker = nodeMarkers[nodeId];
    if (marker) {
        map.instance.flyTo(marker.getLatLng(), 10, { duration: 1.5 });
    }
}

/**
 * @function toggleArmy
 * @brief 显示/隐藏军队路线，同时同步筛选节点
 * @param {number} army  0=全部显示, 1=中央红军, 2=红二, 4=红四, 25=红25
 */
function toggleArmy(army) {
    var allArmies = [1, 2, 4, 25];

    if (army === 0) {
        // 全部显示：添加所有军队路线 + 所有节点
        allArmies.forEach(function(a) {
            var layer = routeLayers[a];
            if (layer && !map.instance.hasLayer(layer)) {
                layer.addTo(map.instance);
            }
        });
        filterNodesByArmy(0);
        return;
    }

    // 单选一支军队：先移除所有路线，再添加选中的
    allArmies.forEach(function(a) {
        var layer = routeLayers[a];
        if (layer && map.instance.hasLayer(layer)) {
            map.instance.removeLayer(layer);
        }
    });

    var selected = routeLayers[army];
    if (selected) {
        selected.addTo(map.instance);
    }

    // 同步筛选节点：只显示该军队的节点
    filterNodesByArmy(army);
}

window.toggleArmy = toggleArmy;
window.filterNodesByArmy = filterNodesByArmy;

window.map = map;
window.initMap = initMap;
window.loadNodes = loadNodes;
window.loadRoutes = loadRoutes;
window.switchBaseLayer = switchBaseLayer;
window.flyToNode = flyToNode;
