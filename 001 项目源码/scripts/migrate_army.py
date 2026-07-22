#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 为 node 表添加 army 字段并导入新节点数据

用法:
    python3 scripts/migrate_army.py          # 执行迁移
    python3 scripts/migrate_army.py --check  # 仅检查状态
"""

import sqlite3
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def check_db():
    """检查数据库当前状态"""
    db_path = config.DATABASE_PATH
    if not os.path.exists(db_path):
        print(f"[ERR] 数据库文件不存在: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查是否有 army 列
    cursor.execute("PRAGMA table_info(node)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"node 表现有列: {columns}")

    has_army = "army" in columns
    print(f"  → army 列 {'已存在' if has_army else '不存在'}")

    # 检查节点数量
    cursor.execute("SELECT COUNT(*) FROM node")
    node_count = cursor.fetchone()[0]
    print(f"  → 现有节点数: {node_count}")

    # 按 army 分组
    if has_army:
        cursor.execute("SELECT army, COUNT(*) FROM node GROUP BY army")
        rows = cursor.fetchall()
        for army, cnt in rows:
            print(f"    {army}: {cnt}")

    conn.close()
    return has_army


def run_migration():
    """执行数据库迁移"""
    db_path = config.DATABASE_PATH
    json_path = config.NODE_DATA_JSON

    print(f"数据库路径: {db_path}")
    print(f"数据文件路径: {json_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 添加 army 列（如果不存在）
    cursor.execute("PRAGMA table_info(node)")
    columns = [row[1] for row in cursor.fetchall()]

    if "army" not in columns:
        print("[1/3] 添加 army 列...")
        cursor.execute(
            "ALTER TABLE node ADD COLUMN army TEXT DEFAULT '中央红军'"
        )
        # 更新现有节点的 army 字段
        cursor.execute("UPDATE node SET army = '中央红军' WHERE army IS NULL OR army = '中央红军'")
        conn.commit()
        print("  → 已完成")

    if "active_sections" not in columns:
        print("[1.1/3] 添加 active_sections 列...")
        cursor.execute(
            "ALTER TABLE node ADD COLUMN active_sections TEXT DEFAULT '[]'"
        )
        conn.commit()
        print("  → 已完成")

    # 2. 读取新 JSON 数据
    print(f"[2/3] 从 JSON 读取数据...")
    with open(json_path, "r", encoding="utf-8") as f:
        all_nodes = json.load(f)
    print(f"  → 共 {len(all_nodes)} 个节点")

    # 3. 插入或更新节点
    print("[3/3] 写入数据库...")
    imported = 0
    updated = 0
    skipped = 0
    errors = []

    for node in all_nodes:
        try:
            node_id = node.get("node_id")
            if not node_id:
                skipped += 1
                continue

            # 检查是否已存在
            cursor.execute("SELECT id FROM node WHERE node_id = ?", (node_id,))
            existing = cursor.fetchone()

            # 准备字段
            fields = [
                "node_id", "title", "location", "lat", "lng", "time",
                "army", "core_numbers", "famous_battle", "important_meeting",
                "history_event", "core_site", "poem_article", "typical_story",
                "typical_people", "historical_significance", "spark_remains",
                "media_path", "image_list", "audio_path", "video_url",
                "status", "active_sections"
            ]

            data = {}
            for f in fields:
                if f in node:
                    v = node[f]
                    if isinstance(v, list):
                        v = json.dumps(v, ensure_ascii=False)
                    data[f] = v

            # 确保必要字段
            data.setdefault("status", "active")
            data.setdefault("created_at", "2025-01-01T00:00:00Z")
            data.setdefault("updated_at", "2026-07-16T00:00:00Z")

            if existing:
                # 更新
                sets = []
                values = []
                for k, v in data.items():
                    if k in ("node_id", "created_at"):
                        continue  # 不更新主键和创建时间
                    sets.append(f"{k} = ?")
                    values.append(v)
                values.append(node_id)
                cursor.execute(
                    f"UPDATE node SET {', '.join(sets)} WHERE node_id = ?",
                    values
                )
                updated += 1
            else:
                # 插入
                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?"] * len(data))
                cursor.execute(
                    f"INSERT INTO node ({columns}) VALUES ({placeholders})",
                    list(data.values())
                )
                imported += 1

        except Exception as e:
            errors.append(f"  [{node.get('node_id','?')}] {str(e)}")
            skipped += 1

    conn.commit()
    conn.close()

    print(f"\n  → 导入 {imported}, 更新 {updated}, 跳过 {skipped}")
    if errors:
        print(f"  → 错误 {len(errors)}:")
        for e in errors:
            print(f"    {e}")

    # 验证
    verify_db()

    return {
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
        "errors": errors
    }


def verify_db():
    """验证数据库"""
    print("\n=== 验证数据库 ===")
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM node")
    total = cursor.fetchone()[0]
    print(f"总节点数: {total}")

    cursor.execute("SELECT army, COUNT(*) FROM node GROUP BY army ORDER BY army")
    rows = cursor.fetchall()
    for army, cnt in rows:
        print(f"  {army}: {cnt}")

    conn.close()


if __name__ == "__main__":
    if "--check" in sys.argv:
        check_db()
    else:
        run_migration()
