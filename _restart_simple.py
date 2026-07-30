import subprocess, time

ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

# Write restart script on server
restart = 'os.system("pkill -f gunicorn.*5001; sleep 1; cd /opt/longmarch-dev/001项目源码/.. && cd 001项目源码 && nohup ../venv/bin/gunicorn --workers=3 --bind=0.0.0.0:5001 --timeout=60 wsgi:app --daemon --pid=gunicorn.pid > /dev/null 2>&1 &")'
cmd = f'python3 -c "import os; {restart}; import time; time.sleep(2); print(\\\"done\\\")"'
r = subprocess.run(ssh + [cmd], capture_output=True, timeout=20)
print('out:', r.stdout.decode()[:200])
print('err:', r.stderr.decode()[:200])
