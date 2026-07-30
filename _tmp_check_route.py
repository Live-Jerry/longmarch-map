# -*- coding: utf-8 -*-
import json, sqlite3, os

os.chdir(r'D:\长征文化\001 项目源码')

# Check node_data.json for route point names
with open(r'data\node_data.json','r',encoding='utf-8') as f:
    data = json.load(f)

sample = data[0] if data else {}
print('Keys in first node:', list(sample.keys()))
print()

# Check if there's route_points or waypoints field
for n in data:
    for k in n.keys():
        if 'route' in k.lower() or 'way' in k.lower() or 'point' in k.lower():
            print(f'  node {n.get("node_id","?")}: has key "{k}"')

# Also check route_point table
conn = sqlite3.connect(r'data\longmarch.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print('\nTables:', tables)

if 'route_point' in tables:
    cur.execute('PRAGMA table_info(route_point)')
    cols = [c[1] for c in cur.fetchall()]
    print('route_point columns:', cols)
    cur.execute('SELECT * FROM route_point LIMIT 5')
    for r in cur.fetchall():
        print('  ', r)
    cur.execute('SELECT COUNT(*) FROM route_point')
    cnt = cur.fetchone()[0]
    print(f'Total route_point rows: {cnt}')
    
    # Check for army 1 (中央红军) route points
    if 'army' in cols:
        cur.execute('SELECT COUNT(*) FROM route_point WHERE army=1')
        cnt1 = cur.fetchone()[0]
        print(f'Army 1 points: {cnt1}')
        
        # Check if any have names
        if 'name' in cols:
            cur.execute('SELECT name FROM route_point WHERE army=1 AND name IS NOT NULL AND name!="" LIMIT 10')
            named = cur.fetchall()
            print(f'Army 1 named points: {len(named)}')
            for r in named[:5]:
                print('  ', r)

conn.close()
