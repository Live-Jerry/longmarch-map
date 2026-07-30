import subprocess

ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

# Read current messages.html
r = subprocess.run(ssh + [r'cat "/opt/longmarch-dev/001 项目源码/templates/admin/messages.html"'], capture_output=True, timeout=10)
content = r.stdout.decode('utf-8', errors='replace')

# Fix: remove 'return;' from outside-function context
old = 'if (!localStorage.getItem("lm_token")) { location.href = "/login"; return; }'
new = 'if (!localStorage.getItem("lm_token")) { location.href = "/login"; return; }'
# Actually the fix is different - wrap everything in an IIFE or just remove the return

old2 = '''    <script>
    if (!localStorage.getItem("lm_token")) { location.href = "/login"; return; }

    function loadMessages() {'''

new2 = '''    <script>
    (function() {
    if (!localStorage.getItem("lm_token")) { location.href = "/login"; return; }

    function loadMessages() {'''

old_end = '''    loadMessages();
    </script>'''

new_end = '''    loadMessages();
    })();
    </script>'''

if old2 in content and old_end in content:
    content = content.replace(old2, new2, 1)
    content = content.replace(old_end, new_end, 1)
    
    # Write back
    with open(r'D:\长征文化\_msg_fixed.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    subprocess.run(['scp', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', 
        r'D:\长征文化\_msg_fixed.html',
        'root@8.133.203.255:"/opt/longmarch-dev/001 项目源码/templates/admin/messages.html"'], capture_output=True, timeout=10)
    print('Fixed: wrapped in IIFE')
else:
    print('Patterns not found')
    if old2 not in content:
        print('old2 not found')
    if old_end not in content:
        print('old_end not found')
