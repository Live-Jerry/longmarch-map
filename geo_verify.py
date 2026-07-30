import urllib.request, urllib.parse, json, time

nodes = [
    ("1.1", "瑞金"),
    ("1.2", "长汀"),
    ("1.3", "于都"),
    ("2.1", "道县"),
    ("2.1b", "全州"),
    ("3.1", "通道侗族自治县"),
    ("4.1", "黎平"),
    ("4.2", "瓮安"),
    ("4.3", "遵义"),
    ("4.4", "威信县"),
    ("4.5", "苟坝"),
    ("5.1", "赤水河"),
    ("6.1", "皎平渡"),
    ("7.1", "安顺场"),
    ("7.2", "泸定"),
    ("8.1", "夹金山"),
]

# Also known correct coords from the node table for comparison
known = {
    "1.1": (25.8833, 116.02),
    "1.2": (25.8333, 116.36),
    "1.3": (25.95, 115.42),
    "2.1": (25.3, 110.5),
    "3.1": (26.16, 109.78),
    "4.1": (26.23, 109.13),
    "4.3": (27.73, 106.93),
    "7.2": (29.92, 102.23),
    "13.1": (36.92, 107.3),
}

print(f"{'Node':<8} {'Query':<20} {'OSM Lat':<12} {'OSM Lng':<12} {'Known Lat':<12} {'Known Lng':<12} {'Diff'}")
print("="*85)

for nid, query in nodes:
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "longmarch-map/1.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        if data:
            olat = float(data[0]["lat"])
            olng = float(data[0]["lon"])
            klat, klng = known.get(nid, (0, 0))
            if klat:
                dlat = olat - klat
                dlng = olng - klng
                print(f"{nid:<8} {query:<20} {olat:<12.5f} {olng:<12.5f} {klat:<12.5f} {klng:<12.5f} ({dlat:.4f},{dlng:.4f})")
            else:
                print(f"{nid:<8} {query:<20} {olat:<12.5f} {olng:<12.5f} {'-':<12} {'-':<12} N/A")
        else:
            print(f"{nid:<8} {query:<20} {'NOT FOUND':<12} {'':<12} {'-':<12} {'-':<12}")
    except Exception as e:
        print(f"{nid:<8} {query:<20} ERROR: {e}")
    time.sleep(1)
