import sqlite3

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"
backup_db = "/root/longmarch/longmarch_app/data/longmarch.db"

dev = sqlite3.connect(dev_db)
backup = sqlite3.connect(backup_db)

for army in [2, 4, 25]:
    backup_count = backup.execute("SELECT COUNT(*) FROM route_point WHERE army = ? AND is_node = 0", (army,)).fetchone()[0]
    dev_count = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ?", (army,)).fetchone()[0]
    print(f"Army {army}: backup has {backup_count} interp points, dev has {dev_count} total")
    if dev_count == 0 and backup_count > 0:
        rows = backup.execute(
            "SELECT army, order_index, lat, lng, is_node, node_id FROM route_point WHERE army = ? AND is_node = 0 ORDER BY order_index",
            (army,)
        ).fetchall()
        max_id = dev.execute("SELECT COALESCE(MAX(id), 0) FROM route_point").fetchone()[0]
        next_id = max_id + 1
        for row in rows:
            dev.execute(
                "INSERT INTO route_point (id, army, order_index, lat, lng, is_node, node_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (next_id,) + row
            )
            next_id += 1
        dev.commit()
        print(f"  Restored {len(rows)} points for Army {army}")

# Verify final state
for army in [1, 2, 4, 25]:
    cnt = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ?", (army,)).fetchone()[0]
    print(f"Army {army} final: {cnt} points")

dev.close()
backup.close()
