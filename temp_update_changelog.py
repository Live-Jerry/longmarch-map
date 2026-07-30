with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
    c = f.read()

old = '- 修复：启动后禁用"开始"按钮，防止再次点击\n- EC变更跟踪表第20条已同步更新'
new = old.replace(
    '- EC变更跟踪表第20条已同步更新',
    '- 修复：漫游中重新选择速度不会重新启用"开始"按钮\n- EC变更跟踪表第20条已同步更新'
)
c = c.replace(old, new)

with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('done')
