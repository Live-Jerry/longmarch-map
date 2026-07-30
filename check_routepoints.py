import sqlite3

# Old DB (before fix)
old = sqlite3.connect("/root/longmarch/longmarch_app/data/longmarch.db")
cur = old.execute("SELECT COUNT(*) FROM route_point")
print("OLD DB route_point count:", cur.fetchone()[0])
cur = old.execute("SELECT node_id, COUNT(*) FROM route_point GROUP BY node_id ORDER BY node_id LIMIT 10")
for r in cur.fetchall():
    print(f"  node {r[0]}: {r[1]} pts")
# Show first 3 points of each node
cur = old.execute("SELECT node_id, lat, lng, seq FROM route_point WHERE seq <= 3 ORDER BY node_id, seq LIMIT 30")
for r in cur.fetchall():
    print(f"  node {r[0]} seq {r[3]}: ({r[1]}, {r[2]})")
old.close()

print()

# New DB (after fix)
new = sqlite3.connect("/opt/longmarch-map/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db")
cur = new.execute("SELECT COUNT(*) FROM route_point")
print("NEW DB route_point count:", cur.fetchone()[0])
cur = new.execute("SELECT node_id, COUNT(*) FROM route_point GROUP BY node_id ORDER BY node_id LIMIT 10")
for r in cur.fetchall():
    print(f"  node {r[0]}: {r[1]} pts")
cur = new.execute("SELECT node_id, lat, lng, seq FROM route_point WHERE seq <= 3 ORDER BY node_id, seq LIMIT 30")
for r in cur.fetchall():
    print(f"  node {r[0]} seq {r[3]}: ({r[1]}, {r[2]})")
new.close()
