import urllib.request, json

for army in [1, 2, 4, 25]:
    url = "http://127.0.0.1:5001/api/v1/routes/autowalk?army=" + str(army)
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read())
    segs = data.get("data", {}).get("segments", [])
    print("Army", army, ":", len(segs), "segments")
    for s in segs:
        if s.get("node_id"):
            print("  ", s["index"], s.get("node_id"), s.get("title","")[:20],
                  "({:.3f},{:.3f})".format(s["lat"], s["lng"]))
