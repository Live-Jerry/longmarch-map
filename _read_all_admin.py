import subprocess

ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

for name in ['nodes', 'sparks', 'users', 'messages']:
    r = subprocess.run(ssh + [f'cat "/opt/longmarch-dev/001 项目源码/templates/admin/{name}.html"'], capture_output=True, timeout=10)
    content = r.stdout.decode('utf-8', errors='replace')
    with open(f'D:\\长征文化\\_{name}_full.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'{name}.html: {len(content)} chars, {content.count(chr(10))+1} lines')
