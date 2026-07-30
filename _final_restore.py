import shutil, os

# Restore original admin templates
admin = '/opt/longmarch-dev/001 项目源码/templates/admin/'

# First restore originals
shutil.copy2('/tmp/_idx.html', admin + 'index.html')
print('index restored', os.path.getsize(admin + 'index.html'))

shutil.copy2('/tmp/_nds.html', admin + 'nodes.html')
print('nodes restored', os.path.getsize(admin + 'nodes.html'))

shutil.copy2('/tmp/_spr.html', admin + 'sparks.html')
print('sparks restored', os.path.getsize(admin + 'sparks.html'))

shutil.copy2('/tmp/_usr.html', admin + 'users.html')
print('users restored', os.path.getsize(admin + 'users.html'))

# Now deploy base.html (extends base template)
shutil.copy2('/tmp/_base.html', admin + 'base.html')
print('base deployed', os.path.getsize(admin + 'base.html'))

# Now deploy messages.html (extends base.html with correct JS)
shutil.copy2('/tmp/_msg.html', admin + 'messages.html')
print('messages deployed', os.path.getsize(admin + 'messages.html'))

# Verify no extends in originals, yes extends in messages
for f in ['index.html', 'nodes.html', 'sparks.html', 'users.html']:
    c = open(admin + f).read()
    has = 'extends' in c
    print(f'{f}: has extends={has}, size={os.path.getsize(admin+f)}')

for f in ['messages.html', 'base.html']:
    c = open(admin + f).read()
    has = 'extends' in c
    print(f'{f}: has extends={has}, size={os.path.getsize(admin+f)}')
