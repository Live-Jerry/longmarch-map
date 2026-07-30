import json, sys

with open(sys.argv[1], "r", encoding="utf-8") as f:
    data = json.load(f)

for key, info in data["routes"].items():
    print("=== %s: %s (%d pts) ===" % (key, info["name"], len(info["waypoints"])))
    for i, wp in enumerate(info["waypoints"]):
        print("  [%2d] %s (%.5f, %.5f)" % (i+1, wp["name"], wp["lat"], wp["lng"]))
