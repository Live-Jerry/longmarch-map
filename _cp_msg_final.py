import shutil
shutil.copy('/tmp/_msg3.html', '/opt/longmarch-dev/001 项目源码/templates/admin/messages.html')
print('copied')
with open('/opt/longmarch-dev/001 项目源码/templates/admin/messages.html') as f:
    c = f.read()
print('has emoji:', '📊' in c)
