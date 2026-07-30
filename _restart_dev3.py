import os, subprocess, time

# Find DEV gunicorn master PID using PowerShell
pid_cmd = "powershell -Command \"ssh -i 'C:\\Users\\RP Conference\\.ssh\\longmarch_ecs' -o StrictHostKeyChecking=no root@8.133.203.255 'cat /opt/longmarch-dev/001项目源码/gunicorn.pid'\""
r = subprocess.run(pid_cmd, capture_output=True, timeout=10, shell=True)
pid = r.stdout.decode().strip()
print(f'DEV gunicorn PID: {pid}')

# Kill it
kill_cmd = f"ssh -i 'C:\\Users\\RP Conference\\.ssh\\longmarch_ecs' root@8.133.203.255 'kill {pid}; sleep 0.5'"
subprocess.run(kill_cmd, capture_output=True, timeout=10, shell=True)

# Verify killed
r2 = subprocess.run(pid_cmd, capture_output=True, timeout=10, shell=True)
print(f'After kill, PID file: {r2.stdout.decode().strip()[:50] if r2.stdout else "empty"}')

# Deploy msg file first
subprocess.run([
    'ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no',
    'root@8.133.203.255',
    'cp /tmp/_dm.py /tmp/_deploy2.py'
], capture_output=True, timeout=10)

# Write restart script on server  
restart_py = '''import subprocess, time
# Kill old gunicorn
subprocess.run(['pkill', '-f', 'gunicorn.*5001'], capture_output=True, timeout=5)
time.sleep(1)
# Start new
proc = subprocess.Popen(
    ['../venv/bin/gunicorn', '--workers=3', '--bind=0.0.0.0:5001', 
     '--timeout=60', 'wsgi:app', '--daemon', '--pid=gunicorn.pid'],
    cwd='/opt/longmarch-dev/001 项目源码'
)
time.sleep(2)
print('started, pid:', proc.pid)
import urllib.request
try:
    r = urllib.request.urlopen('http://localhost:5001/')
    print('HTTP:', r.status)
except Exception as e:
    print('error:', e)
'''

with open(r'D:\长征文化\_rs_py.py', 'w') as f:
    f.write(restart_py)

subprocess.run(['scp', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', r'D:\长征文化\_rs_py.py', 'root@8.133.203.255:/tmp/_restart.py'], capture_output=True, timeout=10)

r3 = subprocess.run([
    'ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no',
    'root@8.133.203.255', 'python3 /tmp/_restart.py'
], capture_output=True, timeout=20)
print('restart output:', r3.stdout.decode())
print('restart err:', r3.stderr.decode()[:200])
