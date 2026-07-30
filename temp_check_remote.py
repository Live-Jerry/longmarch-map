import json
with open('/opt/longmarch-dev/001 项目源码/data/node_data.json') as f:
    data = json.load(f)
if isinstance(data, list):
    print(f'List of {len(data)} items')
    print('First keys:', list(data[0].keys()) if data else 'empty')
elif isinstance(data, dict):
    print('Keys:', list(data.keys()))
