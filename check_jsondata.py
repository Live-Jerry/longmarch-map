import sys, json

with open("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/node_data.json") as f:
    data = json.load(f)

if isinstance(data, list):
    print(f"Total nodes in node_data.json: {len(data)}")
    for n in data:
        nid = n.get("node_id", "?")
        title = n.get("title", "?")
        lat = n.get("lat", "?")
        lng = n.get("lng", "?")
        print(f"{nid} {title}: ({lat},{lng})")
