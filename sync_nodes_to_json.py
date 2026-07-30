import json, sqlite3

with open("/opt/longmarch-dev/longmarch_route.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"
dev = sqlite3.connect(dev_db)

# Build name->coords from JSON
json_coords = {}
for key in data["routes"]:
    for wp in data["routes"][key]["waypoints"]:
        json_coords[wp["name"]] = (wp["lat"], wp["lng"])

# Update node table where route_point matches
updated = 0
for (name, (lat, lng)) in json_coords.items():
    # Find matching node via route_point node_id
    rp = dev.execute("SELECT DISTINCT node_id FROM route_point WHERE name = ? AND node_id IS NOT NULL", (name,)).fetchone()
    if rp:
        nid = rp[0]
        n = dev.execute("SELECT lat, lng FROM node WHERE node_id = ?", (nid,)).fetchone()
        if n and (abs(n[0] - lat) > 0.001 or abs(n[1] - lng) > 0.001):
            dev.execute("UPDATE node SET lat = ?, lng = ? WHERE node_id = ?", (lat, lng, nid))
            print(f"  {nid:8} {name:10} old({n[0]:.4f},{n[1]:.4f}) -> JSON({lat:.4f},{lng:.4f})")
            updated += 1

dev.commit()
print(f"\nUpdated {updated} nodes to match JSON coordinates")

# Sync route_point is_node=1 to node table
dev.execute("""
    UPDATE route_point 
    SET lat = (SELECT lat FROM node WHERE node.node_id = route_point.node_id),
        lng = (SELECT lng FROM node WHERE node.node_id = route_point.node_id)
    WHERE is_node = 1 AND node_id IN (SELECT node_id FROM node)
""")
dev.commit()
print("Synced route_point node coords to node table")

dev.close()
