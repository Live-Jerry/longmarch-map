import json
with open("/tmp/route_api.json") as f:
    d = json.load(f)
pts = d["data"]["points"]
for p in pts[:8]:
    print(f"  {p.get('name','?'):<10} is_node={p.get('is_node')} node_id={p.get('node_id','?')} node_title={p.get('node_title','?')}")
print(f"\nTotal points: {len(pts)}")
print(f"With name: {sum(1 for p in pts if p.get('name'))}")
