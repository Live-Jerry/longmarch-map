"""
长征路线数据导入工具
用法: python3 import_routes.py <json文件路径>
从 JSON 文件导入路线数据到数据库，更新节点坐标、标题、路线途经点。
"""
import json, sqlite3, sys, os

ARMY_MAP = {'hongyifang':1, 'hongershi':2, 'hongsifang':4, 'hongershiwu':25}

# 节点映射表: (json段名, 途经点名, 出现次序, 数据库节点ID, 节点标题)
# 次序=0 代表第一次出现，=1 代表第二次，以此类推
NODE_MAP = [
    # 中央红军
    ('hongyifang', '瑞金',     0, '1.1',  '瑞金'),
    ('hongyifang', '长汀',     0, '1.2',  '长汀'),
    ('hongyifang', '于都',     0, '1.3',  '于都'),
    ('hongyifang', '道县',     0, '2.1',  '道县'),
    ('hongyifang', '通道',     0, '3.1',  '通道'),
    ('hongyifang', '黎平',     0, '4.1',  '黎平'),
    ('hongyifang', '瓮安',     0, '4.2',  '瓮安'),
    ('hongyifang', '遵义',     0, '4.3',  '遵义'),
    ('hongyifang', '赤水',     0, '5.1',  '赤水'),
    ('hongyifang', '扎西',     0, '4.4',  '扎西'),
    ('hongyifang', '苟坝',     0, '4.5',  '苟坝'),
    ('hongyifang', '皎平渡',    0, '6.1',  '皎平渡'),
    ('hongyifang', '安顺场',    0, '7.1',  '安顺场'),
    ('hongyifang', '泸定',     0, '7.2',  '泸定'),
    ('hongyifang', '宝兴',     0, '8.1',  '宝兴'),
    ('hongyifang', '达维',     0, '9.1',  '达维'),
    ('hongyifang', '两河口',    0, '9.2',  '两河口'),
    ('hongyifang', '卓克基',    0, 'S5.1', '卓克基'),
    ('hongyifang', '芦花',     0, '9.3',  '芦花'),
    ('hongyifang', '毛儿盖',    0, '10.1', '毛儿盖'),
    ('hongyifang', '松潘',     0, '10.2', '松潘'),
    ('hongyifang', '巴西',     0, '10.3', '巴西'),
    ('hongyifang', '俄界',     0, '11.1', '俄界'),
    ('hongyifang', '腊子口',    0, '11.2', '腊子口'),
    ('hongyifang', '哈达铺',    0, '11.3', '哈达铺'),
    ('hongyifang', '通渭',     0, '11.4', '通渭'),
    ('hongyifang', '六盘山',    0, '12.1', '六盘山'),
    ('hongyifang', '吴起镇',    0, '13.1', '吴起镇'),
    # 红二方面军
    ('hongershi', '桑植',     0, 'E1.1', '桑植'),
    ('hongershi', '石阡',     0, 'E2.1', '石阡'),
    ('hongershi', '黔西',     0, 'E3.1', '黔西'),
    ('hongershi', '盘县',     0, 'E4.1', '盘县'),
    ('hongershi', '中甸',     0, 'E5.1', '中甸'),
    ('hongershi', '甘孜',     0, 'E5.2', '甘孜'),
    ('hongershi', '绥靖',     0, 'S6.2', '绥靖'),
    ('hongershi', '阿坝',     0, 'E6.1', '阿坝'),
    ('hongershi', '岷县',     0, 'E6.2', '岷县'),
    ('hongershi', '会宁',     0, 'E7.1', '会宁'),
    ('hongershi', '将台堡',    0, 'E7.2', '将台堡'),
    # 红四方面军
    ('hongsifang', '苍溪',    0, 'S1.1', '苍溪'),
    ('hongsifang', '茂县',    0, 'S2.1', '茂县'),
    ('hongsifang', '懋功',    0, 'S3.1', '懋功'),
    ('hongsifang', '两河口',   0, 'S4.1', '两河口'),
    ('hongsifang', '芦花',    0, '9.3',  '芦花'),
    ('hongsifang', '绥靖',    0, 'S6.2', '绥靖'),
    ('hongsifang', '甘孜',    0, 'S7.2', '甘孜'),
    ('hongsifang', '岷县',    0, 'S8.1', '岷县'),
    ('hongsifang', '会宁',    0, 'S8.2', '会宁'),
    # 红二十五军
    ('hongershiwu', '何家冲',   0, 'H1.1', '何家冲'),
    ('hongershiwu', '独树镇',   0, 'H2.1', '独树镇'),
    ('hongershiwu', '庾家河',   0, 'H3.1', '庾家河'),
    ('hongershiwu', '葛牌',    0, 'H4.1', '葛牌'),
    ('hongershiwu', '沣峪口',   0, 'H5.1', '沣峪口'),
    ('hongershiwu', '泾川',    0, 'H6.1', '泾川'),
    ('hongershiwu', '延川永坪镇', 0, 'H6.2', '永坪镇'),
]

