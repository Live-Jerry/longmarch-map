import sqlite3
dev = sqlite3.connect("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db")

# Compare route_point node coords vs node table coords
cur = dev.execute("SELECT n.node_id, n.title, n.lat, n.lng, r.lat, r.lng FROM node n JOIN route_point r ON r.node_id = n.node_id WHERE r.is_node = 1 ORDER BY n.id")
rows = cur.fetchall()
m = 0
for r in rows:
    nid, title, nlat, nlng, rplat, rplng = r
    if abs(rplat - nlat) > 0.0001 or abs(rplng - nlng) > 0.0001:
        m += 1
        print(f"MISMATCH {nid} {title}: node=({nlat},{nlng}) rp=({rplat},{rplng})")
print(f"\nMismatches: {m}/{len(rows)}")
dev.close()
