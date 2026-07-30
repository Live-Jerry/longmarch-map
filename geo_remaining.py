import subprocess, json, time, urllib.parse

# Nodes that were NOT in the first successful batch
extra_queries = {
    "9.2": ("两河口", "两河口镇 小金"),
    "9.3": ("芦花镇", "芦花镇 黑水"),
    "10.2": ("松潘草地", "松潘草地"),
    "11.1": ("俄界", "俄界 迭部"),
    "11.4": ("榜罗镇", "榜罗镇"),
    "E1.1": ("桑植", "桑植县"),
    "E2.1": ("石阡", "石阡县"),
    "E3.1": ("黔西", "黔西县"),
    "E4.1": ("盘县", "盘州市"),
    "E5.1": ("中甸", "香格里拉"),
    "E5.2": ("甘孜", "甘孜县"),
    "E6.1": ("阿坝", "阿坝县"),
    "E6.2": ("岷县", "岷县"),
    "S1.1": ("苍溪", "苍溪县"),
    "S2.1": ("茂县", "茂县"),
    "S5.1": ("卓克基", "卓克基镇"),
    "S6.2": ("金川", "金川县"),
    "S7.1": ("炉霍", "炉霍县"),
    "H1.1": ("何家冲", "何家冲 罗山"),
    "H2.1": ("独树镇", "独树镇 方城"),
    "H3.1": ("庾家河", "庾家河"),
    "H4.1": ("葛牌镇", "葛牌镇"),
    "H5.1": ("沣峪口", "沣峪口"),
    "H6.1": ("王村镇", "王村镇 泾川"),
    "H6.2": ("永坪镇", "永坪镇 延川"),
}

print(f"{'Node':<7} {'Name':<15} {'Lat':<12} {'Lng':<12} {'Result':<12}")
print("="*58)

for nid, (name, query) in extra_queries.items():
    q = urllib.parse.quote(query)
    url = f"https://photon.komoot.io/api/?q={q}&limit=1"
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "10", url],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        if data.get("features"):
            f = data["features"][0]
            g = f["geometry"]
            p = f["properties"]
            if g["type"] == "Point":
                lon, lat = g["coordinates"]
                src = p.get("name", "?")
                state = p.get("state", "?")
                print(f"{nid:<7} {name:<15} {lat:<12.5f} {lon:<12.5f} {src}({state})")
            else:
                print(f"{nid:<7} {name:<15} NOT POINT")
        else:
            print(f"{nid:<7} {name:<15} NOT FOUND")
    except Exception as e:
        print(f"{nid:<7} {name:<15} ERROR: {e}")
    time.sleep(1)
