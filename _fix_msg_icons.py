import subprocess
ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

r = subprocess.run(ssh + [r'cat "/opt/longmarch-dev/001 项目源码/templates/admin/messages.html"'], capture_output=True, timeout=10)
content = r.stdout.decode('utf-8', errors='replace')

old = '''            <a href="/admin"       class="admin-nav-item">总览</a>
            <a href="/admin/nodes"  class="admin-nav-item">节点管理</a>
            <a href="/admin/users"  class="admin-nav-item">用户管理</a>
            <a href="/admin/sparks" class="admin-nav-item">星火审核</a>
            <a href="/admin/messages" class="admin-nav-item active">留言管理</a>
            <a href="/"            class="admin-nav-item" style="margin-top:20px">返回地图</a>'''

new = '''            <a href="/admin"       class="admin-nav-item">📊 总览</a>
            <a href="/admin/nodes"  class="admin-nav-item">📍 节点管理</a>
            <a href="/admin/users"  class="admin-nav-item">👥 用户管理</a>
            <a href="/admin/sparks" class="admin-nav-item">✦ 星火审核</a>
            <a href="/admin/messages" class="admin-nav-item active">💬 留言管理</a>
            <a href="/"            class="admin-nav-item" style="margin-top:20px">← 返回地图</a>'''

# Debug: check exact match
idx = content.find('<a href="/admin"')
print(f'Found at idx: {idx}')
snippet = content[idx:idx+700]
print('Actual:')
print(repr(snippet[:600]))
print()
print('Expected:')
print(repr(old[:600]))
print()
print('Match:', repr(snippet[:500]) == repr(old[:500]))
