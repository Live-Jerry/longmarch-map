# -*- coding: utf-8 -*-
"""书法碑帖文件资源入库：扫描 002 精选资料 目录的 PDF，写入 resource_link（module_id=4 书法文化）"""
import os, sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC_DIR = r'D:\长征文化\002 项目资源\网盘文件\002 精选资料'
DB_PATH = r'D:\长征文化\009 知常轩\001 项目源码\data\zhichangxuan.db'

def fmt_size(n):
    mb = n / (1024*1024)
    if mb >= 1:
        return '%.1f MB' % mb
    return '%d KB' % (n // 1024)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1. resource_link 加 module_id 列（不存在才加）
cols = [r[1] for r in cur.execute('PRAGMA table_info(resource_link)')]
if 'module_id' not in cols:
    cur.execute('ALTER TABLE resource_link ADD COLUMN module_id INTEGER')
    print('已添加 module_id 列')

# 2. 删除旧的书法碑帖文件记录（category=shufa_pdf 的，避免重复）
cur.execute("DELETE FROM resource_link WHERE category='shufa_pdf'")
print('已清理旧 shufa_pdf 记录')

# 3. 扫描目录插入
files = sorted([f for f in os.listdir(SRC_DIR) if f.lower().endswith('.pdf')])
count = 0
for fname in files:
    fpath = os.path.join(SRC_DIR, fname)
    size = os.path.getsize(fpath)
    title = os.path.splitext(fname)[0]
    url = '/static/shufa/' + fname
    cur.execute('''INSERT INTO resource_link
        (title, category, source, file_size, share_url, access_code, description, status, module_id)
        VALUES (?,?,?,?,?,?,?,?,?)''',
        (title, 'shufa_pdf', fname, fmt_size(size), url, None,
         '书法碑帖 PDF，支持在线预览与下载', 1, 4))
    count += 1
    print('  +', title, fmt_size(size))

conn.commit()
conn.close()
print('共入库 %d 条书法碑帖记录' % count)
