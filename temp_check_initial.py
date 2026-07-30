import subprocess

base = '0beb056'
cwd = 'D:\\长征文化'

for f in ['map.js', 'controls.js', 'nodes.js']:
    try:
        result = subprocess.run(
            ['git', 'show', f'{base}:001 项目源码/static/js/{f}'],
            capture_output=True, text=True, cwd=cwd
        )
        content = result.stdout
        # Count specific keywords
        for kw in ['route-point', 'RoutePoint', 'routePoint', 'point', 'label', 'L.divIcon', 'L.marker']:
            c = content.count(kw)
            if c > 0:
                print(f'{f}: {kw} = {c}')
        print()
    except:
        print(f'{f}: ERROR')
