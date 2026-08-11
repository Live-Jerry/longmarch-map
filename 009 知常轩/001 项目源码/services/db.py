# -*- coding: utf-8 -*-
"""
知常轩 · 数据访问层
SQLite 读写封装（module / article / daily_saying / resource_link）
"""
import os, sqlite3

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目源码/
DB_PATH = os.path.join(BASE, 'data', 'zhichangxuan.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- 模块 ----------------
def get_modules():
    conn = get_db()
    rows = conn.execute('SELECT * FROM module WHERE status=1 ORDER BY sort_order').fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------- 每日一句 ----------------
def get_today_saying():
    """取今日每日一句；无今日记录则随机取一条"""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM daily_saying ORDER BY CASE WHEN date=date('now','localtime') THEN 0 ELSE 1 END, RANDOM() LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_daily_sayings(limit=20):
    conn = get_db()
    rows = conn.execute('SELECT * FROM daily_saying ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------- 资源 ----------------
def get_resources(category=None):
    conn = get_db()
    if category:
        rows = conn.execute('SELECT * FROM resource_link WHERE status=1 AND category=? ORDER BY id', (category,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM resource_link WHERE status=1 ORDER BY id').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_module_files(module_id):
    """按模块取文件资源（书法碑帖等，category=shufa_pdf）"""
    conn = get_db()
    rows = conn.execute('SELECT * FROM resource_link WHERE status=1 AND module_id=? ORDER BY id', (module_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------- 文章 ----------------
def get_article(aid):
    conn = get_db()
    row = conn.execute('SELECT * FROM article WHERE id=? AND status=1', (aid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_articles_by_module(module_id, limit=20):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM article WHERE status=1 AND module_id=? ORDER BY published_at DESC LIMIT ?',
        (module_id, limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_random_article():
    """随机取一篇已发布文章（首页今日推荐用），带模块名"""
    conn = get_db()
    row = conn.execute(
        'SELECT a.*, m.name AS module_name, m.slug AS module_slug FROM article a '
        'JOIN module m ON a.module_id = m.id WHERE a.status=1 ORDER BY RANDOM() LIMIT 1'
    ).fetchone()
    conn.close()
    return dict(row) if row else None
