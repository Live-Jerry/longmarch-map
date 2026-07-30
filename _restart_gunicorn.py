import subprocess

ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

# Find gunicorn PID
r = subprocess.run(ssh + ['ps aux | grep gunicorn | grep -v grep | head -3'], capture_output=True, timeout=10)
print(r.stdout.decode())

# Restart with SIGHUP to master
r2 = subprocess.run(ssh + ['pkill -HUP -f "gunicorn.*5001" 2>/dev/null; sleep 2; curl -s -o /dev/null -w "%{http_code}" "http://localhost:5001/admin/messages"'], capture_output=True, timeout=15)
print(f'HTTP status: {r2.stdout.decode().strip()}')
print(f'stderr: {r2.stderr.decode().strip()}')
