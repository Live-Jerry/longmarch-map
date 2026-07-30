import subprocess

ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

# First SCP all files to /tmp/
files = {
    r'D:\长征文化\_idx_full.html': '/tmp/_idx.html',
    r'D:\长征文化\_nodes_full.html': '/tmp/_nds.html',
    r'D:\长征文化\_sparks_full.html': '/tmp/_spr.html',
    r'D:\长征文化\_users_full.html': '/tmp/_usr.html',
}

for local, remote in files.items():
    subprocess.run(['scp', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', local, f'root@8.133.203.255:{remote}'], capture_output=True, timeout=10)

# Use Python on server to copy each file one by one
for fname in ['_idx', '_nds', '_spr', '_usr']:
    # Create and run a simple copy script
    cmd = f"python3 -c \"import shutil; shutil.copy('/tmp/{fname}.html', '/opt/longmarch-dev/001 项目源码/templates/admin/" + "{}.html".format({'idx': 'index', 'nds': 'nodes', 'spr': 'sparks', 'usr': 'users'}[fname.split('_')[1][:3]]) + r"'); print('ok')"
    
    r = subprocess.run(ssh + [cmd], capture_output=True, timeout=15)
    out = r.stdout.decode('utf-8', errors='replace')
    err = r.stderr.decode('utf-8', errors='replace')
    if out.strip():
        print(f'{fname}: {out.strip()}')
    else:
        print(f'{fname}: FAILED. err={err[:100]}')

# Also copy messages.html (the extends base version with correct scripts)
subprocess.run(['scp', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', r'D:\长征文化\_msg_correct.html', 'root@8.133.203.255:/tmp/_msg.html'], capture_output=True, timeout=10)
r = subprocess.run(ssh + ["python3 -c \"import shutil; shutil.copy('/tmp/_msg.html', '/opt/longmarch-dev/001 项目源码/templates/admin/messages.html'); print('msg ok')\""], capture_output=True, timeout=10)
print(r.stdout.decode('utf-8', errors='replace')[:100])

# Verify
r = subprocess.run(ssh + ["python3 -c \"import os; d='/opt/longmarch-dev/001 项目源码/templates/admin/'; print({f:os.path.getsize(d+f) for f in os.listdir(d) if f.endswith('.html')})\""], capture_output=True, timeout=10)
print(r.stdout.decode('utf-8', errors='replace')[:300])
