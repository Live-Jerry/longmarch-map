with open('001 项目源码/static/js/controls.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find startAutowalk and block of cleanup code
for i, line in enumerate(lines, 1):
    if 'function startAutowalk' in line or '清理已有' in line or 'btn-autowalk-start' in line:
        print(f'Line {i:>4}: {line.rstrip()}')
