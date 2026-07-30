import sqlite3

# Restore interpolation points from old backup
# Strategy: only touch is_node=0 (interpolation points), keep already-corrected is_node=1 points

backup_db = "/root/longmarch/longmarch_app/data/longmarch.db"
dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

backup = sqlite3.connect(backup_db)
dev = sqlite3.connect(dev_db)

# Get backup interpolation points (is_node=0)
backup_interp = backup.execute(
    "SELECT army, order_index, lat, lng, is_node, node_id FROM route_point WHERE is_node = 0 ORDER BY army, order_index"
).fetchall()

print(f"Backup has {len(backup_interp)} interpolation points (is_node=0)")

# Get current dev interpolation points count
dev_interp_count = dev.execute("SELECT COUNT(*) FROM route_point WHERE is_node = 0").fetchone()[0]
print(f"Dev currently has {dev_interp_count} interpolation points")

# Get current dev node points count
dev_node_count = dev.execute("SELECT COUNT(*) FROM route_point WHERE is_node = 1").fetchone()[0]
print(f"Dev currently has {dev_node_count} node points (is_node=1)")

# Delete ALL interpolation points from dev
dev.execute("DELETE FROM route_point WHERE is_node = 0")
removed = dev_interp_count

# Insert backup interpolation points
# But we need to generate new IDs first
max_id = dev.execute("SELECT COALESCE(MAX(id), 0) FROM route_point").fetchone()[0]
next_id = max_id + 1

inserted = 0
for row in backup_interp:
    army, order_index, lat, lng, is_node, node_id = row
    dev.execute(
        "INSERT INTO route_point (id, army, order_index, lat, lng, is_node, node_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (next_id, army, order_index, lat, lng, is_node, node_id)
    )
    next_id += 1
    inserted += 1

dev.commit()

# Verify
print(f"\nDeleted {removed} liner interp points, inserted {inserted} original historical interp points")
final_interp = dev.execute("SELECT COUNT(*) FROM route_point WHERE is_node = 0").fetchone()[0]
final_nodes = dev.execute("SELECT COUNT(*) FROM route_point WHERE is_node = 1").fetchone()[0]
print(f"Final state: {final_nodes} node points + {final_interp} interp points = {final_nodes + final_interp} total")

# Show a sample
sample = dev.execute(
    "SELECT id, army, order_index, lat, lng, is_node FROM route_point WHERE army = 1 AND is_node = 0 ORDER BY order_index LIMIT 5"
).fetchall()
print(f"\nArmy 1 interp sample: {[(p[0], p[2], round(p[3],4), round(p[4],4)) for p in sample]}")

backup.close()
dev.close()
