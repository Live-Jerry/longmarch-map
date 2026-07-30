# -*- coding: utf-8 -*-
import sqlite3, json, os

os.chdir(r'D:\长征文化\001 项目源码')
conn = sqlite3.connect(r'data\longmarch.db')
cur = conn.cursor()

# All named route points for Army 1 (中央红军)
cur.execute('SELECT name, is_node, order_index, lat, lng FROM route_point WHERE army=1 AND name IS NOT NULL AND name!="" ORDER BY order_index')
named = cur.fetchall()
print(f'=== Army 1: {len(named)} named points ===')
print(f'{"name":<10} {"type":<6} {"idx":<5} {"lat":<10} {"lng":<10}')
print('-'*45)
for r in named:
    ptype = 'NODE' if r[1] else 'waypt'
    print(f'{r[0]:<10} {ptype:<6} {r[2]:<5} {r[3]:<10.4f} {r[4]:<10.4f}')

# Check the node table to see what names maps have
cur.execute('SELECT node_id, title FROM node ORDER BY node_id')
nodes = cur.fetchall()
print(f'\n=== {len(nodes)} nodes in DB ===')
for n in nodes:
    print(f'  {n[0]:<5} {n[1]}')

# Now check what the GeoJSON API returns - look at how route data is built
cur.execute('SELECT stage, COUNT(*) FROM route_point WHERE army=1 GROUP BY stage')
stages = cur.fetchall()
print(f'\n=== Army 1 stages ===')
for s in stages:
    print(f'  stage="{s[0]}": {s[1]} points')

# Check specific waypoints with names (is_node=0)
cur.execute('SELECT name, order_index, lat, lng, node_id FROM route_point WHERE army=1 AND is_node=0 AND name IS NOT NULL AND name!="" ORDER BY order_index')
waypts = cur.fetchall()
print(f'\n=== Named waypoints (is_node=0, Army 1): {len(waypts)} ===')
for w in waypts:
    print(f'  {w[0]:<10} idx={w[1]:<5} ({w[2]:.4f}, {w[3]:.4f})')

conn.close()
