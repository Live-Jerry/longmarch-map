import sqlite3

old_db = "/root/longmarch/longmarch_app/data/longmarch.db"
dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

# Get route_point data from old DB
old = sqlite3.connect(old_db)
cur = old.execute("SELECT id, army, stage, lat, lng, order_index, is_node, node_id FROM route_point ORDER BY id")
old_rows = cur.fetchall()
print(f"OLD DB: {len(old_rows)} route_point rows")
old.close()

# Overwrite dev route_point
dev = sqlite3.connect(dev_db)
cur = dev.execute("SELECT COUNT(*) FROM route_point")
print(f"DEV DB before: {cur.fetchone()[0]} rows")

dev.execute("DELETE FROM route_point")
dev.executemany("INSERT INTO route_point (id, army, stage, lat, lng, order_index, is_node, node_id) VALUES (?,?,?,?,?,?,?,?)", old_rows)
dev.commit()

cur = dev.execute("SELECT COUNT(*) FROM route_point")
print(f"DEV DB after: {cur.fetchone()[0]} rows")

# Verify sample
cur = dev.execute("SELECT id, lat, lng, is_node, node_id FROM route_point WHERE is_node=0 ORDER BY id LIMIT 5")
for r in cur.fetchall():
    print(f"  interp id={r[0]}: ({r[1]:.4f}, {r[2]:.4f})")

dev.close()
print("Done.")
