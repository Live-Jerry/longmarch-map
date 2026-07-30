import shutil, os

files = {
    '/tmp/_base.html': '/opt/longmarch-dev/001 项目源码/templates/admin/base.html',
    '/tmp/_index.html': '/opt/longmarch-dev/001 项目源码/templates/admin/index.html',
    '/tmp/_nodes.html': '/opt/longmarch-dev/001 项目源码/templates/admin/nodes.html',
    '/tmp/_sparks.html': '/opt/longmarch-dev/001 项目源码/templates/admin/sparks.html',
    '/tmp/_users.html': '/opt/longmarch-dev/001 项目源码/templates/admin/users.html',
    '/tmp/_messages.html': '/opt/longmarch-dev/001 项目源码/templates/admin/messages.html',
}

for src, dst in files.items():
    if os.path.exists(src):
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        print(f'copied {src} -> {dst} ({size} bytes)')
    else:
        print(f'MISSING: {src}')
