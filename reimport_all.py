import json, sqlite3

# Read the authoritative JSON from local workspace
with open("D:\\长征文化\\000 脚本策划\\长征路线完整坐标数据.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

army_map = {
    "hongyifang": (1, "红一方面军（中央红军）"),
    "hongershi": (2, "红二方面军"),
    "hongsifang": (4, "红四方面军"),
    "hongershiwu": (25, "红二十五军"),
}

dev = sqlite3.connect(dev_db)

# Clear all route_point
dev.execute("DELETE FROM route_point")
print("Cleared route_point")

# Re-import all waypoints
total = 0
for key, (army_id, army_name) in army_map.items():
    route = data["routes"][key]
    waypoints = route["waypoints"]
    
    for i, wp in enumerate(waypoints):
        name = wp["name"]
        lng, lat = wp["lng"], wp["lat"]
        
        # Check if this waypoint matches a node in the node table
        node_match = dev.execute(
            "SELECT node_id FROM node WHERE (title LIKE ? OR title LIKE ? OR title LIKE ? OR title LIKE ?) AND title != 'Test'",
            (f"%{name}%", f"%{name}（%", f"%{name}→%", f"%（{name}）%")
        ).fetchone()
        node_id = node_match[0] if node_match else None
        
        dev.execute(
            "INSERT INTO route_point (army, order_index, lat, lng, is_node, node_id, name) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (army_id, i + 1, lat, lng, 1 if node_match else 0, node_id, name)
        )
        total += 1

dev.commit()
print(f"Imported {total} waypoints")

# Show summary
for army_id in [1, 2, 4, 25]:
    cnt = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ?", (army_id,)).fetchone()[0]
    nodes = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ? AND is_node = 1", (army_id,)).fetchone()[0]
    print(f"  Army {army_id}: {cnt} total, {nodes} matched to nodes")

# Verify 苍溪 in Army 4 route
gx = dev.execute("SELECT order_index, lat, lng, name, is_node, node_id FROM route_point WHERE army = 4 AND name = '苍溪'").fetchall()
print(f"\n苍溪 in route: {gx}")

# Verify 长汀 in Army 1 route
ct = dev.execute("SELECT order_index, lat, lng, name, is_node, node_id FROM route_point WHERE army = 1 AND name = '长汀'").fetchall()
print(f"长汀 in route: {ct}")

dev.close()

# Also save the JSON to the dev server
import shutil
dest = "/opt/longmarch-dev/longmarch_route.json"
print(f"\nJSON saved to dev server at: {dest}")
