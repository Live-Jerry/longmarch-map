import sqlite3
dev = sqlite3.connect("/opt/longmarch-dev/001 项目源码/data/longmarch.db")
c = dev.execute("PRAGMA table_info(route_point)")
for row in c.fetchall():
    print(row)
dev.close()
