import sqlite3

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"
dev = sqlite3.connect(dev_db)

# Explicit correct coordinates for nodes that were wrongly matched
# Source: JSON waypoints (correct match) or Photon API result
fixes = {
    # 4.5: was matched to "遵义" waypoint by mistake
    "4.5": (27.4700, 106.9100),  # 苟坝 - actually JSON matches this to 遵义... 
    # Hmm, let me reconsider. The JSON waypoint for 四渡赤水 says "遵义" at (27.47, 106.91)
    # But 4.5 (苟坝) is NOT the same as 遵义
}

# Actually, let me check what the route_point has for these waypoints
# The JSON waypoints include "扎西" at (105.048, 27.841) and "扎西" at (105.05, 27.85)
# Node 4.4 "云南威信（扎西镇）" should match "扎西" waypoint

# Let me look at what the JSON waypoint coordinates are for each name
print("=== Current node coords ===")
nodes = dev.execute("SELECT node_id, title, lat, lng FROM node ORDER BY id").fetchall()
for n in nodes:
    print(f"  {n[0]:<8} {n[1]:<35} ({n[2]:.4f}, {n[3]:.4f})")

# The key issue: some nodes were matched to wrong waypoints
# Let me fix the ones that I KNOW are wrong by explicit mapping

print("\n=== Fixing wrongly matched nodes ===")

# 7.1 should be "安顺场" (29.25, 102.22) not "安顺" (26.25, 105.93)
# The JSON waypoint id=46 is "安顺场" at (29.25, 102.22)
# But "安顺" at (26.25, 105.93) matched first
correct_7_1 = dev.execute("SELECT lat, lng FROM route_point WHERE army = 1 AND order_index = 46").fetchone()
if correct_7_1:
    print(f"  7.1 安顺场 route_point: ({correct_7_1[0]:.4f}, {correct_7_1[1]:.4f})")
    dev.execute("UPDATE node SET lat = ?, lng = ? WHERE node_id = '7.1'", correct_7_1)

# 4.5 苟坝 was matched to "遵义" (27.47, 106.91) but should keep the specific 苟坝 coords
# The JSON doesn't have a separate "苟坝" waypoint - it's part of the 遵义-赤水 segment
# The Photon API result was most accurate here
# Let's check what 4.3 遵义 was set to
n43 = dev.execute("SELECT lat, lng FROM node WHERE node_id = '4.3'").fetchone()
n45 = dev.execute("SELECT lat, lng FROM node WHERE node_id = '4.5'").fetchone()
print(f"  4.3 遵义 = ({n43[0]:.4f}, {n43[1]:.4f})")
print(f"  4.5 苟坝 = ({n45[0]:.4f}, {n45[1]:.4f})")
# 4.3 was set to (27.47, 106.91) which matches "四渡赤水南渡乌江" waypoint in JSON
# The correct 遵义 coordinates should be from JSON waypoint id=27 "遵义" at (27.536, 106.829)
correct_4_3 = dev.execute("SELECT lat, lng FROM route_point WHERE army = 1 AND order_index = 27").fetchone()
if correct_4_3:
    print(f"  4.3 遵义 should be: ({correct_4_3[0]:.4f}, {correct_4_3[1]:.4f})")
    dev.execute("UPDATE node SET lat = ?, lng = ? WHERE node_id = '4.3'", correct_4_3)

# 4.5 苟坝 - use the JSON waypoint for the specific area
# Since there's no 苟坝 waypoint, keep the route point from the relevant segment
# Let's interpolate or use the nearest waypoint
# Actually, 苟坝会议会址 is at (27.652, 106.565) from Photon API
# Or we can use waypoint id=27 (遵义) since 苟坝 is near 遵义
dev.execute("UPDATE node SET lat = 27.6524, lng = 106.5649 WHERE node_id = '4.5'")
print(f"  4.5 苟坝 set to (27.6524, 106.5649)")

# 8.1 夹金山 - was matched to "宝兴" (30.368, 102.815)
# But 夹金山 is a specific mountain near 宝兴
# The JSON waypoint id=50 "宝兴" is at (30.368, 102.815)
# Let me check what makes most sense
correct_8_1 = dev.execute("SELECT lat, lng FROM route_point WHERE army = 1 AND order_index = 41").fetchone()
# Actually, 夹金山 should be between 宝兴 and 达维
# Waypoint 50 = 宝兴 (30.368, 102.815), waypoint 51 = 达维 (30.82, 102.56)
# 夹金山 is at about (30.7, 102.5) roughly midpoint
dev.execute("UPDATE node SET lat = 30.8200, lng = 102.5600 WHERE node_id = '8.1'")
print(f"  8.1 夹金山 set to (30.8200, 102.5600)")

# 5.1 赤水河 - was matched to "赤水" waypoint
correct_5_1 = dev.execute("SELECT lat, lng FROM route_point WHERE army = 1 AND order_index = 31").fetchone()
if correct_5_1:
    print(f"  5.1 赤水河 route_point: ({correct_5_1[0]:.4f}, {correct_5_1[1]:.4f})")
    # This is correct - "赤水" waypoint

# 10.2 松潘草地 - was matched to "松潘" waypoint
correct_10_2 = dev.execute("SELECT lat, lng FROM route_point WHERE army = 1 AND order_index = 56").fetchone()
if correct_10_2:
    print(f"  10.2 松潘草地 route_point: ({correct_10_2[0]:.4f}, {correct_10_2[1]:.4f})")

# 12.1 六盘山 was matched to "六盘山" waypoint (correct)
correct_12_1 = dev.execute("SELECT lat, lng FROM route_point WHERE army = 1 AND order_index = 67").fetchone()
if correct_12_1:
    print(f"  12.1 六盘山 route_point: ({correct_12_1[0]:.4f}, {correct_12_1[1]:.4f})")

# 13.1 吴起镇 was matched to "吴起镇" waypoint (correct)
correct_13_1 = dev.execute("SELECT lat, lng FROM route_point WHERE army = 1 AND order_index = 69").fetchone()
if correct_13_1:
    print(f"  13.1 吴起镇 route_point: ({correct_13_1[0]:.4f}, {correct_13_1[1]:.4f})")

# 9.1 懋功 - was matched to "达维" (30.82, 102.56) or "懋功" (31.18, 102.65)?
# Node 9.1 title is "四川小金（懋功/达维）" 
# JSON "达维" = (30.82, 102.56), "懋功" = (31.18, 102.65)
# 小金县 is at about (30.998, 102.361)
# Let's use the JSON 懋功 waypoint
correct_9_1 = dev.execute("SELECT lat, lng FROM route_point WHERE army = 1 AND order_index = 52").fetchone()
if correct_9_1:
    print(f"  9.1 懋功 route_point: ({correct_9_1[0]:.4f}, {correct_9_1[1]:.4f})")

# 9.2 两河口 - was matched to "两河口" waypoint
correct_9_2 = dev.execute("SELECT lat, lng FROM route_point WHERE army = 1 AND order_index = 53").fetchone()
if correct_9_2:
    print(f"  9.2 两河口 route_point: ({correct_9_2[0]:.4f}, {correct_9_2[1]:.4f})")

dev.commit()

# Verify final state
print("\n=== Final node coords ===")
nodes = dev.execute("SELECT node_id, title, lat, lng FROM node ORDER BY id").fetchall()
for n in nodes:
    print(f"  {n[0]:<8} {n[1]:<35} ({n[2]:.4f}, {n[3]:.4f})")

dev.close()
