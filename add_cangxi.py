import sqlite3, json

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"
dev = sqlite3.connect(dev_db)

# Get current max id
max_id = dev.execute("SELECT COALESCE(MAX(id), 0) FROM route_point").fetchone()[0]

# Read JSON to check original data
with open("/opt/longmarch-dev/longmarch_route.json", "r") as f:
    data = json.load(f)

hongsi = data["routes"]["hongsifang"]["waypoints"]
print("Original 红四方面军 waypoints:")
for i, wp in enumerate(hongsi):
    print(f"  [{i+1}] {wp['name']:<8} ({wp['lat']:.4f}, {wp['lng']:.4f})")

# Add 苍溪 (Cangxi) between order_index 2 (南江) and 3 (广元)
# Shift all subsequent order_index by +1
cangxi_lat = 31.935
cangxi_lng = 106.163

# Shift indices for army 4, order > 2
dev.execute("UPDATE route_point SET order_index = order_index + 1 WHERE army = 4 AND order_index > 2")

# Insert 苍溪 at order_index 3
next_id = max_id + 1
dev.execute(
    "INSERT INTO route_point (id, army, order_index, lat, lng, is_node, node_id, name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    (next_id, 4, 3, cangxi_lat, cangxi_lng, 1, "S1.1", "苍溪")
)
dev.commit()

print(f"\nAdded 苍溪 at order_index=3, id={next_id}")

# Verify
pts = dev.execute("SELECT order_index, name, lat, lng FROM route_point WHERE army = 4 ORDER BY order_index LIMIT 8").fetchall()
for p in pts:
    print(f"  [{p[0]}] {p[1]:<8} ({p[2]:.4f}, {p[3]:.4f})")

# Check 苍溪 node
n = dev.execute("SELECT node_id, title, lat, lng FROM node WHERE node_id = 'S1.1'").fetchone()
print(f"\nNode S1.1 苍溪: ({n[2]:.4f},{n[3]:.4f})")
print(f"Route point 苍溪: ({cangxi_lat},{cangxi_lng})")

dev.close()
