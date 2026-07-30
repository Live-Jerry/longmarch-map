import sqlite3

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

# Verified correct coordinates (from API + user provided)
# Only nodes that need correction are listed
corrections = {
    # Core nodes (中央红军)
    "1.2": (25.669, 116.329),     # 福建长汀 -> 长汀县
    "2.1": (25.468, 111.601),     # 湖南道县->全州（湘江两岸）-> 道县
    "4.5": (27.652, 106.565),     # 贵州遵义（苟坝村）-> 苟坝会议会址
    "5.1": (28.488, 105.910),     # 赤水河一带 -> 赤水市
    "6.1": (26.127, 102.449),     # 云南寻甸、禄劝（皎平渡）-> 皎平渡镇
    "7.2": (29.763, 102.142),     # 四川泸定 -> 泸定县
    "8.1": (30.588, 102.169),     # 四川宝兴（夹金山）
    "9.2": (31.490, 102.489),     # 四川小金（两河口镇）
    "10.1": (32.601, 103.063),    # 四川松潘（毛儿盖、沙窝）-> 毛儿盖镇
    "10.2": (32.8333, 103.5000),  # 四川阿坝（松潘草地）- 用户提供
    "10.3": (33.576, 102.964),    # 四川若尔盖（巴西镇）-> 若尔盖县
    "11.1": (34.1333, 102.8000),  # 甘肃迭部（俄界/高吉村）- 用户提供
    "11.2": (34.132, 103.929),    # 甘肃迭部（腊子口）-> 腊子口镇
    "11.3": (34.231, 104.223),    # 甘肃宕昌（哈达铺）-> 哈达铺镇
    "11.4": (35.036, 104.938),    # 甘肃通渭（榜罗镇）
    "13.1": (36.983, 108.159),    # 陕西吴起镇 -> 吴起县
    
    # 红二方面军
    "E3.1": (27.088, 106.105),    # 贵州黔西（大定/毕节）-> 黔西市
    "E4.1": (25.868, 104.603),    # 云南盘县 -> 盘州市
    
    # 红四方面军
    "S1.1": (31.935, 106.163),    # 四川苍溪（强渡嘉陵江）-> 苍溪县
    "S6.2": (31.537, 101.810),    # 四川金川（绥靖）
    
    # 红25军
    "H1.1": (31.7833, 114.2000),  # 河南罗山（何家冲）- 用户提供
    "H2.1": (33.2000, 112.3000),  # 河南方城（独树镇）- 用户提供
    "H4.1": (33.912, 109.502),    # 陕西蓝田（葛牌镇）
    "H5.1": (33.9667, 108.8000),  # 陕西长安（沣峪口）- 用户提供
    "H6.2": (37.009, 109.818),    # 陕西永坪镇
}

dev = sqlite3.connect(dev_db)

# Update node table
for nid, (lat, lng) in corrections.items():
    dev.execute("UPDATE node SET lat = ?, lng = ? WHERE node_id = ?", (lat, lng, nid))

dev.commit()

# Count updates and verify
cur = dev.execute("SELECT node_id, title, lat, lng FROM node ORDER BY id")
updated = 0
for r in cur.fetchall():
    nid, title, lat, lng = r
    if nid in corrections:
        expected = corrections[nid]
        if abs(lat - expected[0]) < 0.001 and abs(lng - expected[1]) < 0.001:
            updated += 1
            print(f"OK {nid} {title}: ({lat:.4f}, {lng:.4f})")

print(f"\nUpdated {updated} node coordinates in dev database")
dev.close()
