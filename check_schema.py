import sqlite3
d = sqlite3.connect("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db")
c = d.execute("PRAGMA table_info(route_point)").fetchall()
for r in c:
    print(r)
d.close()
