# -*- coding: utf-8 -*-
"""
知常轩数据库初始化脚本
建表：module / article / daily_saying / resource_link（V2.2 方案 7.3 数据模型）
用法: python init_db.py
"""
import os, sqlite3, io, json

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, 'data', 'zhichangxuan.db')

SCHEMA = """
-- 模块表
CREATE TABLE IF NOT EXISTS module (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50),
    slug VARCHAR(50) UNIQUE,
    color VARCHAR(20),
    accent VARCHAR(20),
    description TEXT,
    badge VARCHAR(10),
    sort_order INTEGER DEFAULT 0,
    status INTEGER DEFAULT 1
);

-- 文章表
CREATE TABLE IF NOT EXISTS article (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200),
    module_id INTEGER REFERENCES module(id),
    column_name VARCHAR(50),
    content TEXT,
    original_text TEXT,
    annotation TEXT,
    translation TEXT,
    cover_image VARCHAR(200),
    tags VARCHAR(200),
    age_level VARCHAR(20),
    status INTEGER DEFAULT 0,
    author_id INTEGER,
    published_at DATETIME,
    views INTEGER DEFAULT 0
);

-- 每日一句
CREATE TABLE IF NOT EXISTS daily_saying (
    id INTEGER PRIMARY KEY,
    original_text TEXT NOT NULL,
    source VARCHAR(200),
    translation TEXT,
    scene VARCHAR(200),
    date DATE UNIQUE
);

-- 资源导航
CREATE TABLE IF NOT EXISTS resource_link (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200),
    category VARCHAR(50),
    source VARCHAR(200),
    file_size VARCHAR(50),
    share_url VARCHAR(500),
    access_code VARCHAR(20),
    description TEXT,
    status INTEGER DEFAULT 1
);
"""

MODULES = [
    ('中国哲学', 'zhexue', '#1C1C2E', '#E8C547', '哲学是全部科学之母——建立思维框架，理解世界本质。', 1, '中'),
    ('经典古籍', 'guiji', '#C73E3A', '#F5F0E8', '不求背诵，只求理解——让孩子读懂古人的智慧。', 2, '经'),
    ('儒与道', 'rudao', '#2D6A4F', '#E8C547', '儒道互补，才是完整的中国精神。', 3, '儒'),
    ('书法文化', 'shufa', '#2B2B2B', '#E8EEF2', '书法是中华文化的基因工程。', 4, '书'),
    ('诗歌国度', 'shige', '#7BA3A8', '#F5F0E8', '诗不是用来背的，是用来感受的。', 5, '诗'),
    ('中国历史', 'jindaishi', '#8B5E3C', '#F5F0E8', '以史为鉴，培养历史理性与民族自信。', 6, '史'),
    ('长征精神', 'changzheng', '#D4A017', '#C73E3A', '理解长征，才能理解中国共产党为什么能。', 7, '征'),
    ('科学前沿', 'kexue', '#35658A', '#E8EEF2', '科技强国，培养科学精神与探索欲。', 8, '科'),
]

DAILY_SAYINGS = [
    ('知人者智，自知者明。胜人者有力，自胜者强。', '《道德经》第三十三章',
     '能了解别人是智慧，能认识自己才是真正的明智；能战胜别人是有力，能战胜自己才是真正的强大。',
     '考试失利时，问问自己——我要战胜的，其实是昨天的我。'),
    ('千里之行，始于足下。', '《道德经》第六十四章',
     '走一千里的路程，是从脚下第一步开始的。',
     '面对大目标不知从何下手时，先迈出第一步。'),
    ('上善若水。水善利万物而不争。', '《道德经》第八章',
     '最高的善就像水一样。水善于滋润万物却不与万物相争。',
     '和同学发生矛盾时，想想水的智慧——利他而不争。'),
    ('学而不思则罔，思而不学则殆。', '《论语·为政》',
     '只学习不思考就会迷惑，只思考不学习就会懈怠。',
     '做完题不订正等于白做——学和思要一起走。'),
    ('三人行，必有我师焉。', '《论语·述而》',
     '几个人一起走，其中一定有可以当我老师的人。',
     '每个人都有值得你学习的地方。'),
    ('玉不琢，不成器；人不学，不知道。', '《三字经》',
     '玉石不经过雕琢，不能成为器物；人不学习，就不明白道理。',
     '学习就像雕琢，过程辛苦，结果美丽。'),
    ('知之者不如好之者，好之者不如乐之者。', '《论语·雍也》',
     '知道它的人不如喜爱它的人，喜爱它的人不如以它为乐的人。',
     '找到学习的乐趣，比逼自己努力更重要。'),
    ('天行健，君子以自强不息。', '《周易》',
     '天道的运行刚健有力，君子应当像天一样奋发图强、永不停息。',
     '遇到困难时，想想天体的运行——永远向前。'),
]

RESOURCES = [
    ('道德经', 'A', '帛书本80章原文+译文结构化JSON；全文朗读80章音频', '已就绪', '知常轩线上精读（已上线）', None,
     '原文注音对照+白话译文+儿童解读+原文朗读，五段式精读'),
    ('论语', 'A', '20篇朗读音频', '已下载', None, None, '经典诵读音频资源'),
    ('荀子', 'A', 'txt + 集解 + 32篇音频', '已下载', None, None, '先秦儒家经典'),
    ('增广贤文', 'A', 'PDF', '已下载', None, None, '蒙学读物'),
    ('小学生必背古诗75+70', 'A', '音频 + PDF', '已下载', None, None, '小学古诗诵读'),
    ('中华书局二十四史', 'A', '24册PDF（古籍影印）', '已下载', None, None, '正史影印本'),
    ('初学套餐碑帖', 'A', '礼器碑/曹全碑/多宝塔/九成宫/小楷集 高清JPG', '已下载', None, None, '书法临摹碑帖'),
]


def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(SCHEMA)

    # 模块
    cur.execute('SELECT COUNT(*) FROM module')
    if cur.fetchone()[0] == 0:
        cur.executemany('INSERT INTO module (name, slug, color, accent, description, sort_order, badge) VALUES (?,?,?,?,?,?,?)', MODULES)
        print('模块:', len(MODULES), '条')

    # 每日一句
    cur.execute('SELECT COUNT(*) FROM daily_saying')
    if cur.fetchone()[0] == 0:
        cur.executemany('INSERT INTO daily_saying (original_text, source, translation, scene) VALUES (?,?,?,?)', DAILY_SAYINGS)
        print('每日一句:', len(DAILY_SAYINGS), '条')

    # 资源
    cur.execute('SELECT COUNT(*) FROM resource_link')
    if cur.fetchone()[0] == 0:
        cur.executemany('INSERT INTO resource_link (title, category, source, file_size, share_url, access_code, description) VALUES (?,?,?,?,?,?,?)', RESOURCES)
        print('资源:', len(RESOURCES), '条')

    conn.commit()
    conn.close()
    print('数据库就绪:', DB_PATH)


if __name__ == '__main__':
    main()
