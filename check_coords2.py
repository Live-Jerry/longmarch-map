import sqlite3
dev = sqlite3.connect("/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db")
cur = dev.execute("PRAGMA table_info(node)")
cols = [r[1] for r in cur.fetchall()]
print("node columns:", cols)

# Pick the first 3 string columns as name candidates
cur = dev.execute("SELECT * FROM node LIMIT 1")
row = cur.fetchone()
if row:
    for i, col in enumerate(cols):
        print(f"  {col}: {row[i]}")
dev.close()
