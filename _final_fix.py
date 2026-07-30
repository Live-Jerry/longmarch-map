import subprocess, time

# Write restart script
script = '''
import subprocess, time, os

# Copy the fixed messages file
import shutil
shutil.copy('/tmp/msg_fixed.html', '/opt/longmarch-dev/001 项目源码/templates/admin/messages.html')

# Kill old gunicorn
subprocess.run(['pkill', '-f', 'gunicorn.*:5001'], capture_output=True, timeout=5)
time.sleep(1)

# Verify old is dead
result = subprocess.run(['pgrep', '-f', 'gunicorn.*:5001'], capture_output=True, timeout=5)
print(f'old pids: {result.stdout.decode().strip()}')

# Start new gunicorn
proc = subprocess.Popen(
    ['../venv/bin/gunicorn', '--workers=3', '--bind=0.0.0.0:5001',
     '--timeout=60', 'wsgi:app', '--daemon', '--pid=gunicorn.pid'],
    cwd='/opt/longmarch-dev/001 项目源码',
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(2)

# Test
import urllib.request
try:
    r = urllib.request.urlopen('http://localhost:5001/admin/messages', timeout=5)
    print(f'HTTP {r.status}')
    content = r.read().decode('utf-8')
    print(f'length: {len(content)}')
    print(f'has IIFE: {"(function()" in content}')
    print(f'has return; outside: {"return;" in content}')
except Exception as e:
    print(f'error: {e}')
'''

with open(r'D:\长征文化\_server_restart.py', 'w') as f:
    f.write(script)

import os
subprocess.run(['scp', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', r'D:\长征文化\_server_restart.py', 'root@8.133.203.255:/tmp/_srv.py'], capture_output=True, timeout=10)

ssh_cmd = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']
r = subprocess.run(ssh_cmd + ['python3 /tmp/_srv.py'], capture_output=True, timeout=30)
print(r.stdout.decode(errors='replace'))
print('err:', r.stderr.decode(errors='replace')[:500])
