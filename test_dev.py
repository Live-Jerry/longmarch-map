import json, urllib.request
resp = urllib.request.urlopen("http://127.0.0.1:5001/api/v1/routes/autowalk?army=1", timeout=5)
d = json.loads(resp.read())
s = d["data"]["segments"]
n = [x for x in s if x.get("node_id")]
print(f"OK: {len(s)} segs, {len(n)} nodes")
