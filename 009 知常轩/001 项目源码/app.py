# -*- coding: utf-8 -*-
"""
知常轩主站 · Flask 应用入口
V1.0 结构上线：首页 + 8 模块页 + 文章系统 + 每日一句 + 资源中心 + 重走长征路接入
"""
import os
from flask import Flask, render_template, abort

BASE = os.path.dirname(os.path.abspath(__file__))

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'zhichangxuan-dev-key')
    app.config['JSON_AS_ASCII'] = False

    # ---------------- 模块数据（V2.2 方案 1.3） ----------------
    MODULES = [
        {'slug': 'zhexue',     'name': '中国哲学', 'en': 'Chinese Philosophy', 'color': '#1C1C2E', 'accent': '#E8C547',
         'desc': '哲学是全部科学之母——建立思维框架，理解世界本质。',
         'columns': ['先秦诸子入门', '核心概念词典', '思维方法专题', '青少年哲学对话']},
        {'slug': 'guiji',      'name': '经典古籍', 'en': 'Classical Texts', 'color': '#F5F0E8', 'accent': '#C73E3A',
         'desc': '不求背诵，只求理解——让孩子读懂古人的智慧。',
         'columns': ['必读经典三级导读', '古籍精读课', '经典人物', '古文学习工具']},
        {'slug': 'rudao',      'name': '儒与道', 'en': 'Confucianism & Taoism', 'color': '#E8C547', 'accent': '#2D6A4F',
         'desc': '儒道互补，才是完整的中国精神。',
         'columns': ['儒家', '道家', '儒道对比专题', '家长课堂']},
        {'slug': 'shufa',      'name': '书法文化', 'en': 'Calligraphy', 'color': '#1A1A1A', 'accent': '#E8EEF2',
         'desc': '书法是中华文化的基因工程。',
         'columns': ['书法简史', '五体书详解', '名家名帖赏析', '书法入门教程', '趣味书法']},
        {'slug': 'shige',      'name': '诗歌国度', 'en': 'Poetry', 'color': '#2D6A4F', 'accent': '#F5F0E8',
         'desc': '诗不是用来背的，是用来感受的。',
         'columns': ['诗词发展史', '四大流派精读', '诗词创作入门', '诗词与科学', '诗词闯关', '诗词地图']},
        {'slug': 'jindaishi',  'name': '近现代史', 'en': 'Modern History', 'color': '#C73E3A', 'accent': '#1A1A1A',
         'desc': '以史为鉴，培养历史理性与民族自信。',
         'columns': ['近代中国时间轴', '重大事件专题', '重要历史人物', '少年红色故事', '历史图片馆', '复兴之路']},
        {'slug': 'changzheng', 'name': '长征精神', 'en': 'Long March Spirit', 'color': '#E8C547', 'accent': '#C73E3A',
         'desc': '理解长征，才能理解中国共产党为什么能。',
         'columns': ['长征全景地图', '重要节点', '长征故事', '长征诗词', '现代意义', '数字可视化'],
         'subapp': 'https://cz.zhichangxuan.com'},
        {'slug': 'kexue',      'name': '当代科学', 'en': 'Modern Science', 'color': '#2D6A4F', 'accent': '#E8EEF2',
         'desc': '科技强国，培养科学精神与探索欲。',
         'columns': ['物理世界', '化学世界', '生物世界', '天文与宇宙', '数学思维', '前沿科技', '科学辟谣', '家庭小实验']},
    ]

    # ---------------- 路由 ----------------
    @app.route('/')
    def index():
        return render_template('index.html', modules=MODULES)

    @app.route('/modules/<slug>')
    def module_page(slug):
        for m in MODULES:
            if m['slug'] == slug:
                return render_template('module.html', mod=m, modules=MODULES)
        abort(404)

    @app.route('/article/<int:aid>')
    def article_page(aid):
        return render_template('article.html', aid=aid, modules=MODULES)

    @app.route('/daily')
    def daily():
        return render_template('daily.html', modules=MODULES)

    @app.route('/resources')
    def resources():
        return render_template('resources.html', modules=MODULES)

    @app.route('/parents')
    def parents():
        return render_template('parents.html', modules=MODULES)

    @app.route('/about')
    def about():
        return render_template('about.html', modules=MODULES)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html', modules=MODULES), 404

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8020, debug=True)
