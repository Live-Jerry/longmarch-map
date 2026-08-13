# -*- coding: utf-8 -*-
"""
知常轩主站 · Flask 应用入口
V1.0 结构上线：首页 + 模块页 + 文章系统 + 每日一句 + 资源中心 + 我走长征路接入
模块数量不写死，由 module 表数据驱动，后续可动态增删
"""
import os
from flask import Flask, render_template, abort, request, redirect, url_for, flash
from services import db

BASE = os.path.dirname(os.path.abspath(__file__))

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'zhichangxuan-dev-key')
    app.config['JSON_AS_ASCII'] = False

            # ---------------- 模块数据（DB 读取 + 栏目映射） ----------------
    COLUMNS = {
        'zhexue': ['先秦诸子入门', '核心概念词典', '思维方法专题', '青少年哲学对话'],
        'guiji': ['必读经典', '古籍精读课', '经典人物', '古文学习工具'],
        'rudao': ['儒家', '道家', '儒道对比专题', '家长课堂'],
        'shufa': ['书法简史', '五体书详解', '名家名帖赏析', '书法入门教程', '趣味书法'],
        'shige': ['诗词发展史', '四大流派精读', '诗词创作入门', '诗词与科学', '诗词闯关', '诗词地图'],
        'jindaishi': ['近代中国时间轴', '重大事件专题', '重要历史人物', '少年红色故事', '历史图片馆', '复兴之路'],
        'changzheng': ['长征全景地图', '重要节点', '长征故事', '长征诗词', '现代意义', '数字可视化'],
        'kexue': ['物理世界', '化学世界', '生物世界', '天文与宇宙', '数学思维', '前沿科技', '科学辟谣', '家庭小实验'],
        'xixue': ['欧美经典理论', '经典著作导读', '西方思想史', '中西对比专题', '大师与名著'],
        'biancheng': ['编程入门', '编程语言学习', '算法与思维', '编程资讯', '项目实践', '青少年编程赛事'],
        'yingyu': ['英语启蒙', '词汇与语法', '听说读写', '原版阅读', '英语学习资讯'],
        'wodeshijie': ['奇趣话题', '十万个为什么', '科学趣闻', '成长困惑', '兴趣分享'],
    }
    SUBAPPS = {'changzheng': 'https://cz.zhichangxuan.com'}
    MODULES = db.get_modules()
    MODULE_EN = {
        'zhexue': 'Chinese Philosophy', 'guiji': 'Classical Texts',
        'rudao': 'Confucianism & Taoism', 'shufa': 'Calligraphy',
        'shige': 'Poetry', 'jindaishi': 'Chinese History',
        'changzheng': 'Long March Spirit', 'kexue': 'Science Frontiers',
        'xixue': 'Western Learning', 'biancheng': 'Programming',
        'yingyu': 'English Learning', 'wodeshijie': 'My World',
    }
    for m in MODULES:
        m['en'] = MODULE_EN.get(m['slug'], '')
        m['desc'] = m.get('description', '')
        m['columns'] = COLUMNS.get(m['slug'], [])
        if m['slug'] in SUBAPPS:
            m['subapp'] = SUBAPPS[m['slug']]
    # ---------------- 路由 ----------------
    @app.context_processor
    def inject_modules():
        """全站注入模块列表：主导航与首页模块网格共用同一数据源，保证二者一致"""
        return dict(modules=MODULES)

    @app.route('/')
    def index():
        pick = db.get_random_article()
        return render_template('index.html', modules=MODULES, saying=db.get_today_saying(), pick=pick)

    @app.route('/modules/<slug>')
    def module_page(slug):
        for m in MODULES:
            if m['slug'] == slug:
                articles = db.get_articles_by_module(m['id'])
                files = db.get_module_files(m['id'])
                return render_template('module.html', mod=m, modules=MODULES, articles=articles, files=files)
        abort(404)

    @app.route('/article/<int:aid>')
    def article_page(aid):
        art = db.get_article(aid)
        if not art:
            abort(404)
        cur_slug = ''
        for m in MODULES:
            if m['id'] == art['module_id']:
                cur_slug = m['slug']
        return render_template('article.html', article=art, modules=MODULES, current_slug=cur_slug)

    @app.route('/daily')
    def daily():
        return render_template('daily.html', modules=MODULES, sayings=db.get_daily_sayings())

    @app.route('/resources')
    def resources():
        # 资源按所属模块分组（module_id），未归属资源归入「其他资源」
        res = db.get_resources()
        group_list = [{'module': m, 'resources': []} for m in MODULES]
        others = []
        for r in res:
            g = next((g for g in group_list if g['module']['id'] == r['module_id']), None)
            if g:
                g['resources'].append(r)
            else:
                others.append(r)
        return render_template('resources.html', modules=MODULES, group_list=group_list, others=others)

    @app.route('/resources/browse/<path:subpath>')
    def resource_browse(subpath):
        # 本地资源目录浏览：/static/res/<subpath>/ 下的文件列表
        # 安全校验：只允许 res 目录内的相对路径，禁止 .. 穿越
        if '..' in subpath or subpath.startswith('/') or os.path.isabs(subpath):
            abort(404)
        res_dir = os.path.join(app.static_folder, 'res')
        target_dir = os.path.normpath(os.path.join(res_dir, subpath))
        if not target_dir.startswith(os.path.normpath(res_dir)) or not os.path.isdir(target_dir):
            abort(404)
        files = []
        for name in sorted(os.listdir(target_dir)):
            full = os.path.join(target_dir, name)
            if os.path.isfile(full):
                files.append({
                    'name': name,
                    'url': url_for('static', filename='res/' + subpath + '/' + name),
                    'size': os.path.getsize(full),
                })
        return render_template('resource_files.html', modules=MODULES, subpath=subpath, files=files)

    @app.route('/resources/upload', methods=['GET', 'POST'])
    def resource_upload():
        if request.method == 'POST':
            title = (request.form.get('title') or '').strip()
            module_id = request.form.get('module_id', type=int)
            column_name = (request.form.get('column_name') or '').strip()
            category = (request.form.get('category') or 'A').strip()
            description = (request.form.get('description') or '').strip()
            share_url = (request.form.get('share_url') or '').strip()
            if not title or not module_id:
                flash('请填写资料标题并选择所属模块', 'error')
                return redirect(url_for('resource_upload'))
            db.add_resource(title=title, module_id=module_id, column_name=column_name,
                            category=category, description=description, share_url=share_url)
            flash('提交成功：资料已登记，经管理员审核后上线展示（先审后发）', 'success')
            return redirect(url_for('resources'))
        preselect = request.args.get('module', '')
        columns_json = {m['slug']: m['columns'] for m in MODULES}
        return render_template('upload.html', modules=MODULES, preselect=preselect,
                               columns_json=columns_json)

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
