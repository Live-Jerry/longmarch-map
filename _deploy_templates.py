import subprocess, shutil, os

ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

# Copy files on server
deploy_script = '''import shutil, os

files = {
    '/tmp/_base.html': '/opt/longmarch-dev/001 项目源码/templates/admin/base.html',
    '/tmp/_index.html': '/opt/longmarch-dev/001 项目源码/templates/admin/index.html',
    '/tmp/_nodes.html': '/opt/longmarch-dev/001 项目源码/templates/admin/nodes.html',
    '/tmp/_sparks.html': '/opt/longmarch-dev/001 项目源码/templates/admin/sparks.html',
    '/tmp/_users.html': '/opt/longmarch-dev/001 项目源码/templates/admin/users.html',
    '/tmp/_messages.html': '/opt/longmarch-dev/001 项目源码/templates/admin/messages.html',
}

for src, dst in files.items():
    if os.path.exists(src):
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        print(f'copied {src} -> {dst} ({size} bytes)')
    else:
        print(f'MISSING: {src}')
'''

with open(r'D:\长征文化\_deploy.py', 'w') as f:
    f.write(deploy_script)

subprocess.run(['scp', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', r'D:\长征文化\_deploy.py', 'root@8.133.203.255:/tmp/_deploy.py'], capture_output=True, timeout=10)
r = subprocess.run(ssh + ['python3 /tmp/_deploy.py'], capture_output=True, timeout=15)
print(r.stdout.decode('utf-8', errors='replace'))
print('err:', r.stderr.decode('utf-8', errors='replace')[:200])
