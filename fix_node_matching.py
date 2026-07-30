# Fix route_point node_id matching and coordinate alignment
import sqlite3

DB = "/opt/longmarch-dev/001 项目源码/data/longmarch.db"

# Explicit army-specific name->node_id mappings
NAME_NODE_MAP = {
    1: {"瑞金": "1.1", "长汀": "1.2", "于都": "1.3", "道县": "2.1",
        "通道": "3.1", "黎平": "4.1", "瓮安": "4.2", "遵义": "4.3",
        "扎西": "4.4", "威信": "4.4", "水田寨": "4.5",
        "赤水": "5.1", "皎平渡": "6.1", "安顺场": "7.1", "石棉": "7.1",
        "泸定": "7.2", "宝兴": "8.1", "达维": "9.1", "懋功": "9.1",
        "两河口": "9.2", "马尔康": "9.3", "毛儿盖": "10.1",
        "松潘": "10.2", "若尔盖": "10.3", "班佑": "10.3", "巴西": "10.3",
        "俄界": "11.1", "腊子口": "11.2", "哈达铺": "11.3",
        "岷县": "E6.2", "通渭": "11.4", "六盘山": "12.1", "环县": "13.1",
        "吴起镇": "13.1", "马道口": None, "云石山": None},
    2: {"桑植": "E1.1", "永顺": None, "大庸": None, "芷江": None,
        "玉屏": None, "镇远": None, "黄平": None, "瓮安": None,
        "毕节": "E3.1", "赫章": None, "奎香": None, "镇雄": None,
        "宣威": None, "盘县": "E4.1", "昆明": None, "丽江": None,
        "中甸": "E5.1", "甘孜": "E5.2", "绒坝岔": None, "阿坝": "E6.1",
        "包座": None, "岷县": "E6.2", "渭源": None, "会宁": "E7.1",
        "将台堡": "E7.2"},
    4: {"通江": None, "巴中": None, "旺苍": None, "南江": None,
        "广元": None, "剑门关": None, "江油": None, "茂县": "S2.1",
        "理县": None, "懋功": "S3.1", "两河口": "S4.1", "马尔康": "S5.1",
        "刷经寺": None, "阿坝": "S6.1", "甘孜": "S7.2", "炉霍": "S7.1",
        "绒坝岔": None, "若尔盖": "S6.1", "巴西": "S8.1", "岷县": "S8.1",
        "会宁": "S8.2"},
    25: {"何家冲": "H1.1", "信阳": None, "桐柏": None, "独树镇": "H2.1",
         "卢氏": None, "洛南": None, "蔡川": None, "商洛": None,
         "镇安": None, "葛牌": "H4.1", "蓝田": "H4.1", "沣峪口": "H5.1",
         "秦渡镇": None, "凤县": None, "两当": None, "天水": None,
         "秦安": None, "通渭": None, "隆德": None, "泾川": "H6.1",
         "永和": None, "延川永坪镇": "H6.2"}
}

conn = sqlite3.connect(DB)
c = conn.cursor()

# 1. Get node coordinates
c.execute("SELECT node_id, lat, lng FROM node")
node_coords = {r[0]: (r[1], r[2]) for r in c.fetchall()}

print("=== Fixing route_point node_id and coordinates ===")

for army in [1, 2, 4, 25]:
    name_map = NAME_NODE_MAP[army]
    
    c.execute("SELECT id, name FROM route_point WHERE army=?", (army,))
    rows = c.fetchall()
    
    fixed_nid = 0
    fixed_coord = 0
    
    for rp_id, name in rows:
        # Determine correct node_id
        correct_nid = None
        for nm, nid in name_map.items():
            if name and nm in name:
                correct_nid = nid
                break
        
        # Special case: 懋功 in army 1 (JSON maps it to 达维, keep S3.1)
        if army == 1 and name == "懋功":
            correct_nid = "S3.1"
        
        if correct_nid:
            # Update node_id
            c.execute("UPDATE route_point SET node_id=? WHERE id=?", (correct_nid, rp_id))
            fixed_nid += 1
            
            # Fix coordinates to match node table
            if correct_nid and correct_nid in node_coords:
                nlat, nlng = node_coords[correct_nid]
                c.execute("UPDATE route_point SET lat=?, lng=? WHERE id=?", (nlat, nlng, rp_id))
                fixed_coord += 1
                node_label = f"{correct_nid} ({nlat:.4f},{nlng:.4f})"
                # print(f"  army={army} {name:12} -> {node_label}")
        else:
            # Clear incorrect node_id
            c.execute("UPDATE route_point SET node_id=NULL WHERE id=?", (rp_id,))
    
    print(f"  Army {army}: {fixed_nid} node_id matches, {fixed_coord} coords fixed")

conn.commit()
conn.close()
print("Done!")
