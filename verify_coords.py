import sqlite3, json

# Compare node table vs node_data.json
dev = sqlite3.connect("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db")
cur = dev.execute("SELECT node_id, title, lat, lng FROM node ORDER BY id")
db_nodes = {r[0]: r for r in cur.fetchall()}
dev.close()

with open("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/node_data.json") as f:
    json_nodes = json.load(f)

print(f"DB nodes: {len(db_nodes)}, JSON nodes: {len(json_nodes)}")

# Compare
mismatches = []
for jn in json_nodes:
    nid = jn.get("node_id")
    if nid in db_nodes:
        dbn = db_nodes[nid]
        jlat = float(jn["lat"])
        jlng = float(jn["lng"])
        dlat = float(dbn[2])
        dlng = float(dbn[3])
        if abs(jlat - dlat) > 0.0001 or abs(jlng - dlng) > 0.0001:
            mismatches.append((nid, dbn[1], jlat, jlng, dlat, dlng))

print(f"\nDB vs JSON mismatches: {len(mismatches)}")
for m in mismatches:
    print(f"  {m[0]} {m[1]}: json=({m[2]},{m[3]}) db=({m[4]},{m[5]})")

if not mismatches:
    print("  All match!")
