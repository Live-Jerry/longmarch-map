import subprocess

src = r'D:\长征文化\001 项目源码\static\js\nodes.js'
r = subprocess.run(['scp', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', src, 'root@8.133.203.255:/tmp/nodes_fix.js'], capture_output=True, timeout=10)
print('scp:', 'OK' if r.returncode == 0 else 'FAIL')
if r.returncode != 0:
    print(r.stderr.decode('utf-8', errors='replace')[:200])

# Copy to DEV static dir via python on server
ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']
r2 = subprocess.run(ssh + ['python3 -c "import shutil; shutil.copy2(\'/tmp/nodes_fix.js\', \'/opt/longmarch-dev/001 项目源码/static/js/nodes.js\'); print(\'copied\')"'], capture_output=True, timeout=10)
print(r2.stdout.decode('utf-8', errors='replace')[:200])

# Verify
r3 = subprocess.run(ssh + ['grep "initVoices" "/opt/longmarch-dev/001 项目源码/static/js/nodes.js"'], capture_output=True, timeout=10)
print('has initVoices:', r3.stdout.decode()[:20] if r3.stdout else 'NO')
r4 = subprocess.run(ssh + ['grep "primeSpeechEngine" "/opt/longmarch-dev/001 项目源码/static/js/nodes.js"'], capture_output=True, timeout=10)
print('has primeSpeechEngine:', r4.stdout.decode()[:20] if r4.stdout else 'NO')
