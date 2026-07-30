import sqlite3

DB = "/opt/longmarch-dev/001 项目源码/data/longmarch.db"

# JSON original coordinates for waypoints that got wrong node_id matches
# These waypoints are not actual nodes; restore JSON coords and node_id=NULL
RESTORE = {
    # Army 4: 若尔盖 and 巴西 are intermediate waypoints, not nodes
    4: {
        "若尔盖": (33.58, 102.96),   # JSON: 33.58, 102.96
        "巴西":   (34.07, 103.44),   # JSON: 34.07, 103.44
    },
    # Army 1: 班佑 is intermediate, not a node
    1: {
        "班佑": (33.62, 103.15),     # JSON: 33.62, 103.15
    }
}

conn = sqlite3.connect(DB)
c = conn.cursor()

for army, fixmap in RESTORE.items():
    for name, (lat, lng) in fixmap.items():
        c.execute(
            "UPDATE route_point SET node_id=NULL, lat=?, lng=? WHERE army=? AND name=?", 
            (lat, lng, army, name)
        )
        print(f"  Army {army}: '{name}' restored to ({lat}, {lng}), node_id cleared")

conn.commit()

# Verify
print("\n=== Verification ===")
for army in [1, 4]:
    c.execute("SELECT id, name, node_id, lat, lng FROM route_point WHERE army=? AND (name='若尔盖' OR name='巴西' OR name='班佑')", (army,))
    for r in c.fetchall():
        print(f"  Army {army}: {r[1]:8} node={r[2]} ({r[3]:.3f},{r[4]:.3f})")

conn.close()
print("Done")
