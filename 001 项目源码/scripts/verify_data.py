#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证脚本 - 检查 node_data.json 和数据库完整性

用法: python3 scripts/verify_data.py
"""

import json
import sqlite3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config

# =============================================================================
# 必填字段
# =============================================================================
REQUIRED_FIELDS = [
    "node_id", "title", "location", "lat", "lng", "time",
    "army", "famous_battle", "important_meeting",
    "history_event", "core_site", "poem_article", "typical_story",
    "typical_people", "historical_significance"
]

ACTIVE_SECTIONS_FIELDS = [
    "famous_battle", "important_meeting", "history_event",
    "core_site", "poem_article", "typical_story",
    "typical_people", "historical_significance"
]

EXPECTED_ARMIES = {
    "中央红军": (29, "1.1-14.2"),
    "红二方面军": (10, "E1.1-E7.2"),
    "红四方面军": (11, "S1.1-S8.2"),
    "红25军": (7, "H1.1-H6.2"),
}

ALLOWED_ARMIES = set(EXPECTED_ARMIES.keys())

errors = []
warnings = []


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  [FAIL] {msg}")
    else:
        print(f"  [OK] {msg}")


def warn(condition, msg):
    if not condition:
        warnings.append(msg)
        print(f"  [WARN]  {msg}")
    else:
        print(f"  [OK] {msg}")


print("=" * 60)
print(" 验证 node_data.json")
print("=" * 60)

json_path = config.NODE_DATA_JSON
with open(json_path, "r", encoding="utf-8") as f:
    all_nodes = json.load(f)

print(f"\n总节点数: {len(all_nodes)}")

# ---- 1. 检查必填字段 ----
print("\n[1] 检查必填字段...")
for node in all_nodes:
    nid = node.get("node_id", "?")
    for field in REQUIRED_FIELDS:
        check(
            field in node,
            f"节点 {nid} 缺少必填字段: {field}"
        )

# ---- 2. 检查 army 归属 ----
print("\n[2] 检查 army 字段...")
from collections import Counter
army_counts = Counter(n["army"] for n in all_nodes)
for army, expected in EXPECTED_ARMIES.items():
    actual = army_counts.get(army, 0)
    warn(
        actual == expected[0],
        f"{army} 应有 {expected[0]} 个节点 (ID范围 {expected[1]})，实际 {actual} 个"
    )

for army in army_counts:
    check(army in ALLOWED_ARMIES, f"army 值 '{army}' 在允许范围内")

# ---- 3. 检查 node_id 命名规范 ----
print("\n[3] 检查 node_id 命名规范...")
for node in all_nodes:
    nid = node["node_id"]
    army = node.get("army", "")
    if army == "中央红军":
        check(
            "." in nid and nid[0].isdigit(),
            f"中央红军 node_id 应为数字格式 (如 1.1): {nid}"
        )
    elif army == "红二方面军":
        check(
            nid.startswith("E") and "." in nid,
            f"红二方面军 node_id 应以 E 开头: {nid}"
        )
    elif army == "红四方面军":
        check(
            nid.startswith("S") and "." in nid,
            f"红四方面军 node_id 应以 S 开头: {nid}"
        )
    elif army == "红25军":
        check(
            nid.startswith("H") and "." in nid,
            f"红25军 node_id 应以 H 开头: {nid}"
        )

# ---- 4. 检查标题和坐标完整性 ----
print("\n[4] 检查标题和坐标...")
for node in all_nodes:
    nid = node["node_id"]
    check(
        isinstance(node.get("lat"), (int, float)) and abs(node["lat"]) < 90,
        f"节点 {nid} 纬度异常: {node.get('lat')}"
    )
    check(
        isinstance(node.get("lng"), (int, float)) and abs(node["lng"]) < 180,
        f"节点 {nid} 经度异常: {node.get('lng')}"
    )
    title = node.get("title", "")
    check(len(title) > 0, f"节点 {nid} 标题为空")

# ---- 5. 检查 XML/JSON 格式完整性 ----
print("\n[5] 检查 JSON 格式完整性...")
check(isinstance(all_nodes, list), "根节点应为列表")
check(len(all_nodes) > 0, "列表不为空")
check(len(all_nodes) == sum(army_counts.values()), "总节点数等于各军之和")

# ---- 6. 检查 active_sections 正确性 ----
print("\n[6] 检查 active_sections（可选）...")
for node in all_nodes:
    nid = node["node_id"]
    sections = node.get("active_sections", [])
    if sections:
        # 检查 time 和 historical_significance 是否在 sections 中
        has_time = "time" in sections
        has_significance = "historical_significance" in sections
        if not has_significance:
            warn(
                False,
                f"节点 {nid} 的 active_sections 缺少 historical_significance"
            )

# ---- 7. 检查数据库 ----
print("\n[7] 验证数据库...")
db_path = config.DATABASE_PATH
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM node")
    db_count = cursor.fetchone()[0]
    check(db_count >= len(all_nodes), f"数据库应有 >= {len(all_nodes)} 条，实际 {db_count} 条")

    cursor.execute("SELECT army, COUNT(*) FROM node GROUP BY army ORDER BY army")
    db_army = cursor.fetchall()
    print(f"  数据库按军队统计:")
    for army, cnt in db_army:
        print(f"    {army}: {cnt}")

    cursor.execute("SELECT sql FROM sqlite_master WHERE name='node' AND type='table'")
    create_sql = cursor.fetchone()[0]
    has_army_col = "army" in (create_sql or "")
    check(has_army_col, "数据库表 node 包含 army 列")

    cursor.execute("PRAGMA table_info(node)")
    db_cols = [r[1] for r in cursor.fetchall()]
    for field in REQUIRED_FIELDS:
        check(field in db_cols, f"数据库表包含 {field} 列")

    conn.close()
else:
    print("  [WARN]  数据库文件不存在，跳过数据库验证")

# =============================================================================
# 最终统计
# =============================================================================
print("\n" + "=" * 60)
print(" 验证结果")
print("=" * 60)
print(f"\n总节点: {len(all_nodes)}")
for army, cnt in sorted(army_counts.items()):
    print(f"  {army}: {cnt} 个节点")

print(f"\n错误: {len(errors)}")
for e in errors:
    print(f"  [FAIL] {e}")
print(f"警告: {len(warnings)}")
for w in warnings:
    print(f"  [WARN]  {w}")

if errors:
    print("\n[FAIL] 验证未通过，请修复以上错误")
    sys.exit(1)
else:
    print("\n[OK] 验证通过！")

# 输出摘要 JSON
summary = {
    "total_nodes": len(all_nodes),
    "army_counts": dict(army_counts),
    "errors": len(errors),
    "warnings": len(warnings)
}
summary_path = os.path.join(os.path.dirname(json_path), "verify_summary.json")
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print(f"摘要已写入: {summary_path}")
