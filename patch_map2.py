import re

path = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/static/js/map.js"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the exact loadRoutes function boundaries
start_marker = "async function loadRoutes()"
end_marker = "console.error(\"[Map]"

start_idx = content.find(start_marker)
if start_idx < 0:
    print("ERROR: loadRoutes not found")
    exit(1)

# Find the end - the closing } before the next function or comment
# Look for "async function" or "/**" after the end of loadRoutes
search_from = start_idx + len(start_marker)
end_of_func = content.find("}\n\n/**", search_from)
if end_of_func < 0:
    end_of_func = content.find("}\n\nasync", search_from)
if end_of_func < 0:
    # Try just finding the closing bracket pattern
    print("Looking for function end...")
    # Find the second-to-last } before smoothCurve
    smooth_idx = content.find("function smoothCurve", search_from)
    if smooth_idx > 0:
        # Find the last } before smoothCurve
        end_of_func = content.rfind("}", search_from, smooth_idx)

if end_of_func < 0:
    print(f"ERROR: Could not find end of loadRoutes. start={start_idx}")
    print(content[start_idx:start_idx+500])
    exit(1)

# Extract the old function text (including closing })
old_func = content[start_idx:end_of_func+1]  # Include the closing }

print(f"Extracted old function: {len(old_func)} chars")
print(f"First line: {old_func.split(chr(10))[0]}")

# Add loadRoutePoints function before loadRoutes
new_func_to_add = '''/**
 * @function loadRoutePoints
 * @brief 加载路线点数据，为带名称的非节点添加地名标记
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

'''

# Also add loadRoutePoints() call at the end of loadRoutes
# Find the last console.log inside loadRoutes
call_marker = 'console.log("[Map]'
call_idx = content.find(call_marker, start_idx, end_of_func)
if call_idx < 0:
    print("ERROR: console.log not found inside loadRoutes")
    print(content[start_idx:start_idx+500])
    exit(1)

# Find the end of this line
line_end = content.find("\n", call_idx)
if line_end < 0:
    line_end = end_of_func

# Insert loadRoutePoints() call before this line ends
insertion = content[call_idx:line_end]
new_line = "        // 为路线添加地名标记\n        loadRoutePoints();\n\n        " + insertion.lstrip()
content = content[:call_idx] + new_line + content[line_end:]

# Insert the new function before loadRoutes
content = content[:start_idx] + new_func_to_add + content[start_idx:]

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Patched map.js")
print(f"File size: {len(content)} bytes")
