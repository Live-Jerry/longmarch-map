import shutil, os
src = '/tmp/msg_fixed.html'
dst = '/opt/longmarch-dev/001 项目源码/templates/admin/messages.html'
shutil.copy2(src, dst)
print('copied to', dst[:30])
# Verify
with open(dst) as f:
    line = f.readline()
print('First line:', line.rstrip()[:50])
# Check for IIFE
with open(dst) as f:
    content = f.read()
print('Has IIFE:', '(function()' in content)
print('Has return;: content count:', content.count('return;'))
