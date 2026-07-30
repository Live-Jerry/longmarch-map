import subprocess

base = '0beb056'
cwd = 'D:\\长征文化'
result = subprocess.run(
    ['git', 'show', f'{base}:001 项目源码/static/js/controls.js'],
    capture_output=True, text=True, cwd=cwd
)
lines = result.stdout.split('\n')

# Print lines with L.divIcon or L.marker
for i, line in enumerate(lines, 1):
    if 'L.divIcon' in line or 'L.marker' in line or 'route-point' in line:
        # Print 2 lines before and after
        start = max(0, i-3)
        end = min(len(lines), i+3)
        print(f'--- Lines {start+1}-{end} ---')
        for j in range(start, end):
            print(f'  {j+1}: {lines[j]}')
        print()
