import urllib.request, urllib.parse, json, time

nodes = [
    ("瑞金", "1.1"),
    ("长汀", "1.2"),
    ("于都", "1.3"),
    ("道县", "2.1"),
    ("全州", "2.1b"),
    ("通道侗族自治县", "3.1"),
    ("黎平", "4.1"),
    ("瓮安", "4.2"),
    ("遵义", "4.3"),
    ("威信县", "4.4"),
    ("赤水", "5.1"),
    ("皎平渡", "6.1"),
    ("安顺场", "7.1"),
    ("泸定", "7.2"),
    ("夹金山", "8.1"),
    ("小金", "9.1"),
    ("吴起县", "13.1"),
    ("会宁县", "14.1"),
    ("将台堡", "14.2"),
    ("六盘山", "12.1"),
    ("哈达铺", "11.3"),
    ("腊子口", "11.2"),
    ("毛儿盖", "10.1"),
    ("若尔盖", "10.3"),
]

db_coords = {
    "1.1": (25.8833, 116.02),
    "1.2": (25.8333, 116.36),
    "1.3": (25.95, 115.42),
    "2.1": (25.3, 110.5),
    "3.1": (26.16, 109.78),
    "4.1": (26.23, 109.13),
    "4.2": (27.07, 107.47),
    "4.3": (27.73, 106.93),
    "4.4": (27.85, 105.03),
    "5.1": (28.3, 106.03),
    "6.1": (26.3, 102.38),
    "7.1": (29.17, 102.3),
    "7.2": (29.92, 102.23),
    "8.1": (30.8, 102.5),
    "9.1": (31.0, 102.4),
    "10.1": (32.8, 102.8),
    "10.3": (33.7, 103.6),
    "11.2": (34.1, 104.3),
    "11.3": (34.0, 104.3),
    "12.1": (35.68, 106.22),
    "13.1": (36.92, 107.3),
    "14.1": (35.6937, 105.0523),
    "14.2": (35.82, 105.87),
}

print(f"{'Name':<15} {'Node':<6} {'API Lat':<10} {'API Lng':<10} {'DB Lat':<10} {'DB Lng':<10} {'Delta'}")
print("="*75)

for name, nid in nodes:
    q = urllib.parse.quote(name)
    url = f"https://photon.komoot.io/api/?q={q}&limit=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        if data.get("features"):
            feat = data["features"][0]
            geom = feat.get("geometry", {})
            if geom.get("type") == "Point":
                lon, lat = geom["coordinates"]
            else:
                lon, lat = 0, 0
            props = feat.get("properties", {})
            display = props.get("name", name)
            if nid in db_coords:
                dl, dln = db_coords[nid]
                print(f"{display:<15} {nid:<6} {lat:<10.5f} {lon:<10.5f} {dl:<10.5f} {dln:<10.5f} ({lat-dl:.4f},{lon-dln:.4f})")
            else:
                print(f"{display:<15} {nid:<6} {lat:<10.5f} {lon:<10.5f} {'-':<10} {'-':<10}")
        else:
            print(f"{name:<15} {nid:<6} NOT FOUND")
    except Exception as e:
        print(f"{name:<15} {nid:<6} ERROR: {e}")
    time.sleep(0.5)
