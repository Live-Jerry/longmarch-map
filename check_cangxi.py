import sqlite3, urllib.request, json

DB = "/opt/longmarch-dev/001 项目源码/data/longmarch.db"

# Check route_point data
c = sqlite3.connect(DB).cursor()
print("=== route_point 苍溪 ===")
c.execute("SELECT id, name, army, node_id, lat, lng, order_index FROM route_point WHERE name LIKE '%苍%'")
for r in c.fetchall():
    print(f"  {r}")

print("\n=== route_point army 4 count ===")
c.execute("SELECT COUNT(*) FROM route_point WHERE army=4")
print(f"  {c.fetchone()[0]} points")

print("\n=== API check: army 4 autowalk ===")
url = "http://localhost:5002/api/v1/routes/autowalk?army=4"
resp = urllib.request.urlopen(url)
data = json.loads(resp.read())
segs = data.get("data", {}).get("segments", [])
for s in segs:
    nid = s.get("node_id") or "-"
    if s.get("title") and ("苍" in s["title"] or "溪" in s["title"]):
        print(f"  FOUND: {s['index']}: {s['title']} node={nid} ({s['lat']},{s['lng']})")
if not any("苍" in str(s) or "溪" in str(s) for s in segs):
    print("  苍溪 NOT FOUND in API response!")
    for s in segs[:5]:
        print(f"  {s['index']}: {s.get('title','?')}")
    print("  ...")
    for s in segs[-3:]:
        print(f"  {s['index']}: {s.get('title','?')}")
