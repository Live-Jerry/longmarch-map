import json, sqlite3, sys

# 精确映射：路线点名称 -> 节点编号
# 不使用任何文字搜索，不模糊匹配，全部手动指定

ARMY1_NODE_MAP = {
    "长汀": "1.2",
    "瑞金": "1.1",
    "于都": "1.3",
    "道县": "2.1",
    "通道": "3.1",
    "黎平": "4.1",
    "瓮安": "4.2",
    "遵义": "4.3",
    "赤水": "5.1",
    "扎西": "4.4",
    "皎平渡": "6.1",
    "安顺场": "7.1",
    "泸定": "7.2",
    "宝兴": "8.1",
    "达维": "9.1",
    "懋功": "9.1",
    "两河口": "9.2",
    "毛儿盖": "10.1",
    "若尔盖": "10.3",
    "俄界": "11.1",
    "腊子口": "11.2",
    "哈达铺": "11.3",
    "岷县": "E6.2",
    "通渭": "11.4",
    "六盘山": "12.1",
    "吴起镇": "13.1",
}

ARMY2_NODE_MAP = {
    "桑植": "E1.1",
    "毕节": "E3.1",
    "盘县": "E4.1",
    "中甸": "E5.1",
    "甘孜": "E5.2",
    "阿坝": "E6.1",
    "岷县": "E6.2",
    "会宁": "E7.1",
    "将台堡": "E7.2",
}

ARMY4_NODE_MAP = {
    "茂县": "S2.1",
    "懋功": "S3.1",
    "两河口": "S4.1",
    "阿坝": "S6.1",
    "炉霍": "S7.1",
    "甘孜": "S7.2",
    "岷县": "S8.1",
    "会宁": "S8.2",
}

ARMY25_NODE_MAP = {
    "何家冲": "H1.1",
    "独树镇": "H2.1",
    "葛牌": "H4.1",
    "沣峪口": "H5.1",
    "泾川": "H6.1",
    "延川永坪镇": "H6.2",
}

ARMY_MAP = {
    "hongyifang": (1, ARMY1_NODE_MAP),
    "hongershi":   (2, ARMY2_NODE_MAP),
    "hongsifang":  (4, ARMY4_NODE_MAP),
    "hongershiwu": (25, ARMY25_NODE_MAP),
}

with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)

db_path = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"
dev = sqlite3.connect(db_path)
dev.execute("DELETE FROM route_point")
dev.execute("DELETE FROM sqlite_sequence WHERE name='route_point'")

total = 0
node_count = 0
used = set()

for key, (army_id, node_map) in ARMY_MAP.items():
    waypoints = data["routes"].get(key, {}).get("waypoints", [])
    for seq_idx, wp in enumerate(waypoints):
        seq = seq_idx + 1
        name = wp["name"]
        lng, lat = wp["lng"], wp["lat"]

        node_id = node_map.get(name, None)
        if node_id is not None:
            key_tuple = (army_id, node_id)
            if key_tuple in used:
                node_id = None
            else:
                used.add(key_tuple)

        dev.execute(
            "INSERT INTO route_point (army, order_index, lat, lng, is_node, node_id, name) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (army_id, seq, lat, lng, 1 if node_id else 0, node_id, name)
        )
        total += 1
        if node_id:
            node_count += 1

dev.commit()
print("Imported %d waypoints, %d node markers" % (total, node_count))

for army_id in [1, 2, 4, 25]:
    cnt = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ?", (army_id,)).fetchone()[0]
    nd = dev.execute("SELECT COUNT(*) FROM route_point WHERE army = ? AND is_node = 1", (army_id,)).fetchone()[0]
    markers = dev.execute("SELECT node_id, name, order_index FROM route_point WHERE army = ? AND is_node = 1 ORDER BY order_index", (army_id,)).fetchall()
    print("  Army %d: %d pts, %d nodes - %s" % (army_id, cnt, nd, ", ".join(["%s[%s]" % (m[1], m[0]) for m in markers])))

# Verify
dups = dev.execute("SELECT army, node_id, COUNT(*) FROM route_point WHERE is_node=1 AND node_id IS NOT NULL GROUP BY army, node_id HAVING COUNT(*) > 1").fetchall()
if dups:
    print("\nERROR - duplicates:", dups)
else:
    print("\nNo duplicate node_ids, no fuzzy matching used")

dev.close()
