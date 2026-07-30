import urllib.request, urllib.parse, json, time, sqlite3

dev = sqlite3.connect("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db")
cur = dev.execute("SELECT node_id, title, lat, lng FROM node ORDER BY id")
db_nodes = cur.fetchall()
dev.close()

print(f"Total nodes in DB: {len(db_nodes)}")
print()

# Query each node via Photon API
queries = [
    # For each node, use its title as the search query
]

def smart_query(title, nid):
    # Simplify the title for geocoding
    t = title.replace("（", "(").replace("）", ")").replace("→", " ")
    # Remove parenthetical when it contains extra info
    t = t.split("(")[0].strip()
    # Remove known suffixes
    for suffix in ["一带", "一带（皎平渡）", "（安顺场）", "（夹金山）", "（扎西镇）", "（猴场镇）", "（苟坝村）", "（芦花镇）", "（巴西镇）", "（毛儿盖、沙窝）", "（俄界/高吉村）", "（腊子口）", "（哈达铺）", "（榜罗镇）"]:
        t = t.replace(suffix, "")
    t = t.strip()
    # Handle special cases
    special = {
        "湖南通道": "通道侗族自治县",
        "贵州瓮安": "瓮安县",
        "云南威信": "威信县",
        "云南寻甸、禄劝": "皎平渡",
        "四川石棉": "安顺场",
        "四川宝兴": "夹金山",
        "四川小金": "小金县",
        "四川黑水": "芦花镇",
        "四川松潘": "毛儿盖镇",
        "四川阿坝": "阿坝县",
        "四川若尔盖": "若尔盖县",
        "甘肃迭部俄界": "俄界",
        "甘肃迭部腊子口": "腊子口镇",
        "甘肃宕昌哈达铺": "哈达铺镇",
        "甘肃通渭榜罗镇": "榜罗镇",
        "宁夏固原六盘山": "六盘山",
        "陕西吴起镇": "吴起县",
        "甘肃会宁": "会宁县",
        "宁夏西吉将台堡": "将台堡镇",
        "贵州黔西": "黔西县",
        "云南盘县": "盘州市",
        "云南中甸": "香格里拉市",
        "四川甘孜": "甘孜县",
        "四川苍溪强渡嘉陵江": "苍溪县",
        "四川茂县": "茂县",
        "四川卓克基": "卓克基",
        "四川金川绥靖": "金川县",
        "炉霍道孚": "炉霍县",
        "河南罗山何家冲": "何家冲",
        "河南方城独树镇": "独树镇",
        "陕西庾家河": "庾家河",
        "陕西蓝田葛牌镇": "葛牌镇",
        "陕西长安沣峪口": "沣峪口",
        "甘肃泾川王村镇": "王村镇",
        "陕西永坪镇": "永坪镇",
        "福建长汀": "长汀县",
        "江西于都": "于都县",
    }
    return special.get(title, t)

print(f"{'Node':<7} {'Title':<30} {'DB Lat':<10} {'DB Lng':<10} {'API Lat':<10} {'API Lng':<10} {'Dist(km)':<10}")
print("="*90)

mismatches = []
for n in db_nodes:
    nid, title, dlat, dlng = n
    q = smart_query(title, nid)
    
    if dlat is None or dlng is None:
        print(f"{nid:<7} {title:<30} {'NONE':<10} {'NONE':<10} {'SKIP':<10} {'':<10} {'':<10}")
        continue
    
    url = "https://photon.komoot.io/api/?q=" + urllib.parse.quote(q) + "&limit=1&lang=zh"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        if data.get("features"):
            f = data["features"][0]
            g = f["geometry"]
            p = f["properties"]
            if g["type"] == "Point":
                lon, lat = g["coordinates"]
            else:
                lon, lat = 0, 0
            dn = ((lat-dlat)*111)**2 + ((lon-dlng)*85)**2
            dkm = dn**0.5
            src = p.get("name", "?")
            out = f"{nid:<7} {title:<30} {dlat:<10.5f} {dlng:<10.5f} {lat:<10.5f} {lon:<10.5f} {dkm:<10.1f}"
            if dkm > 15:
                out += " !!!"
                mismatches.append((nid, title, dlat, dlng, lat, lon, dkm))
            print(out)
        else:
            print(f"{nid:<7} {title:<30} {dlat:<10.5f} {dlng:<10.5f} {'NOT FOUND':<10} {'':<10}")
    except Exception as e:
        print(f"{nid:<7} {title:<30} {dlat:<10.5f} {dlng:<10.5f} {'ERROR':<10} {str(e)[:30]:<10}")
    time.sleep(0.3)

print()
print(f"\n=== SIGNIFICANT DEVIATIONS (>15km): {len(mismatches)} ===")
for m in mismatches:
    print(f"{m[0]:<7} {m[1]:<30} DB({m[2]:.4f},{m[3]:.4f}) API({m[4]:.4f},{m[5]:.4f}) {m[6]:.1f}km")