# 不在 JSON 途经点中但需要从其他路线同步坐标的节点
EXTRA_NODES = [
    ('14.1', '会宁', 'hongsifang', '会宁', 0),  # 从红四方面军取坐标
    ('14.2', '将台堡', 'hongershi', '将台堡', 0),
]

# 节点军队归属（覆盖默认'中央红军'）
ARMY_ASSIGN = {
    '14.1': '红四方面军',
    '14.2': '红二方面军',
    'E7.1': '红四方面军',  # V1.6 红二不再经会宁
}

DB_DIRS = [
    '/opt/longmarch-dev/001 项目源码/data',
    '/opt/longmarch/001 项目源码/data',
    '001 项目源码/data',
    'data',
]

def find_waypoint(data, army_key, name, occurrence):
    """在 JSON 数据中查找指定次序的同名途经点"""
    count = 0
    for wp in data['routes'][army_key]['waypoints']:
        if wp['name'] == name:
            if count == occurrence:
                return wp
            count += 1
    return None


def build_route_point_lookup():
    """构建 (army_key, name, occurrence) -> node_id 字典"""
    lookup = {}
    for army_key, wp_name, occ, node_id, _ in NODE_MAP:
        lookup[(army_key, wp_name, occ)] = node_id
    return lookup


def import_data(json_path, db_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    db = sqlite3.connect(db_path)
    cur = db.cursor()

    # 检查 route_point 表结构
    cols = {r[1] for r in cur.execute('PRAGMA table_info(route_point)').fetchall()}
    has_name = 'name' in cols

    # 第一步：更新节点坐标和标题
    print('=== 更新节点坐标和标题 ===')
    updated_nodes = 0
    for army_key, wp_name, occ, node_id, new_title in NODE_MAP:
        wp = find_waypoint(data, army_key, wp_name, occ)
        if not wp:
            print(f'  警告: [{army_key}] {wp_name} 第{occ+1}次出现未找到')
            continue
        cur.execute('UPDATE node SET title=?, lat=?, lng=? WHERE node_id=?',
                    (new_title, wp['lat'], wp['lng'], node_id))
        if cur.rowcount > 0:
            print(f'  {node_id:6s} {wp_name:12s} ({wp["lat"]:.4f}, {wp["lng"]:.4f})')
            updated_nodes += 1
        else:
            print(f'  错误: 节点 {node_id} 在数据库中不存在')

    # 更新额外节点（不在路线途经点中的独立节点）
    for node_id, title, army_key, wp_name, occ in EXTRA_NODES:
        wp = find_waypoint(data, army_key, wp_name, occ)
        if wp:
            cur.execute('UPDATE node SET title=?, lat=?, lng=? WHERE node_id=?',
                        (title, wp['lat'], wp['lng'], node_id))
            if cur.rowcount > 0:
                print(f'  {node_id:6s} {wp_name:12s} ({wp["lat"]:.4f}, {wp["lng"]:.4f}) [额外]')
                updated_nodes += 1

    # 设置节点军队归属
    for nid, a in ARMY_ASSIGN.items():
        cur.execute('UPDATE node SET army=? WHERE node_id=?', (a, nid))

    print(f'  共更新 {updated_nodes} 个节点')
    db.commit()

    # 第二步：重建路线途经点
    print()
    print('=== 重建路线途经点 ===')
    cur.execute('DELETE FROM route_point')
    route_point_lookup = build_route_point_lookup()
    total_points = 0

    for army_key, army_data in data['routes'].items():
        army_num = ARMY_MAP[army_key]
        occ_counter = {}

        for i, wp in enumerate(army_data['waypoints']):
            wp_name = wp['name']
            occ = occ_counter.get(wp_name, 0)
            occ_counter[wp_name] = occ + 1

            node_id = route_point_lookup.get((army_key, wp_name, occ))

            if has_name:
                cur.execute(
                    'INSERT INTO route_point (army, stage, lat, lng, order_index, is_node, node_id, name) VALUES (?,?,?,?,?,?,?,?)',
                    (army_num, '', wp['lat'], wp['lng'], i, 1 if node_id else 0, node_id, wp_name)
                )
            else:
                cur.execute(
                    'INSERT INTO route_point (army, stage, lat, lng, order_index, is_node, node_id) VALUES (?,?,?,?,?,?,?)',
                    (army_num, '', wp['lat'], wp['lng'], i, 1 if node_id else 0, node_id)
                )
            total_points += 1

        print(f'  {army_data["name"]}: {len(army_data["waypoints"])} 个途经点')

    # 额外节点也加入路线（如果是会宁/将台堡这类总节点）
    for node_id, title, army_key, wp_name, occ in EXTRA_NODES:
        wp = find_waypoint(data, army_key, wp_name, occ)
        if wp:
            army_num = ARMY_MAP[army_key]
            # 找到该途经点在路线中的位置，更新其 node_id
            cur.execute('UPDATE route_point SET node_id=? WHERE army=? AND name=? AND node_id IS NULL',
                        (node_id, army_num, wp_name))

    db.commit()
    print(f'  共 {total_points} 个途经点')

    # 第三步：验证
    print()
    print('=== 验证 ===')
    for a in [1, 2, 4, 25]:
        n = cur.execute('SELECT COUNT(*) FROM route_point WHERE army=?', (a,)).fetchone()[0]
        nn = cur.execute('SELECT COUNT(*) FROM route_point WHERE army=? AND node_id IS NOT NULL', (a,)).fetchone()[0]
        name_count = 0
        if has_name:
            name_count = cur.execute('SELECT COUNT(*) FROM route_point WHERE army=? AND name IS NOT NULL AND name!=""', (a,)).fetchone()[0]
            print(f'  Army {a}: {n} 个途经点 ({nn} 个绑定节点, {name_count} 个有名称)')
        else:
            print(f'  Army {a}: {n} 个途经点 ({nn} 个绑定节点)')

    db.close()
    print()
    print('完成。')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python3 import_routes.py <JSON文件路径>')
        sys.exit(1)

    json_path = sys.argv[1]
    if not os.path.isfile(json_path):
        print(f'错误: 文件 {json_path} 不存在')
        sys.exit(1)

    # 查找数据库
    db_path = None
    for d in DB_DIRS:
        p = os.path.join(d, 'longmarch.db')
        if os.path.isfile(p):
            db_path = p
            break

    if not db_path:
        print('错误: 找不到数据库文件 longmarch.db')
        sys.exit(1)

    print(f'JSON: {json_path}')
    print(f'数据库: {db_path}')
    import_data(json_path, db_path)
