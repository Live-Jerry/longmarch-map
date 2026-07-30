import shutil, sys
src = '/tmp/msg_fixed.html'
dst = '/opt/longmarch-dev/001 项目源码/templates/admin/messages.html'
shutil.copy2(src, dst)
print('copied ok')
with open(dst) as f:
    c = f.read()
print('lines:', len(c.split('\n')))
print('has IIFE:', '(function()' in c)
