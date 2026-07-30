with open('001 项目源码/static/js/controls.js', 'r', encoding='utf-8') as f:
    c = f.read()

opens = c.count('{') + c.count('(') + c.count('[')
closes = c.count('}') + c.count(')') + c.count(']')
print(f'括号匹配: {opens}/{closes}', 'OK' if opens == closes else 'FAIL')

print('A-清理标记:', 'removeLayer(autowalkState.marker)' in c)
print('A-animFrame清除:', 'clearTimeout(autowalkState.animFrame)' in c)
print('A-waitTimer清除:', 'clearTimeout(autowalkState.waitTimer)' in c)

idx = c.find('btn-autowalk-start')
if idx >= 0:
    after = c[idx+18:idx+50]
    print(f'B-禁用按钮: {"disabled = true" in after} (remainder:{after[:20]})')

# Check that cleanup is in startAutowalk specifically
sa_start = c.find('function startAutowalk')
sa_block = c[sa_start:sa_start+150]
print(f'C-清理在startAutowalk中: {"removeLayer" in sa_block}')
