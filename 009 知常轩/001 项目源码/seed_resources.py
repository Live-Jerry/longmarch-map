# -*- coding: utf-8 -*-
"""知常轩资源板块填充 - 公共资源（全部链接已经服务器 curl 验证 200）"""
import sqlite3, os

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, 'data', 'zhichangxuan.db')

# 模块 id: 1=中国哲学 2=经典古籍 3=儒道和一 4=书法文化 5=诗歌国度 6=中国历史
#          7=长征精神 8=科学前沿 9=西学中用 10=编程世界 11=英语学习 12=我的世界

RESOURCES = [
    # ---------- 电子书：古籍原文（中国哲学书电子化计划 / 古诗文网，均公有领域原文） ----------
    ('论语（原文）', 2, 'book', '中国哲学书电子化计划', 'https://ctext.org/analects/zh', '儒家经典全文阅读'),
    ('孟子（原文）', 2, 'book', '中国哲学书电子化计划', 'https://ctext.org/mencius/zh', '儒家经典全文阅读'),
    ('大学（原文）', 2, 'book', '中国哲学书电子化计划', 'https://ctext.org/great-learning/zh', '四书之一全文阅读'),
    ('中庸（原文）', 2, 'book', '中国哲学书电子化计划', 'https://ctext.org/doctrine-of-the-mean/zh', '四书之一全文阅读'),
    ('三字经（原文）', 2, 'book', '古诗文网', 'https://www.gushiwen.cn/guwen/bookv_6c1c6e29d848.aspx', '蒙学读物全文阅读'),
    ('千字文（原文）', 2, 'book', '中国哲学书电子化计划', 'https://ctext.org/thousand-character-classic/zh', '蒙学读物全文阅读'),
    ('增广贤文（原文）', 2, 'book', '中国哲学书电子化计划', 'https://ctext.org/zeng-guang-xian-wen/zh', '蒙学格言集全文阅读'),
    ('史记（原文）', 2, 'book', '中国哲学书电子化计划', 'https://ctext.org/records-of-the-grand-historian/zh', '二十四史之首全文阅读'),
    ('道德经（原文）', 3, 'book', '中国哲学书电子化计划', 'https://ctext.org/dao-de-jing/zh', '道家经典全文阅读'),
    ('庄子（原文）', 3, 'book', '中国哲学书电子化计划', 'https://ctext.org/zhuangzi/zh', '道家经典全文阅读'),
    ('唐诗三百首（原文）', 5, 'book', '古诗文网', 'https://www.gushiwen.cn/shiwens/default.aspx?astr=%E5%94%90%E8%AF%97%E4%B8%89%E7%99%BE%E9%A6%96', '唐诗选本全文阅读'),
    ('古诗文网古籍库', 5, 'book', '古诗文网', 'https://www.gushiwen.cn/guwen/', '诗词古文在线查阅'),
    ('中国哲学书电子化计划', 1, 'book', 'ctext.org', 'https://ctext.org/zh', '先秦两汉典籍全文数据库'),
    ('史记（原文）', 6, 'book', '中国哲学书电子化计划', 'https://ctext.org/records-of-the-grand-historian/zh', '纪传体通史全文阅读'),
    ('国家图书馆·中华古籍资源库', 6, 'book', '中国国家图书馆', 'https://www.nlc.cn/', '官方古籍数字化资源'),
    # ---------- 视频：官方公开平台 ----------
    ('国家中小学智慧教育平台', 1, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
    ('国家中小学智慧教育平台', 2, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
    ('国家中小学智慧教育平台', 3, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
    ('国家中小学智慧教育平台', 4, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
    ('国家中小学智慧教育平台', 5, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
    ('国家中小学智慧教育平台', 6, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
    ('国家中小学智慧教育平台', 7, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
    ('国家中小学智慧教育平台', 8, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
    ('国家中小学智慧教育平台', 9, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
    ('国家中小学智慧教育平台', 10, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
    ('国家中小学智慧教育平台', 11, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
    ('国家中小学智慧教育平台', 12, 'video', '教育部官方平台', 'https://basic.smartedu.cn/', '免费公开课与学习资源'),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    total = 0
    for title, mid, cat, source, url, desc in RESOURCES:
        exists = cur.execute(
            'SELECT id FROM resource_link WHERE title=? AND module_id=? AND category=? AND share_url=?',
            (title, mid, cat, url)).fetchone()
        if exists:
            print('已存在,跳过:', title, 'mod', mid)
            continue
        cur.execute('''INSERT INTO resource_link
            (title, module_id, column_name, category, source, file_size, share_url, access_code, description, status)
            VALUES (?,?,?,?,?,?,?,?,?,1)''',
            (title, mid, '', cat, source, '在线阅读', url, '', desc))
        total += 1
        print('入库:', title, '-> mod', mid)
    conn.commit()
    conn.close()
    print('本次入库资源:', total, '条')


if __name__ == '__main__':
    main()
