import json, sqlite3

with open("/opt/longmarch-dev/longmarch_route.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

army_map = {"hongyifang": 1, "hongershi": 2, "hongsifang": 4, "hongershiwu": 25}

dev = sqlite3.connect(dev_db)

# Get all nodes
all_nodes = dev.execute("SELECT node_id, title FROM node WHERE title != 'Test'").fetchall()

def match_node(name):
    """Find best matching node for a waypoint name. Returns None if no good match."""
    name_clean = name.strip()
    
    # Explicit override for problematic matches
    overrides = {
        "安顺": None,  # 贵州安顺, NOT node 7.1 安顺场
        "威信": None,  # 威信 is adjacent to 扎西, both near node 4.4 but we already matched 扎西
        "懋功": None,  # Already matched 达维 for node 9.1
        "巴西": None,  # Already matched 若尔盖 for node 10.3
        "岷县": None,  # Already matched 哈达铺 for node 11.3
        "会宁": None,  # These are end points for other armies, skip duplicate
        "松潘": None,  # Already matched 毛儿盖 for node 10.1
        "将台堡": None, # Skip duplicate
        "贡嘎": None,
        "阿坝": None,  # Multiple armies have 阿坝, let matching handle carefully
        "甘孜": None,  # Multiple uses
    }
    
    if name_clean in overrides:
        return overrides[name_clean]
    
    # Build list of candidate nodes
    candidates = []
    for nid, title in all_nodes:
        # Check if this node_id was already assigned
        existing = dev.execute(
            "SELECT COUNT(*) FROM route_point WHERE node_id = ? AND is_node = 1",
            (nid,)
        ).fetchone()[0]
        if existing > 0:
            continue  # Skip already-assigned node_ids
        
        # Various matching strategies:
        # 1. Exact title match
        if title == name_clean:
            candidates.append((1, nid, title))
            continue
        
        # 2. title starts with province+name (e.g., "江西瑞金")
        # Remove province prefix from title
        provinces = ["江西", "福建", "贵州", "云南", "四川", "湖南", "广西", "甘肃", "陕西", "宁夏", "重庆", "湖北", "河南", "广东"]
        title_short = title
        for p in provinces:
            if title.startswith(p):
                title_short = title[len(p):]
                break
        if title_short == name_clean:
            candidates.append((2, nid, title))
            continue
        
        # 3. title contains name in parentheses (e.g., "贵州瓮安（猴场镇）" matches "猴场镇")
        import re
        paren_match = re.findall(r'[（(][^）)]*[）)]', title_short)
        for pm in paren_match:
            inner = pm[1:-1]
            # Handle multiple items separated by / or 、
            for item in re.split(r'[/、／]', inner):
                if item.strip() == name_clean:
                    candidates.append((3, nid, title))
                    break
        
        # 4. title contains name as a direct part (e.g., "福建长汀" contains "长汀")
        # Use word boundary check
        if name_clean in title_short and name_clean not in overrides:
            # Check it's not a partial word match
            idx = title_short.find(name_clean)
            after_char = title_short[idx + len(name_clean):][:1] if idx + len(name_clean) < len(title_short) else ""
            # "安顺" matches "安顺场" - check for this case
            if after_char and after_char in "（(→" or not after_char:
                candidates.append((4, nid, title))
    
    if candidates:
        # Sort by priority (lower number = better match)
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]
    
    return None

dev.execute("DELETE FROM route_point")
assigned = set()
total = 0

for key, army_id in army_map.items():
    waypoints = data["routes"][key]["waypoints"]
    for seq_idx, wp in enumerate(waypoints):
        seq = seq_idx + 1
        name = wp["name"]
        lng, lat = wp["lng"], wp["lat"]
        
        node_id = match_node(name)
        if node_id:
            assigned.add(node_id)
        
        dev.execute(
            "INSERT INTO route_point (army, order_index, lat, lng, is_node, node_id, name) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (army_id, seq, lat, lng, 1 if node_id else 0, node_id, name)
        )
        total += 1

dev.commit()
print(f"Imported {total} waypoints, {len(assigned)} unique node matches")
for army_id in [1, 2, 4, 25]:
    cnt = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ?", (army_id,)).fetchone()[0]
    nodes = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ? AND is_node = 1", (army_id,)).fetchone()[0]
    print(f"  Army {army_id}: {cnt} pts, {nodes} unique node matches")

# Verify
dups = dev.execute("SELECT node_id, COUNT(*) FROM route_point WHERE is_node = 1 AND node_id IS NOT NULL GROUP BY node_id HAVING COUNT(*) > 1").fetchall()
if dups:
    print(f"\nWARNING: Duplicate node_ids:")
    for d in dups:
        names = dev.execute("SELECT name, army FROM route_point WHERE node_id = ? AND is_node = 1", (d[0],)).fetchall()
        print(f"  {d[0]}: {[n[0] for n in names]}")
else:
    print("\nNo duplicate node_ids (good)")

# Show match details for key entries
print("\nNode match details:")
for name in ["长汀", "瑞金", "安顺", "安顺场", "石棉", "扎西", "威信", "水田寨", "道县", "全州", "达维", "懋功"]:
    rp = dev.execute("SELECT army, is_node, node_id FROM route_point WHERE name = ? LIMIT 1", (name,)).fetchone()
    if rp:
        print(f"  {name:8} is_node={rp[1]} node_id={rp[2]}")
    else:
        print(f"  {name:8} NOT FOUND")

dev.close()
