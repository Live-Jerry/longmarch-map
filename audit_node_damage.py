import json, sqlite3

with open("/opt/longmarch-dev/longmarch_route.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"
dev = sqlite3.connect(dev_db)

# Get all nodes
nodes = dev.execute("SELECT node_id, title, lat, lng FROM node ORDER BY id").fetchall()

# Build JSON name->coords
json_coords = {}
for key in data["routes"]:
    for wp in data["routes"][key]["waypoints"]:
        json_coords[wp["name"]] = (wp["lat"], wp["lng"])

# Check what we have now
print("=== Current node table (check for issues) ===")
for n in nodes:
    nid, title, lat, lng = n
    # Check if this node_id is used by multiple route_point waypoints
    rp_waypoints = dev.execute(
        "SELECT name, lat, lng FROM route_point WHERE node_id = ? AND is_node = 1", (nid,)
    ).fetchall()
    if len(rp_waypoints) > 1:
        print(f"\n{nid} {title} ({lat:.4f}, {lng:.4f})")
        for r in rp_waypoints:
            print(f"  -> route_point: {r[0]} ({r[2]:.4f}, {r[1]:.4f}) {'*** DIFFERS ***' if abs(r[1]-lat)>0.001 or abs(r[2]-lng)>0.001 else ''}")
    elif len(rp_waypoints) == 0:
        # No route_point match for this node
        print(f"\n{nid} {title} ({lat:.4f}, {lng:.4f}) - NO route_point match")
    else:
        # Single match - check if it's reasonable
        r = rp_waypoints[0]
        if abs(r[1]-lat) > 0.001 or abs(r[2]-lng) > 0.001:
            print(f"{nid} {title} ({lat:.4f}, {lng:.4f}) rp={r[0]} ({r[2]:.4f}, {r[1]:.4f})")

dev.close()
