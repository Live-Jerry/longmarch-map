import json, sqlite3

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

with open("/opt/longmarch-dev/longmarch_route.json", "r") as f:
    data = json.load(f)

# Build name->coords map from JSON waypoints
json_coords = {}
for key in data["routes"]:
    route = data["routes"][key]
    for wp in route["waypoints"]:
        json_coords[wp["name"]] = (wp["lat"], wp["lng"])

dev = sqlite3.connect(dev_db)

# Update node table where coords differ
nodes = dev.execute("SELECT node_id, title, lat, lng FROM node ORDER BY id").fetchall()
updated = 0
for nid, title, db_lat, db_lng in nodes:
    # Try to find matching JSON entry
    matched_coords = None
    for name, (lat, lng) in json_coords.items():
        if name in title or title.split("（")[0].strip() == name:
            matched_coords = (lat, lng)
            break
    
    if matched_coords:
        jlat, jlng = matched_coords
        if abs(jlat - db_lat) > 0.001 or abs(jlng - db_lng) > 0.001:
            print(f"UPDATE {nid} {title}: DB({db_lat:.4f},{db_lng:.4f}) -> JSON({jlat:.4f},{jlng:.4f})")
            dev.execute("UPDATE node SET lat = ?, lng = ? WHERE node_id = ?", (jlat, jlng, nid))
            updated += 1
        else:
            pass  # Already correct
    else:
        print(f"SKIP {nid} {title}: no JSON match")

dev.commit()
print(f"\nUpdated {updated} nodes")

# Verify route_point matches node table
mismatches = dev.execute("""
    SELECT r.node_id, r.lat, r.lng, n.lat, n.lng
    FROM route_point r
    JOIN node n ON n.node_id = r.node_id
    WHERE r.is_node = 1 AND (abs(r.lat - n.lat) > 0.001 OR abs(r.lng - n.lng) > 0.001)
""").fetchall()
print(f"Route-point/Node mismatches: {len(mismatches)}")
if mismatches:
    for m in mismatches[:5]:
        print(f"  {m[0]}: rp({m[1]:.4f},{m[2]:.4f}) vs node({m[3]:.4f},{m[4]:.4f})")

# Also sync route_point is_node=1 to node coords
dev.execute("""
    UPDATE route_point
    SET lat = (SELECT lat FROM node WHERE node.node_id = route_point.node_id),
        lng = (SELECT lng FROM node WHERE node.node_id = route_point.node_id)
    WHERE is_node = 1 AND node_id IN (SELECT node_id FROM node)
""")
dev.commit()

final = dev.execute("""
    SELECT r.node_id, r.lat, r.lng, n.lat, n.lng
    FROM route_point r
    JOIN node n ON n.node_id = r.node_id
    WHERE r.is_node = 1 AND (abs(r.lat - n.lat) > 0.001 OR abs(r.lng - n.lng) > 0.001)
""").fetchall()
print(f"Final mismatches: {len(final)}")

dev.close()
