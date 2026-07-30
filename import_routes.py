# Re-import route_point from 长征路线完整坐标数据2.0.json
# This file is the authoritative source for route waypoint coordinates

import sqlite3, json, os

DB_PATH = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"
JSON_PATH = os.path.expanduser("~/长征路线完整坐标数据2.0.json")

# Army name mapping
ARMY_MAP = {"hongyifang": 1, "hongershi": 2, "hongsifang": 4, "hongershiwu": 25}

# Load JSON
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Load node table for node_id matching
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT node_id, title, location FROM node")
nodes = c.fetchall()
node_lookup = {}
for nid, title, loc in nodes:
    node_lookup[title] = nid
    if loc:
        node_lookup[loc] = nid
    # Also add short name
    if title and "（" in title:
        node_lookup[title.split("（")[0]] = nid

print("=== Re-importing route_points ===")

# Clear existing route_points
c.execute("DELETE FROM route_point")
conn.commit()

total = 0
matched = 0

for army_key, route_data in data["routes"].items():
    army = ARMY_MAP[army_key]
    print(f"\n[{route_data['name']}] (army={army})")
    
    for idx, wp in enumerate(route_data["waypoints"]):
        name = wp["name"]
        lat = wp["lat"]
        lng = wp["lng"]
        
        # Try to match to node_id
        node_id = None
        for key, nid in node_lookup.items():
            if key and name in key:
                node_id = nid
                break
        
        # Also try exact match
        for key, nid in node_lookup.items():
            if key and name == key.split("（")[0]:
                node_id = nid
                break
        
        if node_id:
            matched += 1
        
        is_node = 1 if node_id else 0
        
        c.execute(
            "INSERT INTO route_point (army, lat, lng, order_index, is_node, node_id, name) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (army, lat, lng, idx, is_node, node_id, name)
        )
        total += 1
    
    print(f"  Imported {len(route_data['waypoints'])} waypoints")

conn.commit()
conn.close()

print(f"\nTotal: {total} points, {matched} matched to nodes")
print("Route_Point re-import complete!")
print("Restart gunicorn on dev server to apply.")
