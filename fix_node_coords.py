import sqlite3

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"
dev = sqlite3.connect(dev_db)

# Set node coordinates from the CORRECT JSON waypoint match
# Route path should follow JSON, node marker should match where the route goes
# Key: for nodes that have multiple waypoint matches, use the intended one

fixes = {
    # 7.1: use "安顺场" waypoint, not "安顺" or "石棉"
    "7.1": (29.25, 102.22),       # 安顺场
    # 10.1: use "毛儿盖" waypoint, not "松潘"  
    "10.1": (32.34, 102.74),      # 毛儿盖
    # 10.3: use "巴西" waypoint (node title says 巴西镇)
    "10.3": (34.07, 103.44),      # 巴西
    # 10.2: use "松潘" waypoint (title says 松潘草地)
    "10.2": (32.63813, 103.59893), # 松潘
    # 9.1: use "达维" waypoint (title says 懋功/达维)
    "9.1": (30.82, 102.56),       # 达维
    # 8.1: use JSON waypoint "宝兴" as closest (夹金山 between 宝兴 and 达维)
    "8.1": (30.36806, 102.81457), # 宝兴
    # 2.1: use "道县" (json waypoint) since title starts with 道县
    "2.1": (25.52753, 111.60007), # 道县
}

for nid, (lat, lng) in fixes.items():
    old = dev.execute("SELECT lat, lng FROM node WHERE node_id = ?", (nid,)).fetchone()
    dev.execute("UPDATE node SET lat = ?, lng = ? WHERE node_id = ?", (lat, lng, nid))
    print(f"{nid}: ({old[0]:.4f},{old[1]:.4f}) -> ({lat:.4f},{lng:.4f})")

# Also sync route_point is_node=1 to match node table
dev.execute("""
    UPDATE route_point 
    SET lat = (SELECT lat FROM node WHERE node.node_id = route_point.node_id),
        lng = (SELECT lng FROM node WHERE node.node_id = route_point.node_id)
    WHERE is_node = 1 AND node_id IN (SELECT node_id FROM node)
""")
dev.commit()

# Verify
print("\n=== Final node coords ===")
nodes = dev.execute("SELECT node_id, title, lat, lng FROM node ORDER BY id").fetchall()
for n in nodes:
    print(f"  {n[0]:<8} {n[1]:<35} ({n[2]:.4f}, {n[3]:.4f})")

dev.close()
