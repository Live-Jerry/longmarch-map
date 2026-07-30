import shutil, os

admin = '/opt/longmarch-dev/001 ÏîÄ¿Ô´Âë/templates/admin/'
pairs = [
    ('/tmp/_idx_new.html', admin + 'index.html'),
    ('/tmp/_nds_new.html', admin + 'nodes.html'),
    ('/tmp/_spr_new.html', admin + 'sparks.html'),
    ('/tmp/_usr_new.html', admin + 'users.html'),
]
for src, dst in pairs:
    shutil.copy2(src, dst)
    print(f'Restored: {dst}')
