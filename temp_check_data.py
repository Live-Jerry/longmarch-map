import json

with open('001 项目源码/data/node_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

if isinstance(data, dict):
    print('Keys:', list(data.keys()))
    for k in ['routes', 'route', 'segments', 'route_points', 'waypoints', 'features']:
        if k in data:
            v = data[k]
            print(f'  {k}: type={type(v).__name__}', end='')
            if isinstance(v, list):
                print(f', len={len(v)}')
                if len(v) > 0:
                    print(f'    first item: {str(v[0])[:100]}')
            elif isinstance(v, dict):
                print(f', keys={list(v.keys())[:5]}')
            else:
                print()
elif isinstance(data, list):
    print(f'List of {len(data)} items')
    if len(data) > 0:
        print(f'First item: {str(data[0])[:100]}')
else:
    print('Unexpected type:', type(data))
