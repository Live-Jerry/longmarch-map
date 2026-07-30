import sqlite3
db = sqlite3.connect('001 项目源码/data/longmarch.db')
cur = db.cursor()

cur.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)

if 'route_point' in tables:
    cur.execute('PRAGMA table_info(route_point)')
    cols = [(r[1], r[2]) for r in cur.fetchall()]
    print('route_point columns:', cols)
    
    cur.execute('SELECT COUNT(*) FROM route_point')
    print('Total route points:', cur.fetchone()[0])
    
    cur.execute('SELECT * FROM route_point LIMIT 10')
    for r in cur.fetchall():
        print(r)
    
    # Check for title/name column
    if any('title' in c[0] or 'name' in c[0] for c in cols):
        cur.execute('SELECT COUNT(*) FROM route_point WHERE title IS NOT NULL AND title != ""')
        print('Points with title:', cur.fetchone()[0])
    else:
        print('No title/name column in route_point')
db.close()
