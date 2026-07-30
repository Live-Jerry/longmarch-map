import json, sqlite3

with open("/opt/longmarch-dev/longmarch_route.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

army_map = {"hongyifang": 1, "hongershi": 2, "hongsifang": 4, "hongershiwu": 25}

dev = sqlite3.connect(dev_db)
dev.execute("DELETE FROM route_point")

# Track which node_ids have been assigned, to avoid duplicates
assigned_node_ids = set()

total = 0
for key, army_id in army_map.items():
    waypoints = data["routes"][key]["waypoints"]
    for seq_idx, wp in enumerate(waypoints):
        seq = seq_idx + 1
        name = wp["name"]
        lng, lat = wp["lng"], wp["lat"]
        
        # Match node - but only if this node_id hasn't been assigned yet
        node_id = None
        matches = dev.execute(
            "SELECT node_id FROM node WHERE (title LIKE ? OR title LIKE ? OR title = ?) AND title != 'Test' LIMIT 1",
            (f"%{name}%", f"%{name}（%", name)
        ).fetchall()
        
        for m in matches:
            nid = m[0]
            if nid not in assigned_node_ids:
                node_id = nid
                assigned_node_ids.add(nid)
                break
        
        dev.execute(
            "INSERT INTO route_point (army, order_index, lat, lng, is_node, node_id, name) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (army_id, seq, lat, lng, 1 if node_id else 0, node_id, name)
        )
        total += 1

dev.commit()
print(f"Imported {total} waypoints, {len(assigned_node_ids)} unique node matches")

for army_id in [1, 2, 4, 25]:
    cnt = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ?", (army_id,)).fetchone()[0]
    nodes = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ? AND is_node = 1", (army_id,)).fetchone()[0]
    print(f"  Army {army_id}: {cnt} pts, {nodes} unique node matches")

# Verify no dup node_ids
dups = dev.execute("SELECT node_id, COUNT(*) FROM route_point WHERE is_node = 1 AND node_id IS NOT NULL GROUP BY node_id HAVING COUNT(*) > 1").fetchall()
if dups:
    print(f"\nWARNING: Duplicate node_ids still exist:")
    for d in dups[:10]:
        names = dev.execute("SELECT name FROM route_point WHERE node_id = ? AND is_node = 1", (d[0],)).fetchall()
        print(f"  {d[0]}: {d[1]}x - {[n[0] for n in names]}")
else:
    print("\nNo duplicate node_ids (good)")

dev.close()
