import sqlite3
db = sqlite3.connect('001 项目源码/data/longmarch.db')
cur = db.cursor()

# Check route_point per army
cur.execute('SELECT army, COUNT(*) FROM route_point GROUP BY army')
for r in cur.fetchall():
    print(f'Army {r[0]}: {r[1]} points')

# Check for nodes (is_node=1)
cur.execute('SELECT COUNT(*) FROM route_point WHERE is_node=1')
print(f'Total node points: {cur.fetchone()[0]}')

# Check non-node points (is_node=0) - these are the in-between points
cur.execute('SELECT COUNT(*) FROM route_point WHERE is_node=0')
print(f'Total route points (between nodes): {cur.fetchone()[0]}')

# Show points with names for army=1
cur.execute('SELECT name, node_id, is_node FROM route_point WHERE army=1 AND name IS NOT NULL AND name != "" ORDER BY order_index')
for r in cur.fetchall():
    marker = '(NODE)' if r[2] == 1 else '(route)'
    print(f'  {marker} {r[0]} {r[1] or ""}')

db.close()
