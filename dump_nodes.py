import sqlite3, json

# Local node table
local = sqlite3.connect("D:/长征文化/001 项目源码/data/longmarch.db")
rows = local.execute("SELECT node_id, title, lat, lng FROM node WHERE title != 'Test' ORDER BY node_id").fetchall()
local.close()

for r in rows:
    print("%6s  %-30s (%.5f, %.5f)" % (r[0], r[1], r[2], r[3]))
print()

# Also dump server node table to compare
import subprocess, os
key_path = os.path.expanduser("~/.ssh/longmarch_ecs")
result = subprocess.run(
    ["ssh", "-i", key_path, "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10",
     "root@8.133.203.255",
     "sqlite3 '/opt/longmarch-dev/001 项目源码/data/longmarch.db' \"SELECT node_id, title, lat, lng FROM node WHERE title != 'Test' ORDER BY node_id\""],
    capture_output=True, text=True, timeout=20
)
if result.returncode == 0:
    print("=== DEV SERVER NODES ===")
    print(result.stdout[:3000])
else:
    print("SSH failed:", result.stderr[:500])
