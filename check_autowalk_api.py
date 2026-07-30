import json, sys
d = json.load(sys.stdin)
segs = d.get("data", {}).get("segments", [])
print("Total segments:", len(segs))
nodes = [s for s in segs if s.get("node_id")]
print("Node segments:", len(nodes))
if segs:
    print("First seg:", segs[0].get("title","?"), segs[0].get("node_id","?"))
if nodes:
    print("First node:", nodes[0].get("title","?"), nodes[0].get("node_id","?"))
