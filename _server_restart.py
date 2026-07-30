
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
