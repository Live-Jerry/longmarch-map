import os, subprocess

result = subprocess.run(
    ['git', 'show', 'HEAD~5:001 项目源码/static/js/map.js'],
    capture_output=True, text=True, cwd='D:\\长征文化'
)
lines = result.stdout.split('\n')

# Print lines around loadRoutes, including between polyline and circleMarker
in_func = False
for i, line in enumerate(lines, 1):
    if 'function loadRoutes' in line:
        in_func = True
    if in_func:
        print(f'{i:>4}: {line}')
        if in_func and line.strip().startswith('function toggleArmy'):
            break
