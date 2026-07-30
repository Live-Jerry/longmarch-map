with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Check and update
old_line = '- 修复：漫游中重新选择速度不会重新启用"开始"按钮'
new_line  = '- 修复：漫游中重新选择速度不会重新启用"开始"按钮\n- 修复：漫游进行中不能修改速度，暂停后可改'

c = c.replace(old_line, new_line)

with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('done')
