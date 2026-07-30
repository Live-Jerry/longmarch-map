import json

with open('001 项目源码/data/node_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check first node for active_sections
node = data[0]
print('First node keys:', list(node.keys()))
print('title:', node.get('title'))
print('active_sections:', node.get('active_sections', 'NOT FOUND'))
if 'active_sections' in node:
    sec = node['active_sections']
    print(f'  type: {type(sec).__name__}', end='')
    if isinstance(sec, list):
        print(f', len: {len(sec)}')
        print(f'  first: {sec[0]}')
    elif isinstance(sec, str):
        print(f', val: {sec[:200]}')

# Count nodes with active_sections
with_sec = sum(1 for n in data if n.get('active_sections'))
print(f'\nNodes with active_sections: {with_sec}/{len(data)}')

# Show a few
for n in data:
    s = n.get('active_sections')
    if s and isinstance(s, list) and len(s) > 0:
        print(f'  {n["title"]}: {len(s)} sections, first={s[0][:80] if isinstance(s[0], str) else str(s[0])[:80]}')
