# -*- coding: utf-8 -*-
import sys, json, urllib.request

url = 'http://127.0.0.1:5000/api/v1/routes/geojson'
resp = urllib.request.urlopen(url)
data = json.loads(resp.read().decode('utf-8'))

f = data['features'][0]
pts = f['properties']['points']
print(f'Army {f["properties"]["army"]}: {len(pts)} points total')
names = [p['title'] for p in pts if p.get('title')]
print(f'{len(names)} points with names')
print('First 10:', names[:10])

# Check if all route point labels would be created (non-empty titles)
empty = [p for p in pts if not p.get('title')]
print(f'{len(empty)} points with empty title (would be skipped)')
