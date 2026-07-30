import sqlite3, math

dev = sqlite3.connect("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db")

# Get correct node coordinates from node table
cur = dev.execute("SELECT node_id, lat, lng FROM node")
node_coords = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
print(f"Loaded {len(node_coords)} nodes from node table")

# Count how many route_point nodes will be updated
cur = dev.execute("SELECT r.id, r.node_id, r.lat, r.lng FROM route_point r WHERE r.is_node = 1")
rows = cur.fetchall()
updated = 0
for r in rows:
    rpid, nid, oldlat, oldlng = r
    if nid in node_coords:
        nlat, nlng = node_coords[nid]
        if abs(oldlat - nlat) > 0.0001 or abs(oldlng - nlng) > 0.0001:
            dev.execute("UPDATE route_point SET lat = ?, lng = ? WHERE id = ?", (nlat, nlng, rpid))
            updated += 1
            print(f"  node {nid}: ({oldlat:.4f},{oldlng:.4f}) -> ({nlat:.4f},{nlng:.4f})")

dev.commit()
print(f"\nUpdated {updated} route_point node coordinates")

# Verify
cur = dev.execute("SELECT n.node_id, n.lat, n.lng, r.lat, r.lng FROM node n JOIN route_point r ON r.node_id = n.node_id AND r.is_node = 1 ORDER BY n.id")
rows = cur.fetchall()
m = 0
for r in rows:
    if abs(r[1]-r[3]) > 0.0001 or abs(r[2]-r[4]) > 0.0001:
        m += 1
        print(f"  STILL MISMATCH: {r[0]}: node=({r[1]},{r[2]}) rp=({r[3]},{r[4]})")
print(f"Remaining mismatches: {m}/{len(rows)}")

dev.close()
