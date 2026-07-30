import sqlite3

# Check node coordinates in dev DB vs node table
dev = sqlite3.connect("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db")

# Compare route_point node coords vs node table coords
cur = dev.execute("SELECT n.id, n.title, r.lat, r.lng, n.lat, n.lng FROM node n JOIN route_point r ON r.node_id = n.id WHERE r.is_node = 1 ORDER BY n.id")
rows = cur.fetchall()
print(f"Node count: {len(rows)}")
mismatch = 0
for r in rows:
    nid, name, rplat, rplng, nlat, nlng = r
    # Be more precise - check if different
    if abs(rplat - nlat) > 0.00001 or abs(rplng - nlng) > 0.00001:
        mismatch += 1
        print(f"  MISMATCH node {nid} ({name}): route_point=({rplat:.5f},{rplng:.5f}) node_table=({nlat:.5f},{nlng:.5f})")
    else:
        print(f"  OK node {nid} ({name}): ({rplat:.5f},{rplng:.5f})")

print(f"\nTotal mismatches: {mismatch}/{len(rows)}")
dev.close()
