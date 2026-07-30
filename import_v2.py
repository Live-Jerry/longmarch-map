import json, sqlite3

with open("/opt/longmarch-dev/longmarch_route.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

army_map = {
    "hongyifang": (1, "红一方面军"),
    "hongershi": (2, "红二方面军"),
    "hongsifang": (4, "红四方面军"),
    "hongershiwu": (25, "红二十五军"),
}

dev = sqlite3.connect(dev_db)
dev.execute("DELETE FROM route_point")

total = 0
for key, (army_id, army_name) in army_map.items():
    waypoints = data["routes"][key]["waypoints"]
    for seq_idx, wp in enumerate(waypoints):
        seq = seq_idx + 1  # sequential 1-based
        name = wp["name"]
        lng, lat = wp["lng"], wp["lat"]
        
        # Match node by name (exact)
        node_match = dev.execute(
            "SELECT node_id FROM node WHERE (title LIKE ? OR title LIKE ? OR title LIKE ? OR title = ?) AND title != 'Test' LIMIT 1",
            (f"%{name}%", f"%{name}（%", f"%→ {name}%", name)
        ).fetchone()
        node_id = node_match[0] if node_match else None
        
        dev.execute(
            "INSERT INTO route_point (army, order_index, lat, lng, is_node, node_id, name) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (army_id, seq, lat, lng, 1 if node_match else 0, node_id, name)
        )
        total += 1

dev.commit()
print(f"Imported {total} waypoints total")
for army_id in [1, 2, 4, 25]:
    cnt = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ?", (army_id,)).fetchone()[0]
    nodes = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ? AND is_node = 1", (army_id,)).fetchone()[0]
    print(f"  Army {army_id}: {cnt} waypoints, {nodes} node matches")

# Show notable new entries
for name in ["水田寨", "皎平渡", "元谋", "昆明", "巴中", "旺苍", "毕节", "赫章", "奎香", "镇雄", "宣威", "盘县", "蔡川", "镇安", "葛牌"]:
    rp = dev.execute("SELECT army, order_index, lat, lng, is_node, node_id FROM route_point WHERE name = ?", (name,)).fetchone()
    if rp:
        a, oi, lat, lng, inode, nid = rp
        print(f"  {name:8} Army {a} seq={oi} ({lat:.4f},{lng:.4f}) node={nid}")
    else:
        print(f"  {name:8} NOT FOUND")

dev.close()
