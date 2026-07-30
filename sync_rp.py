import sqlite3
dev = sqlite3.connect("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db")
cur = dev.execute("UPDATE route_point SET lat = (SELECT lat FROM node WHERE node.node_id = route_point.node_id), lng = (SELECT lng FROM node WHERE node.node_id = route_point.node_id) WHERE route_point.is_node = 1 AND route_point.node_id IN (SELECT node_id FROM node)")
print(f"Updated {cur.rowcount} route_point nodes")
dev.commit()
# Verify
cur = dev.execute("SELECT COUNT(*) FROM (SELECT n.node_id, n.lat as nl, n.lng as nlg, r.lat as rl, r.lng as rlg FROM node n JOIN route_point r ON r.node_id = n.node_id AND r.is_node = 1) WHERE abs(nl - rl) > 0.0001 OR abs(nlg - rlg) > 0.0001")
print(f"Remaining mismatches: {cur.fetchone()[0]}")
dev.close()
