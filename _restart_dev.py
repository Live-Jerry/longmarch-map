import subprocess, os

ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

# Build the pattern for the DEV gunicorn startup command
dev_cmd = [
    'cd /opt/longmarch-dev/001项目源码',
    'source ../venv/bin/activate',
    'gunicorn --workers=3 --bind=0.0.0.0:5001 --timeout=60 wsgi:app --daemon --pid=gunicorn.pid'
]

# Kill old gunicorn and start new
full_cmd = 'kill $(cat /opt/longmarch-dev/001项目源码/gunicorn.pid 2>/dev/null) 2>/dev/null; sleep 1; cd "/opt/longmarch-dev/001 项目源码" && ../venv/bin/python3 ../venv/bin/gunicorn --workers=3 --bind=0.0.0.0:5001 --timeout=60 wsgi:app --daemon --pid=gunicorn.pid 2>&1; sleep 2; curl -s -o /dev/null -w "%{http_code}" "http://localhost:5001/"'

# But the path has a space... Let me try a different approach
# Write a restart script on the server
restart_script = '''#!/bin/bash
kill $(cat /opt/longmarch-dev/001项目源码/gunicorn.pid 2>/dev/null) 2>/dev/null
sleep 1
cd /opt/longmarch-dev/001项目源码
source ../venv/bin/activate
nohup gunicorn --workers=3 --bind=0.0.0.0:5001 --timeout=60 wsgi:app --daemon --pid=gunicorn.pid > /dev/null 2>&1 &
sleep 2
curl -s -o /dev/null -w "HTTP %{http_code}\\n" http://localhost:5001/
'''

# Write restart script, scp it, run it
local = r'D:\长征文化\_rs.sh'
with open(local, 'w') as f:
    f.write(restart_script)

subprocess.run(['scp', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', local, 'root@8.133.203.255:/tmp/_rs.sh'], capture_output=True, timeout=10)
r = subprocess.run(ssh + ['chmod +x /tmp/_rs.sh && /tmp/_rs.sh'], capture_output=True, timeout=20)
print(r.stdout.decode())
print('err:', r.stderr.decode()[:200])
