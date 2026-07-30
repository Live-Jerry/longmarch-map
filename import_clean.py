import json, sqlite3

with open("/opt/longmarch-dev/longmarch_route.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

army_map = {"hongyifang": 1, "hongershi": 2, "hongsifang": 4, "hongershiwu": 25}
dev = sqlite3.connect(dev_db)
dev.execute("DELETE FROM route_point")

# Step 1: import all waypoints - set is_node=1 for all matches initially
total = 0
for key, army_id in army_map.items():
    waypoints = data["routes"][key]["waypoints"]
    for seq_idx, wp in enumerate(waypoints):
        seq = seq_idx + 1
        name = wp["name"]
        lng, lat = wp["lng"], wp["lat"]
        
        # Simple initial matching
        node_match = dev.execute(
            "SELECT node_id FROM node WHERE title = ? OR title LIKE ? OR title = ? LIMIT 1",
            (name, f"%{name}%", name)
        ).fetchone()
        node_id = node_match[0] if node_match else None
        
        dev.execute(
            "INSERT INTO route_point (army, order_index, lat, lng, is_node, node_id, name) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (army_id, seq, lat, lng, 1 if node_id else 0, node_id, name)
        )
        total += 1

# Step 2: deduplicate node_id - only keep FIRST occurrence
dev.execute("""
    UPDATE route_point SET is_node = 0, node_id = NULL 
    WHERE id NOT IN (
        SELECT MIN(id) FROM route_point 
        WHERE node_id IS NOT NULL AND is_node = 1 
        GROUP BY node_id
    )
    AND is_node = 1
""")
removed = dev.execute("SELECT changes()").fetchone()[0]
dev.commit()

print(f"Imported {total} waypoints")
print(f"Removed {removed} duplicate node assignments")

# Verify no dupes
dups = dev.execute("SELECT node_id, name, army FROM route_point WHERE is_node = 1 AND node_id IS NOT NULL").fetchall()
print(f"Unique node markers: {len(dups)}")
for d in dups:
    print(f"  {d[2]} {d[0]:6} {d[1]}")

dev.close()
