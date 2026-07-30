import urllib.request, json

resp = urllib.request.urlopen("http://127.0.0.1:5001/api/v1/routes/geojson")
data = json.loads(resp.read())
for f in data["features"]:
    a = f["properties"]["army"]
    coords = f["geometry"]["coordinates"]
    print("army=%s (type=%s), points=%d" % (a, type(a).__name__, len(coords)))

# Also check node army values
resp2 = urllib.request.urlopen("http://127.0.0.1:5001/api/v1/nodes?per_page=1000")
data2 = json.loads(resp2.read())
items = data2.get("data", {}).get("items", data2.get("data", {}).get("nodes", []))
armies = set()
for n in items:
    armies.add(str(n.get("army", "NONE")))
print("\nNode army values:", sorted(armies))
print("Total nodes:", len(items))

# Check node armies for army 4
army4_nodes = [n for n in items if str(n.get("army")) == "4" or n.get("army") == "红四方面军"]
print("Army 4 nodes:", len(army4_nodes))
for n in army4_nodes:
    print("  %s: %s -> %s" % (n.get("node_id"), n.get("title","")[:20], n.get("army")))
