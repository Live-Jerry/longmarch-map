import sqlite3, math

dev_db = "/opt/longmarch-dev/001 \u9879\u76ee\u6e90\u7801/data/longmarch.db"
dev = sqlite3.connect(dev_db)

# For each army, get ordered route_points, and regenerate interpolation points
# Strategy: keep interp count per segment same, recalculate coords as evenly-spaced between corrected nodes

armies = dev.execute("SELECT DISTINCT army FROM route_point ORDER BY army").fetchall()
print(f"Armies: {[a[0] for a in armies]}")

total_updated = 0

for (army,) in armies:
    # Get route_points for this army ordered by order_index
    pts = dev.execute(
        "SELECT id, lat, lng, is_node, node_id, order_index FROM route_point WHERE army = ? ORDER BY order_index",
        (army,)
    ).fetchall()
    
    if not pts or len(pts) < 2:
        continue
    
    # Find segments between consecutive node points
    segments = []
    prev_node_idx = -1
    for i, pt in enumerate(pts):
        if pt[3] == 1:  # is_node
            if prev_node_idx >= 0 and i > prev_node_idx + 1:
                # Interpolation points exist between prev_node and this node
                prev_pt = pts[prev_node_idx]
                interp_count = i - prev_node_idx - 1
                segments.append((prev_pt, pt, interp_count, prev_node_idx + 1, i))
            prev_node_idx = i
    
    if not segments:
        print(f"  Army {army}: no segments with interp points, skipping")
        continue
    
    print(f"  Army {army}: {len(segments)} segments to regenerate")
    
    for seg in segments:
        prev_pt, this_pt, count, start_idx, end_idx = seg
        
        old_lat1, old_lng1 = prev_pt[1], prev_pt[2]
        old_lat2, old_lng2 = this_pt[1], this_pt[2]
        
        # These should already be corrected - double-check with node table
        if prev_pt[4]:  # has node_id
            n = dev.execute("SELECT lat, lng FROM node WHERE node_id = ?", (prev_pt[4],)).fetchone()
            if n:
                old_lat1, old_lng1 = n[0], n[1]
        if this_pt[4]:
            n = dev.execute("SELECT lat, lng FROM node WHERE node_id = ?", (this_pt[4],)).fetchone()
            if n:
                old_lat2, old_lng2 = n[0], n[1]
        
        # Generate evenly-spaced interpolation points between corrected nodes
        for j in range(count):
            idx = start_idx + j
            orig_pt = pts[idx]
            ratio = (j + 1) / (count + 1)
            new_lat = old_lat1 + (old_lat2 - old_lat1) * ratio
            new_lng = old_lng1 + (old_lng2 - old_lng1) * ratio
            
            dev.execute(
                "UPDATE route_point SET lat = ?, lng = ? WHERE id = ?",
                (new_lat, new_lng, orig_pt[0])
            )
            total_updated += 1

dev.commit()
print(f"\nTotal interpolation points regenerated: {total_updated}")

# Verify
for (army,) in armies:
    pts = dev.execute(
        "SELECT id, lat, lng, is_node, order_index FROM route_point WHERE army = ? ORDER BY order_index LIMIT 5",
        (army,)
    ).fetchall()
    if pts:
        print(f"  Army {army} first 5: {[(p[0], round(p[1],4), round(p[2],4), p[3]) for p in pts]}")

dev.close()
