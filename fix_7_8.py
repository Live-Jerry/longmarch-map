import sqlite3
dev = sqlite3.connect("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db")
dev.execute("UPDATE node SET lat = 29.274, lng = 102.283 WHERE node_id = '7.1'")
dev.execute("UPDATE node SET lat = 30.588, lng = 102.169 WHERE node_id = '8.1'")
dev.execute("UPDATE route_point SET lat = (SELECT lat FROM node WHERE node.node_id = route_point.node_id), lng = (SELECT lng FROM node WHERE node.node_id = route_point.node_id) WHERE is_node = 1 AND node_id IN (SELECT node_id FROM node)")
dev.commit()
for nid in ["7.1", "8.1"]:
    n = dev.execute("SELECT node_id, lat, lng FROM node WHERE node_id = ?", (nid,)).fetchone()
    r = dev.execute("SELECT lat, lng FROM route_point WHERE node_id = ? AND is_node = 1", (nid,)).fetchone()
    print(f"  {nid}: node({n[1]:.4f},{n[2]:.4f}) rp({r[0]:.4f},{r[1]:.4f})")
dev.close()
