import subprocess, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

# Read all admin templates
results = {}
for name in ['index', 'nodes', 'sparks', 'users', 'messages']:
    r = subprocess.run(ssh + [f'cat "/opt/longmarch-dev/001 项目源码/templates/admin/{name}.html"'], capture_output=True, timeout=10)
    results[name] = r.stdout.decode('utf-8', errors='replace')

# The base sidebar HTML (from index.html - the canonical version with emojis)
sidebar_html = '''        <div class="admin-sidebar">
            <h2>🚩 管理后台</h2>
            <a href="/admin" class="admin-nav-item" data-page="index">📊 总览</a>
            <a href="/admin/nodes" class="admin-nav-item" data-page="nodes">📍 节点管理</a>
            <a href="/admin/users" class="admin-nav-item" data-page="users">👥 用户管理</a>
            <a href="/admin/sparks" class="admin-nav-item" data-page="sparks">✦ 星火审核</a>
            <a href="/admin/messages" class="admin-nav-item" data-page="messages">💬 留言管理</a>
            <a href="/" class="admin-nav-item" style="margin-top:20px">← 返回地图</a>
        </div>'''

# The nav JS
nav_js = '''    <script>
    // Active nav highlighting (from base.html)
    var path = location.pathname;
    document.querySelectorAll(".admin-nav-item").forEach(function(a) {
        a.classList.toggle("active", a.getAttribute("href") === path);
    });
    </script>'''

# Base.html
base_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}管理后台{% endblock %} -- 重走长征路</title>
    <link rel="stylesheet" href="/static/css/style.css">
    {% block extra_head %}{% endblock %}
</head>
<body>
    <div class="admin-layout">''' + '\n' + sidebar_html + '''

        <div class="admin-main">
            {% block content %}{% endblock %}
        </div>
    </div>''' + '\n' + nav_js + '''
    {% block scripts %}{% endblock %}
</body>
</html>'''

print('base.html OK')

# For each page, extract: title, main content area, and scripts after </div> admin-layout close
def extract_parts(text, name):
    """Extract: title, main-content-html, post-layout-scripts"""
    # Title
    m = re.search(r'<title>(.*?)</title>', text)
    title = m.group(1) if m else '管理后台'
    # Clean title (remove site name suffix)
    title = re.sub(r'\s*[—\-]{1,2}\s*重走长征路', '', title).strip()
    
    # Find admin-layout div and track depth to find its closing
    layout_open = text.find('<div class="admin-layout">')
    if layout_open < 0:
        print(f'{name}: no admin-layout found')
        return None
    
    # Parse from layout_open, track div depth
    depth = 0
    layout_end = -1
    i = layout_open
    while i < len(text):
        # Check for comment
        if text[i:i+4] == '<!--':
            ci = text.find('-->', i)
            if ci >= 0:
                i = ci + 3
                continue
        # Check for closing div
        if text[i:i+6] == '</div>':
            depth -= 1
            if depth == 0 and i > layout_open + 10:
                layout_end = i + 6
                break
            i += 6
            continue
        # Check for opening div
        if text[i:i+4] == '<div' and not text[i+4:i+5].isalpha():
            # Count <div> openings - but need to handle attributes
            depth += 1
            i += 4
            continue
        i += 1
    
    if layout_end < 0:
        print(f'{name}: could not find layout close')
        return None
    
    # Content inside admin-main
    main_start = text.find('<div class="admin-main">', layout_open)
    if main_start < 0:
        print(f'{name}: no admin-main')
        return None
    content_start = main_start + len('<div class="admin-main">')
    content = text[content_start:layout_end].strip()
    
    # Scripts after layout close (before </body>)
    body_close = text.find('</body>', layout_end)
    remainder = text[layout_end:body_close].strip()
    
    # Extract only meaningful scripts/includes (skip empty/whitespace)
    script_lines = []
    for line in remainder.split('\n'):
        s = line.strip()
        if s.startswith('<script') or s.startswith('{% include') or s.startswith('{% script'):
            script_lines.append(line)
    
    scripts = '\n'.join(script_lines)
    
    return {'title': title, 'content': content, 'scripts': scripts}

# Build new templates
new_templates = {}
for name, text in results.items():
    parts = extract_parts(text, name)
    if parts is None:
        print(f'{name}: FAILED')
        continue
    
    new = '{% extends "admin/base.html" %}\n'
    new += '{% block title %}' + parts['title'] + '{% endblock %}\n'
    new += '{% block content %}\n' + parts['content'] + '\n{% endblock %}\n'
    if parts['scripts']:
        new += '{% block scripts %}\n' + parts['scripts'] + '\n{% endblock %}\n'
    
    new_templates[name] = new
    print(f'{name}: {len(new.split(chr(10)))} lines, title="{parts["title"]}", has_scripts={bool(parts["scripts"])}')

# Deploy base.html
with open(r'D:\长征文化\_base.html', 'w', encoding='utf-8') as f:
    f.write(base_html)

r = subprocess.run(['scp', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', r'D:\长征文化\_base.html', 'root@8.133.203.255:/tmp/_base.html'], capture_output=True, timeout=10)
if r.returncode == 0:
    print('base.html scp OK')
else:
    print('base.html scp FAILED')
    print(r.stderr.decode())

# Deploy new templates
for name, new in new_templates.items():
    fp = rf'D:\长征文化\_{name}_new.html'
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new)
    
    r = subprocess.run(['scp', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', fp, f'root@8.133.203.255:/tmp/_{name}.html'], capture_output=True, timeout=10)
    if r.returncode != 0:
        print(f'{name} scp FAILED: {r.stderr.decode()[:200]}')
    
print('All files staged in /tmp/')
