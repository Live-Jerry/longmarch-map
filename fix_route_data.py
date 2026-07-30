# Fix route_point data: insert missing nodes and correct coordinates
# Uses node table as authoritative coordinate source

import sqlite3
import sys

DB_PATH = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Get all node coordinates (authoritative)
    c.execute("SELECT node_id, lat, lng, army FROM node WHERE node_id NOT IN ('99.99')")
    node_map = {}  # node_id -> (lat, lng, army)
    for row in c.fetchall():
        node_map[row[0]] = (row[1], row[2], row[3])
    
    print(f"Loaded {len(node_map)} nodes from node table")
    
    # 2. Get all route_point entries
    c.execute("SELECT id, node_id, name, lat, lng, army, order_index, is_node FROM route_point ORDER BY army, order_index")
    route_points = c.fetchall()
    
    # 3. Check which nodes are missing vs present
    present_nodes = {}  # army -> set of node_ids
    for rp in route_points:
        army = rp[5]
        nid = rp[1]
        if nid:
            if army not in present_nodes:
                present_nodes[army] = set()
            present_nodes[army].add(nid)
    
    # 4. Build army->node mapping from node table
    army_node_map = {}  # army_num -> [(node_id, lat, lng)]
    army_name_to_num = {
        "中央红军": 1,
        "红二方面军": 2,
        "红四方面军": 4,
        "红25军": 25,
    }
    for nid, (lat, lng, aname) in node_map.items():
        a_num = army_name_to_num.get(aname)
        if a_num:
            if a_num not in army_node_map:
                army_node_map[a_num] = []
            army_node_map[a_num].append((nid, lat, lng))
    
    # 5. For each army, find nodes that should be in route_point but aren't
    for a_num in [1, 2, 4, 25]:
        p = present_nodes.get(a_num, set())
        missing = [(nid, lat, lng) for (nid, lat, lng) in army_node_map.get(a_num, []) if nid not in p]
        present = [(nid, lat, lng) for (nid, lat, lng) in army_node_map.get(a_num, []) if nid in p]
        
        if missing:
            print(f"\nArmy {a_num}: {len(missing)} missing node(s):")
            for nid, lat, lng in sorted(missing):
                print(f"  {nid} ({lat}, {lng})")
            
            # Get existing route_points for this army to find insertion position
            army_rps = [rp for rp in route_points if rp[5] == a_num]
            if army_rps:
                last_idx = max(rp[6] for rp in army_rps)
            else:
                last_idx = 0
            
            for nid, lat, lng in missing:
                last_idx += 1
                # Find name and title from node table
                c.execute("SELECT title, location FROM node WHERE node_id = ?", (nid,))
                nr = c.fetchone()
                name = (nr[0] or nr[1] or nid) if nr else nid
                # Trim name to reasonable length
                name = name[:30]
                
                print(f"  >> Inserting: idx={last_idx}, name={name}, ({lat}, {lng})")
                c.execute(
                    "INSERT INTO route_point (army, lat, lng, order_index, is_node, node_id, name) VALUES (?, ?, ?, ?, 1, ?, ?)",
                    (a_num, lat, lng, last_idx, nid, name)
                )
    
    # 6. Fix coordinate mismatches: for route_point entries with node_id, update coords from node table
    fixes = 0
    for rp in route_points:
        rp_id, nid, rp_name, rp_lat, rp_lng, rp_army, rp_idx, rp_is_node = rp
        if nid and nid in node_map:
            n_lat, n_lng, _ = node_map[nid]
            if abs(rp_lat - n_lat) > 0.001 or abs(rp_lng - n_lng) > 0.001:
                print(f"  Fix coords: {nid} ({rp_name}) route_point ({rp_lat},{rp_lng}) -> node ({n_lat},{n_lng})")
                c.execute("UPDATE route_point SET lat=?, lng=? WHERE id=?", (n_lat, n_lng, rp_id))
                fixes += 1
    
    if fixes:
        print(f"\nFixed {fixes} coordinate mismatches")
    
    conn.commit()
    conn.close()
    print("\nDone. Check autowalk on dev.zhichangxuan.com")

if __name__ == "__main__":
    main()
