import subprocess, os

# Fix all admin sidebars - add properly indented messages link
pages = ['nodes.html', 'sparks.html', 'users.html', 'index.html']
base = '/opt/longmarch-dev/001 项目源码/templates/admin'
ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']
key = r'C:\Users\RP Conference\.ssh\longmarch_ecs'

for page in pages:
    # Read from server using grep to get lines around sidebar
    read_cmd = f'cat "{base}/{page}"'
    r = subprocess.run(ssh + [read_cmd], capture_output=True, timeout=10)
    content = r.stdout.decode('utf-8', errors='replace')
    
    # Split into lines
    lines = content.split('\n')
    new_lines = []
    msgs_added = False
    
    for line in lines:
        stripped = line.strip()
        
        # Fix existing malformed messages link
        if '/admin/messages' in stripped and 'admin-nav' in stripped:
            new_lines.append('            <a href="/admin/messages" class="admin-nav-item">留言管理</a>')
            msgs_added = True
            continue
        
        # If we hit the return-to-map link and haven't added messages yet
        if not msgs_added and '返回地图' in stripped and 'admin-nav' in stripped:
            new_lines.append('            <a href="/admin/messages" class="admin-nav-item">留言管理</a>')
            msgs_added = True
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Write to local temp file
    local = f'D:\\长征文化\\_adm_{page}'
    with open(local, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # SCP using proper quoting for the remote path
    remote = f'root@8.133.203.255:"{base}/{page}"'
    scp_cmd = ['scp', '-i', key, local, remote]
    subprocess.run(scp_cmd, capture_output=True, timeout=10)
    os.remove(local)
    print(f'Fixed {page}: msgs_added={msgs_added}')

print('All sidebars fixed')
