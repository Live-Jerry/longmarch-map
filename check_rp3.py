import sqlite3

old = sqlite3.connect("/root/longmarch/longmarch_app/data/longmarch.db")
new = sqlite3.connect("/opt/longmarch-map/001 项目源码/data/longmarch.db")

# Get all route_points ordered by order_index for comparison
old_cur = old.execute("SELECT id, army, stage, lat, lng, order_index, is_node, node_id FROM route_point ORDER BY id")
old_rows = old_cur.fetchall()

new_cur = new.execute("SELECT id, army, stage, lat, lng, order_index, is_node, node_id FROM route_point ORDER BY id")
new_rows = new_cur.fetchall()

print(f"OLD: {len(old_rows)} points, NEW: {len(new_rows)} points")

# Count differences
diff_count = 0
for i in range(min(len(old_rows), len(new_rows))):
    o = old_rows[i]
    n = new_rows[i]
    if abs(o[3] - n[3]) > 0.0001 or abs(o[4] - n[4]) > 0.0001:
        diff_count += 1
        if diff_count <= 20:
            print(f"DIFF id={o[0]}/{n[0]} node_id={o[7]} order={o[5]}: old=({o[3]:.5f},{o[4]:.5f}) new=({n[3]:.5f},{n[4]:.5f}) delta=({n[3]-o[3]:.5f},{n[4]-o[4]:.5f})")

print(f"Total differences: {diff_count} out of {len(old_rows)}")

old.close()
new.close()
