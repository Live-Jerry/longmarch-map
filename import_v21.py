import sqlite3, json

DB = "/opt/longmarch-dev/001 项目源码/data/longmarch.db"
JSON_PATH = "/root/长征路线完整坐标数据2.1.json"

# Per-army exact name -> node_id mapping (no fuzzy, no partial match)
NAME_NODE = {
    1: {"瑞金": "1.1", "长汀": "1.2", "于都": "1.3", "道县": "2.1",
        "通道": "3.1", "黎平": "4.1", "瓮安": "4.2", "遵义": "4.3",
        "扎西": "4.4", "威信": "4.4", "水田寨": "4.5",
        "赤水": "5.1", "皎平渡": "6.1", "安顺场": "7.1",
        "泸定": "7.2", "宝兴": "8.1", "达维": "9.1", "懋功": "9.1",
        "两河口": "9.2", "毛儿盖": "10.1",
        "松潘": "10.2", "若尔盖": "10.3", "巴西": "10.3",
        "俄界": "11.1", "腊子口": "11.2", "哈达铺": "11.3",
        "岷县": "E6.2", "通渭": "11.4", "六盘山": "12.1",
        "吴起镇": "13.1"},
    2: {"桑植": "E1.1", "毕节": "E3.1", "盘县": "E4.1",
        "中甸": "E5.1", "甘孜": "E5.2", "阿坝": "E6.1",
        "岷县": "E6.2", "会宁": "E7.1", "将台堡": "E7.2"},
    4: {"苍溪": "S1.1", "茂县": "S2.1", "懋功": "S3.1",
        "两河口": "S4.1", "马尔康": "S5.1", "阿坝": "S6.1",
        "炉霍": "S7.1", "甘孜": "S7.2", "岷县": "S8.1",
        "会宁": "S8.2"},
    25: {"何家冲": "H1.1", "独树镇": "H2.1", "葛牌": "H4.1",
         "沣峪口": "H5.1", "泾川": "H6.1", "延川永坪镇": "H6.2"}
}

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT node_id, lat, lng FROM node")
node_coords = {r[0]: (r[1], r[2]) for r in c.fetchall()}

ARMY_MAP = {"hongyifang": 1, "hongershi": 2, "hongsifang": 4, "hongershiwu": 25}

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

c.execute("DELETE FROM route_point")
conn.commit()

total = 0
for army_key, route in data["routes"].items():
    army = ARMY_MAP[army_key]
    name_map = NAME_NODE.get(army, {})
    for i, wp in enumerate(route["waypoints"]):
        name = wp["name"]
        nid = name_map.get(name, None)
        if nid and nid in node_coords:
            lat, lng = node_coords[nid]
        else:
            lat, lng = wp["lat"], wp["lng"]
        is_node = 1 if nid else 0
        c.execute(
            "INSERT INTO route_point (army, lat, lng, order_index, is_node, node_id, name) VALUES (?,?,?,?,?,?,?)",
            (army, lat, lng, i, is_node, nid, name)
        )
        total += 1

conn.commit()
conn.close()
print(f"Re-imported {total} route points from V2.1")
print("Army 4 now includes 苍溪 (S1.1)")
