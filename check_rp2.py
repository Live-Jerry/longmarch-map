import sqlite3

# Compare old vs new route_point data
old = sqlite3.connect("/root/longmarch/longmarch_app/data/longmarch.db")
new = sqlite3.connect("/opt/longmarch-map/001 项目源码/data/longmarch.db")

# Old DB structure
cur = old.execute("PRAGMA table_info(route_point)")
print("OLD route_point columns:", [(r[1], r[2]) for r in cur.fetchall()])
cur = old.execute("SELECT COUNT(*) FROM route_point")
print("OLD total:", cur.fetchone()[0])
cur = old.execute("SELECT node_id, COUNT(*) FROM route_point WHERE node_id IS NOT NULL GROUP BY node_id ORDER BY node_id")
rows = cur.fetchall()
print("OLD with node_id:", len(rows))
for r in rows[:10]:
    print(f"  {r[0]}: {r[1]} pts")
cur = old.execute("SELECT COUNT(*) FROM route_point WHERE node_id IS NULL")
print("OLD no node_id:", cur.fetchone()[0])

old.close()

# New DB
cur = new.execute("PRAGMA table_info(route_point)")
print("NEW route_point columns:", [(r[1], r[2]) for r in cur.fetchall()])
cur = new.execute("SELECT COUNT(*) FROM route_point")
print("NEW total:", cur.fetchone()[0])
cur = new.execute("SELECT node_id, COUNT(*) FROM route_point WHERE node_id IS NOT NULL GROUP BY node_id ORDER BY node_id")
rows = cur.fetchall()
print("NEW with node_id:", len(rows))
for r in rows[:15]:
    print(f"  {r[0]}: {r[1]} pts")

new.close()
