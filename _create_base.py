import subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

# Read all admin templates
results = {}
for name in ['index', 'nodes', 'sparks', 'users', 'messages']:
    r = subprocess.run(ssh + [f'cat "/opt/longmarch-dev/001 项目源码/templates/admin/{name}.html"'], capture_output=True, timeout=10)
    results[name] = r.stdout.decode('utf-8', errors='replace')

# --- Extract common HEAD and SIDEBAR from index.html ---
index = results['index']

# The head section
head_start = index.find('<head>')
head_end = index.find('</head>')
head_content = index[head_start:head_end+7]

# CSS link
css_link = '<link rel="stylesheet" href="/static/css/style.css">'

# Sidebar HTML (the admin-sidebar div)
sidebar_start = index.find('<div class="admin-sidebar">')
sidebar_end = index.find('</div>', sidebar_start)
sidebar_div = index[sidebar_start:sidebar_end+6]

# JS active nav script
nav_script = '''    <script>
    // Active nav highlighting
    var path = location.pathname;
    document.querySelectorAll(".admin-nav-item").forEach(function(a) {
        a.classList.toggle("active", a.getAttribute("href") === path);
    });
    </script>'''

# Build base.html
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
    <div class="admin-layout">
        ''' + sidebar_div + '''

        <div class="admin-main">
            {% block content %}{% endblock %}
        </div>
    </div>

    ''' + nav_script + '''
    {% block scripts %}{% endblock %}
</body>
</html>'''

print(f'base.html built: {len(base_html)} chars')

# --- Transform each admin page ---
# We need to extract: DOCTYPE, <head>, <title>, sidebar div opening, admin-main div, <script> at bottom

def extract_content(text):
    """Extract the main content between admin-main div open and the closing </div> of admin-layout"""
    # Find the content inside admin-main
    main_start = text.find('<div class="admin-main">')
    if main_start < 0:
        return None
    main_end = text.find('</div>', main_start)
    # Actually need to find the matching </div> that closes admin-main
    # Strategy: find the next </div> after </html> or use depth counting

    # Simpler: find the content between admin-main and the whitespace before </div>
    # that leads to admin-layout close

    # Find admin-main opening
    open_tag_start = text.find('<div class="admin-main">')
    content_start = open_tag_start + len('<div class="admin-main">')
    
    # Find the closing </div></div> structure (admin-main + admin-layout)
    # Find the </div> that closes admin-layout by looking from end
    layout_end = text.find('</div>', text.find('admin-layout'))
    second_close = text.find('</div>', layout_end + 6)
    
    # The admin-main content ends at layout_end
    content = text[content_start:layout_end].rstrip()
    return content

def extract_scripts(text):
    """Extract scripts and includes from the body, EXCLUDING nav_script"""
    # Find everything between nav_script injection point and </body>
    body_start = text.find('<body>')
    body_end = text.find('</body>')
    body = text[body_start:body_end]
    
    # Extract scripts/script tags/includes
    parts = []
    in_admin_main = False
    for line in body.split('\n'):
        s = line.strip()
        if 'admin-main' in s:
            in_admin_main = True
            continue
        if in_admin_main:
            if s.startswith('<script') or s.startswith('{% include') or s.startswith('{% script'):
                parts.append(line)
            elif s.startswith('<') and ('script' in s or 'include' in s):
                parts.append(line)
        # After main content
        if '</div>' == s and in_admin_main:
            in_admin_main = False
    return '\n'.join(parts)

# Better approach: replace only the core content
# For each page, extract: page-specific content (inside admin-main div), scripts (after admin layout close)

def transform_page(name, text):
    """Transform an admin page to extend base.html"""
    # Extract title
    import re
    title_match = re.search(r'<title>(.*?)</title>', text)
    title = title_match.group(1) if title_match else '管理后台'
    
    # Remove the title suffix " -- 重走长征路" or " — 重走长征路"
    title = title.replace(' -- 重走长征路', '').replace(' — 重走长征路', '')
    
    # Extract everything after </div> (admin-layout closing) and before </body>
    # This contains script tags and includes
    layout_close_idx = text.find('<div class="admin-layout">')
    layout_end_idx = -1
    # Count div nesting to find correct closing
    depth = 0
    for i in range(layout_close_idx, len(text)):
        if text[i:i+4] == '<!--':
            nci = text.find('-->', i)
            if nci >= 0:
                i = nci + 3
                continue
        if text[i:i+3] == '</div>':
            depth -= 1
        elif text[i:i+3] == '<div':
            depth += 1
        if depth == 0:
            layout_end_idx = i + 6  # end of </div>
            break
    
    if layout_end_idx < 0:
        print(f'{name}: could not find layout end')
        return None
    
    # Extract main content
    main_start = text.find('<div class="admin-main">')
    main_content_start = main_start + len('<div class="admin-main">')
    
    # The content goes to layout_end_idx
    raw_content = text[main_content_start:layout_end_idx].strip()
    
    # Extract scripts (everything from layout_end_idx+1 to </body>)
    body_close = text.find('</body>', layout_end_idx)
    raw_scripts = text[layout_end_idx:body_close].strip()
    
    # Build new template
    new_template = '{% extends "admin/base.html" %}\n'
    new_template += '{% block title %}' + title + '{% endblock %}\n'
    new_template += '{% block content %}\n' + raw_content + '\n{% endblock %}\n'
    
    # Check if there are includes or scripts
    has_include = '{% include' in raw_scripts
    has_script = '<script' in raw_scripts
    
    if has_include or has_script:
        new_template += '{% block scripts %}\n' + raw_scripts + '\n{% endblock %}\n'
    
    return new_template

# Test with messages.html first
for name in ['messages', 'index', 'nodes', 'sparks', 'users']:
    text = results[name]
    new = transform_page(name, text)
    if new:
        lines = len(new.split('\n'))
        print(f'{name}: transformed OK ({lines} lines)')
        # Write to file for inspection
        with open(f'D:\\长征文化\\_{name}_new.html', 'w', encoding='utf-8') as f:
            f.write(new)
        print(f'  -> _{name}_new.html')
    else:
        print(f'{name}: FAILED')
