import json, sqlite3

with open("/opt/longmarch-dev/longmarch_route.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

army_map = {
    "hongyifang": (1, "红一方面军（中央红军）"),
    "hongershi": (2, "红二方面军"),
    "hongsifang": (4, "红四方面军"),
    "hongershiwu": (25, "红二十五军"),
}

dev = sqlite3.connect(dev_db)
cur = dev.execute("PRAGMA table_info(route_point)")
cols = [c[1] for c in cur.fetchall()]
has_name = "name" in cols
print(f"Has name column: {has_name}")

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
        
        # Match node by name
        node_match = dev.execute(
            "SELECT node_id FROM node WHERE (title LIKE ? OR title LIKE ? OR title LIKE ?) AND title != 'Test' LIMIT 1",
            (f"%{name}%", f"%{name}（%", f"%→ {name}%")
        ).fetchone()
        node_id = node_match[0] if node_match else None
        
        if has_name:
            dev.execute(
                "INSERT INTO route_point (army, order_index, lat, lng, is_node, node_id, name) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (army_id, i + 1, lat, lng, 1 if node_match else 0, node_id, name)
            )
        else:
            dev.execute(
                "INSERT INTO route_point (army, order_index, lat, lng, is_node, node_id) VALUES (?, ?, ?, ?, ?, ?)",
                (army_id, i + 1, lat, lng, 1 if node_match else 0, node_id)
            )
        total += 1

dev.commit()
print(f"Imported {total} waypoints")

# Summary
for army_id in [1, 2, 4, 25]:
    cnt = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ?", (army_id,)).fetchone()[0]
    nodes = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ? AND is_node = 1", (army_id,)).fetchone()[0]
    print(f"  Army {army_id}: {cnt} total, {nodes} matched to nodes")

# Verify 苍溪 in Army 4
gx = dev.execute("SELECT order_index, lat, lng, name, is_node, node_id FROM route_point WHERE army = 4 AND name = '苍溪'").fetchall()
print(f"\n苍溪 in Army 4 route: {gx}")

ct = dev.execute("SELECT order_index, lat, lng, name, is_node, node_id FROM route_point WHERE army = 1 AND name = '长汀'").fetchall()
print(f"长汀 in Army 1 route: {ct}")

dev.close()
