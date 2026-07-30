import json, sqlite3

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

with open("/opt/longmarch-dev/longmarch_route.json", "r") as f:
    data = json.load(f)

army_map = {
    "hongyifang": (1, "红一方面军"),
    "hongershi": (2, "红二方面军"),
    "hongsifang": (4, "红四方面军"),
    "hongershiwu": (25, "红二十五军"),
}

dev = sqlite3.connect(dev_db)

# Delete ALL existing route_point data
dev.execute("DELETE FROM route_point")
print("Cleared all route_point data")

# Import waypoints
max_id = 0
total = 0
missing_nodes = []

for key, (army_id, army_name) in army_map.items():
    route = data["routes"][key]
    waypoints = route["waypoints"]
    
    for i, wp in enumerate(waypoints):
        max_id += 1
        name = wp["name"]
        lng, lat = wp["lng"], wp["lat"]
        
        # Check if this waypoint matches a node in the node table
        node_match = dev.execute(
            "SELECT node_id FROM node WHERE title LIKE ? OR title LIKE ? OR title LIKE ?",
            (f"%{name}%", f"%{name}（%", f"%{name}→%")
        ).fetchone()
        node_id = node_match[0] if node_match else None
        
        dev.execute(
            "INSERT INTO route_point (id, army, order_index, lat, lng, is_node, node_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (max_id, army_id, i + 1, lat, lng, 1 if node_match else 0, node_id)
        )
        total += 1
        
        if not node_match:
            if name not in missing_nodes:
                missing_nodes.append(name)

dev.commit()
print(f"Imported {total} waypoints")

# Show which waypoints matched nodes
node_matches = dev.execute("SELECT COUNT(*) FROM route_point WHERE is_node = 1").fetchone()[0]
print(f"Node table matches: {node_matches}")
print(f"Unmatched waypoints ({len(missing_nodes)}): {', '.join(missing_nodes[:20])}")

# Show route summary
for army_id in [1, 2, 4, 25]:
    cnt = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ?", (army_id,)).fetchone()[0]
    name = dict(army_map.values()).get(army_id, "?")
    print(f"  Army {army_id} ({name}): {cnt} waypoints")

dev.close()
