import urllib.request, json

for army in [1, 2, 4, 25]:
    url = f"http://localhost:5002/api/v1/routes/autowalk?army={army}"
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read())
    segs = data.get("data", {}).get("segments", [])
    print(f"=== Army {army}: {len(segs)} segments ===")
    for s in segs:
        nid = s.get("node_id") or "-"
        title = s.get("title", "")[:25]
        print(f"  {s['index']:3d}: node={nid:8} {title:25} ({s['lat']:.4f}, {s['lng']:.4f})")
    print()
