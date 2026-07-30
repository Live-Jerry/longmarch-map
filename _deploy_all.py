import shutil, os

admin = '/opt/longmarch-dev/001 项目源码/templates/admin/'

# Copy msg  
shutil.copy2('/tmp/_msg_fix.html', admin + 'messages.html')
print('messages.html deployed')

# Verify all files have content  
for f in ['index.html', 'nodes.html', 'sparks.html', 'users.html', 'messages.html', 'base.html']:
    path = admin + f
    size = os.path.getsize(path)
    has_extend = 'extends' in open(path).read()
    print(f'{f}: {size} bytes, extends={has_extend}')
