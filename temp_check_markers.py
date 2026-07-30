with open('001 项目源码/static/js/map.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Check for markers that show intermediate route points
checks = [
    'circleMarker', 'route.*marker', 'name.*label', 
    'point.*label', 'route.*label', 'divIcon.*route',
    'L.marker.*route', 'addTo.*routeGroup'
]
for c in checks:
    import re
    found = re.findall(c, content, re.IGNORECASE)
    print(f'{c}: {len(found)} matches')

# Show lines with circleMarker
for i, line in enumerate(content.split('\n'), 1):
    if 'circleMarker' in line:
        print(f'  L.{i}: {line.strip()[:100]}')
