import sqlite3

old = sqlite3.connect("/root/longmarch/longmarch_app/data/longmarch.db")
new = sqlite3.connect("/opt/longmarch-map/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db")

# Check node coordinates: old route_point vs node table
# For nodes with node_id in old route_point
old_cur = old.execute("SELECT node_id, lat, lng, order_index FROM route_point WHERE node_id IS NOT NULL ORDER BY order_index")
old_nodes = old_cur.fetchall()
new_cur = new.execute("SELECT id, lat, lng FROM node ORDER BY id")
new_nodes = {r[0]: (r[1], r[2]) for r in new_cur.fetchall()}

print("=== Node coordinate differences ===")
for n in old_nodes:
    nid = n[0]
    if nid in new_nodes:
        olat, olng = n[1], n[2]
        nlat, nlng = new_nodes[nid]
        dlng = nlng - olng
        dlat = nlat - olat
        if abs(dlat) > 0.001 or abs(dlng) > 0.001:
            print(f"  node {nid}: old=({olat:.4f},{olng:.4f}) new=({nlat:.4f},{nlng:.4f}) delta=({dlat:.4f},{dlng:.4f})")

# Check for node gaps: for each node pair, what interpolation points exist between them?
old_cur = old.execute("SELECT id, node_id, lat, lng, order_index FROM route_point WHERE army=1 ORDER BY order_index")
all_pts = old_cur.fetchall()

print(f"\n=== Army 1 route points total: {len(all_pts)} ===")
# Find interpolation points between consecutive nodes
prev_node_idx = -1
for i, pt in enumerate(all_pts):
    if pt[1] is not None:  # is a node
        if prev_node_idx >= 0 and prev_node_idx < i - 1:
            # There are interpolation points between prev_node and this node
            prev_pt = all_pts[prev_node_idx]
            interp = all_pts[prev_node_idx+1:i]
            print(f"  Between {prev_pt[1]} -> {pt[1]}: {len(interp)} interp points (order {prev_pt[4]}-{pt[4]})")
        prev_node_idx = i

old.close()
new.close()
