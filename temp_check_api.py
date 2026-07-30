import urllib.request, json

url = "http://127.0.0.1:5000/api/v1/routes/autowalk?army=1&speed_kmh=30"
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read().decode())

s = data.get('segments', [])
print(f'Total segments: {len(s)}')
print('First 8:')
for seg in s[:8]:
    print(f'  lat={seg.get("lat")}, lng={seg.get("lng")}, title="{seg.get("title","")}", node_id={seg.get("node_id","")}')
print('Segments 10-15:')
for seg in s[10:15]:
    print(f'  lat={seg.get("lat")}, lng={seg.get("lng")}, title="{seg.get("title","")}", node_id={seg.get("node_id","")}')
