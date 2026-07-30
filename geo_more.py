import urllib.request, urllib.parse, json, time

queries = [
    ("赤水市", "5.1"),
    ("苟坝", "4.5"),
    ("两河口", "9.2"),
    ("巴西镇", "10.3"),
    ("俄界", "11.1"),
    ("榜罗镇", "11.4"),
    ("卢花镇", "9.3"),
    ("沙窝", "10.1"),
    ("松潘草地", "10.2"),
    ("安顺场", "7.1"),
]

for q, nid in queries:
    url = "https://photon.komoot.io/api/?q=" + urllib.parse.quote(q) + "&limit=1&lang=zh"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        if data.get("features"):
            f = data["features"][0]
            p = f["properties"]
            g = f["geometry"]
            name = p.get("name", "?")
            state = p.get("state", "?")
            if g["type"] == "Point":
                lon, lat = g["coordinates"]
                print(f"{q:<15} {nid:<6} lat={lat:.5f} lon={lon:.5f} ({name}, {state})")
            else:
                print(f"{q:<15} {nid:<6} NOT A POINT")
        else:
            print(f"{q:<15} {nid:<6} NOT FOUND")
    except Exception as e:
        print(f"{q:<15} {nid:<6} ERROR: {e}")
    time.sleep(0.5)
