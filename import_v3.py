import json, sqlite3

with open("/opt/longmarch-dev/longmarch_route.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"
army_map = {"hongyifang": 1, "hongershi": 2, "hongsifang": 4, "hongershiwu": 25}
dev = sqlite3.connect(dev_db)
dev.execute("DELETE FROM route_point")

# Explicit name->node_id mapping for problematic matches
explicit_map = {
    "安顺场": "7.1",   # 四川安顺场 -> node 7.1
    "安顺": None,      # 贵州安顺 - not a node
    "威信": "4.4",     # 威信 is the same as 扎西
}

total = 0
for key, army_id in army_map.items():
    waypoints = data["routes"][key]["waypoints"]
    for seq_idx, wp in enumerate(waypoints):
        seq = seq_idx + 1
        name = wp["name"]
        lng, lat = wp["lng"], wp["lat"]
        
        if name in explicit_map:
            node_id = explicit_map[name]
        else:
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

# Deduplicate: only keep first occurrence per node_id
dev.execute("""
    UPDATE route_point SET is_node = 0, node_id = NULL 
    WHERE id NOT IN (
        SELECT MIN(id) FROM route_point 
        WHERE node_id IS NOT NULL AND is_node = 1 
        GROUP BY node_id
    )
    AND is_node = 1
""")
dev.commit()

print(f"Imported {total} waypoints")

# Show all unique node markers with their names
markers = dev.execute("SELECT node_id, name, army, order_index FROM route_point WHERE is_node = 1 AND node_id IS NOT NULL ORDER BY army, order_index").fetchall()
print(f"Unique node markers: {len(markers)}")
for m in markers:
    print(f"  Army {m[2]} [{m[3]:3d}] {m[0]:6} {m[1]}")

# Check if 安顺 is no longer matched
an_shun = dev.execute("SELECT name, is_node, node_id FROM route_point WHERE name IN ('安顺', '安顺场', '石棉')").fetchall()
print(f"\nAnshun check: {an_shun}")

dev.close()
