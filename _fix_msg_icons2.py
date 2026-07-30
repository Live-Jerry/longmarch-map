import subprocess
ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

r = subprocess.run(ssh + [r'cat "/opt/longmarch-dev/001 项目源码/templates/admin/messages.html"'], capture_output=True, timeout=10)
content = r.stdout.decode('utf-8', errors='replace')

# Replace line by line to handle CRLF
lines = content.split('\n')
new_lines = []
changed = 0
for line in lines:
    stripped = line.strip()
    if stripped.startswith('<a href=') and 'admin-nav-item' in stripped:
        if '>总览</a>' in stripped:
            line = line.replace('>总览</a>', '>📊 总览</a>')
            changed += 1
        elif '>节点管理</a>' in stripped and '📊' not in stripped:
            line = line.replace('>节点管理</a>', '>📍 节点管理</a>')
            changed += 1
        elif '>用户管理</a>' in stripped and '📊' not in stripped:
            line = line.replace('>用户管理</a>', '>👥 用户管理</a>')
            changed += 1
        elif '>星火审核</a>' in stripped and '📊' not in stripped:
            line = line.replace('>星火审核</a>', '>✦ 星火审核</a>')
            changed += 1
        elif '>留言管理</a>' in stripped and '📊' not in stripped:
            line = line.replace('>留言管理</a>', '>💬 留言管理</a>')
            changed += 1
        elif '>返回地图</a>' in stripped and '📊' not in stripped:
            line = line.replace('>返回地图</a>', '>← 返回地图</a>')
            changed += 1
    new_lines.append(line)

content = '\n'.join(new_lines)
print(f'Changed {changed} sidebar links')

with open(r'D:\长征文化\_msg_final.html', 'w', encoding='utf-8') as f:
    f.write(content)

subprocess.run(['scp', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', r'D:\长征文化\_msg_final.html', 'root@8.133.203.255:/tmp/_msg3.html'], capture_output=True, timeout=10)
subprocess.run(ssh + ['cp /tmp/_msg3.html /opt/longmarch-dev/001\\\\ 项目源码/templates/admin/messages.html'], capture_output=True, timeout=10)
print('Deployed')
