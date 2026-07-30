import sqlite3

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"
dev = sqlite3.connect(dev_db)

# Check what we have
total = dev.execute("SELECT COUNT(*) FROM route_point").fetchone()[0]
nodes_before = dev.execute("SELECT COUNT(*) FROM route_point WHERE is_node = 1").fetchone()[0]
interp_before = dev.execute("SELECT COUNT(*) FROM route_point WHERE is_node = 0").fetchone()[0]
print(f"Before: {total} total, {nodes_before} nodes, {interp_before} interp")

# Delete interpolation points
dev.execute("DELETE FROM route_point WHERE is_node = 0")
removed = interp_before

# Verify node positions are correct (matching node table)
dev.execute("""
    UPDATE route_point 
    SET lat = (SELECT lat FROM node WHERE node.node_id = route_point.node_id),
        lng = (SELECT lng FROM node WHERE node.node_id = route_point.node_id)
    WHERE is_node = 1 AND node_id IN (SELECT node_id FROM node)
""")

dev.commit()

# Final state
nodes_after = dev.execute("SELECT COUNT(*) FROM route_point WHERE is_node = 1").fetchone()[0]
total_after = dev.execute("SELECT COUNT(*) FROM route_point").fetchone()[0]
print(f"After: {total_after} total, {nodes_after} nodes (removed {removed} interp points)")

# Show all node points
print("\nRoute node points:")
pts = dev.execute("SELECT r.army, r.order_index, r.lat, r.lng, r.node_id, n.title FROM route_point r LEFT JOIN node n ON n.node_id = r.node_id WHERE r.is_node = 1 ORDER BY r.army, r.order_index").fetchall()
for p in pts:
    print(f"  Army {p[0]} [{p[1]}] ({p[2]:.4f}, {p[3]:.4f}) {p[4] or '-':<8} {p[5] or '-':<30}")

dev.close()
