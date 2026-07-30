import subprocess

ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

# Read index.html
r = subprocess.run(ssh + ['cat "/opt/longmarch-dev/001 项目源码/templates/admin/index.html"'], capture_output=True, timeout=10)
index = r.stdout.decode('utf-8', errors='replace')

# Full file
with open(r'D:\长征文化\_idx_full.html', 'w', encoding='utf-8') as f:
    f.write(index)
print(f'index.html: {len(index)} chars, {index.count(chr(10))+1} lines')
print('Saved to _idx_full.html')
