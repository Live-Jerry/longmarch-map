import subprocess
ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']
r = subprocess.run(ssh + ['python3 /tmp/_deploy.py'], capture_output=True, timeout=15)
print(r.stdout.decode('utf-8', errors='replace'))
