import subprocess
ssh = ['ssh', '-i', r'C:\Users\RP Conference\.ssh\longmarch_ecs', '-o', 'StrictHostKeyChecking=no', 'root@8.133.203.255']

# Read the temp file and cp it properly
# Use Python on the server to copy
cmd = '''python3 -c "
import shutil
shutil.copy('/tmp/msg_fixed.html', '/opt/longmarch-dev/001 项目源码/templates/admin/messages.html')
print('copied')
"'''
r = subprocess.run(ssh + [cmd], capture_output=True, timeout=10)
print(r.stdout.decode())
print(r.stderr.decode())
