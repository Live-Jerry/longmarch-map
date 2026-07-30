import subprocess

ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

# Kill old and restart
r = subprocess.run(ssh + ['''kill $(cat "/opt/longmarch-dev/001 项目源码/gunicorn.pid") 2>/dev/null; sleep 1; cd "/opt/longmarch-dev/001 项目源码" && ../venv/bin/gunicorn --workers=3 --bind=0.0.0.0:5001 --timeout=60 wsgi:app --daemon --pid=gunicorn.pid 2>&1; sleep 2; curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:5001/"'''], capture_output=True, timeout=20)
print('out:', r.stdout.decode())
print('err:', r.stderr.decode()[:200])
