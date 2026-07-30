import re

with open("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/static/js/map.js", "r", encoding="utf-8") as f:
    content = f.read()

# Find the loadRoutes function and add a loadRoutePoints function + call
old_func = '''async function loadRoutes() {
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

        console.log("[Map] ✅ 路线绘制完成（平滑曲线）");
    } catch (e) {
        console.error("[Map] 路线加载失败", e);
    }
}'''

new_func = '''/**
 * @function loadRoutePoints
 * @brief 加载路线点数据，为带名称的非节点添加文字标记
 */
async function loadRoutePoints() {
    try {
        const resp = await fetch("/api/v1/routes");
        const result = await resp.json();
        if (!result.data?.armies) return;

        result.data.armies.forEach(function(armyData) {
            var points = armyData.points || [];
            var army = armyData.army;
            var color = armyColors[army] || "#e74c3c";

            points.forEach(function(p) {
                if (p.is_node === 1) return;
                var name = p.name || "";
                if (!name) return;

                var icon = L.divIcon({
                    className: "waypoint-label",
                    html: '<div style="display:flex;align-items:center;gap:2px;">' +
                          '<span style="width:5px;height:5px;border-radius:50%;background:' + color + ';display:inline-block;"></span>' +
                          '<span style="font-size:10px;color:#333;text-shadow:0 0 3px #fff,0 0 3px #fff;white-space:nowrap;">' + name + '</span>' +
                          '</div>',
                    iconSize: [0, 0],
                    iconAnchor: [0, 0]
                });
                var marker = L.marker([p.lat, p.lng], { icon: icon });
                marker.addTo(map.routeGroup);
            });
        });

        console.log("[Map] 路线地名点标记完成");
    } catch (e) {
        console.error("[Map] 路线地名点加载失败", e);
    }
}

async function loadRoutes() {
    try {
        const resp = await fetch("/api/v1/routes/geojson");
        const geojson = await resp.json();
        if (!geojson.features) return;

        geojson.features.forEach(function(feature) {
            const army = feature.properties?.army;
            const color = armyColors[army] || "#e74c3c";

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

            var first = smoothCoords[0];
            var last = smoothCoords[smoothCoords.length - 1];
            L.circleMarker([first[1], first[0]], {
                radius: 6, color: color, fillColor: "#fff", fillOpacity: 1, weight: 3
            }).addTo(map.routeGroup);
            L.circleMarker([last[1], last[0]], {
                radius: 6, color: color, fillColor: color, fillOpacity: 1, weight: 3
            }).addTo(map.routeGroup);
        });

        loadRoutePoints();

        console.log("[Map] ✅ 路线绘制完成（平滑曲线）");
    } catch (e) {
        console.error("[Map] 路线加载失败", e);
    }
}'''

# Normalize line endings to match
old_func_n = old_func.replace('\n', '\r\n')
new_func_n = new_func.replace('\n', '\r\n')

if old_func_n in content:
    content = content.replace(old_func_n, new_func_n)
    with open("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/static/js/map.js", "w", encoding="utf-8", newline='\r\n') as f:
        f.write(content)
    print("SUCCESS: Patched loadRoutes + added loadRoutePoints")
else:
    print("ERROR: old function text not found in file")
    # Debug: find approximate location
    idx = content.find("async function loadRoutes")
    if idx >= 0:
        print(f"Found at position {idx}")
        print(content[idx:idx+100])
    else:
        print("loadRoutes not found at all")
