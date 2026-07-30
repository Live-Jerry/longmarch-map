with open('001 项目源码/static/js/controls.js', 'r', encoding='utf-8') as f:
    code = f.read()

checks = [
    ('title field in routePts', 'title: s.title || ""'),
    ('animateMovement passes target.title', 'target.title'),
    ('function signature has pointTitle', 'function updateAutowalkProgress(nodeIdx, total, progress, pointTitle)'),
    ('pointTitle check', 'if (pointTitle)'),
    ('current-title set to pointTitle', 'el.querySelector(".current-title").textContent = pointTitle'),
]
for name, pattern in checks:
    if pattern in code:
        print(f'OK: {name}')
    else:
        print(f'MISSING: {name}')
print()
print('Lines with updateAutowalkProgress:')
for i, line in enumerate(code.split('\n'), 1):
    if 'updateAutowalkProgress' in line:
        print(f'  {i}: {line.strip()[:100]}')
