import sqlite3, json

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

# Add name column to route_point
dev = sqlite3.connect(dev_db)
try:
    dev.execute("ALTER TABLE route_point ADD COLUMN name TEXT")
    dev.commit()
    print("Added name column")
except Exception as e:
    print(f"Column may already exist: {e}")

# Load JSON waypoints with names
with open("/opt/longmarch-dev/longmarch_route.json", "r") as f:
    data = json.load(f)

army_map = {"hongyifang": 1, "hongershi": 2, "hongsifang": 4, "hongershiwu": 25}

# Build a mapping of (army, order_index) -> name from JSON
wp_names = {}
for key, army_id in army_map.items():
    route = data["routes"][key]
    for i, wp in enumerate(route["waypoints"]):
        order = i + 1
        wp_names[(army_id, order)] = wp["name"]

# Update route_point with names
updated = 0
for (army, order), name in wp_names.items():
    cur = dev.execute("UPDATE route_point SET name = ? WHERE army = ? AND order_index = ?", (name, army, order))
    if cur.rowcount > 0:
        updated += cur.rowcount

dev.commit()
print(f"Updated {updated} route_points with names")

# Verify - show a few
rows = dev.execute("SELECT army, order_index, name, is_node FROM route_point WHERE army = 1 AND order_index <= 10 ORDER BY order_index").fetchall()
for r in rows:
    print(f"  Army {r[0]} [{r[1]}] {r[2]:<12} is_node={r[3]}")

dev.close()
