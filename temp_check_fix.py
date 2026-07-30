with open('001 项目源码/static/js/controls.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if 'disabled = true' in line:
        print(f'Line {i}: {line.rstrip()}')
    if '清理已有' in line:
        print(f'Line {i}: {line.rstrip()}')
