# -*- coding: utf-8 -*-
"""生成 版本管理方案 V2.3"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import datetime

doc = Document()

# ===== 样式设置 =====
style = doc.styles['Normal']
font = style.font
font.name = '微软雅黑'
font.size = Pt(11)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')

# ===== 封面 =====
for _ in range(4):
    doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run('我走长征路 - 长征文化数字地图')
run.font.size = Pt(22)
run.bold = True

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = subtitle.add_run('版本管理方案')
run.font.size = Pt(18)

doc.add_paragraph()

info = doc.add_paragraph()
info.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = info.add_run(f'版本：V2.3\n日期：{datetime.date.today().strftime("%Y年%m月%d日")}\n状态：正式发布')
run.font.size = Pt(12)

doc.add_page_break()

# ===== 版本说明 =====
h = doc.add_heading('版本说明', level=1)
doc.add_paragraph('V2.3 在 V2.2 基础上进行以下调整：')
changes = [
    '修正域名：文档域名与实际部署域名一致（zhichangxuan.com 系列）',
    '简化分支策略：从完整 Git Flow 缩减为 prd/dev 双分支工作流',
    '新增泄漏回滚流程：prd 回滚到上一版本，dev 上修复后重新合并',
]
for c in changes:
    doc.add_paragraph(c, style='List Bullet')

doc.add_paragraph()

# ===== 一、文档概览 =====
doc.add_heading('一、文档概览', level=1)
doc.add_paragraph('本文档适用于"我走长征路 - 长征文化数字地图"Web 项目的版本管理与部署运维。项目基于 Python Flask + Leaflet.js + SQLite 架构，部署于阿里云 ECS。')
doc.add_paragraph()

p = doc.add_paragraph()
run = p.add_run('核心目标：')
run.bold = True
run.font.size = Pt(11)

goals = [
    '将测试版本与发布版本完全隔离，避免变更直接影响线上用户。',
    '所有功能开发、Bug 修复、数据更新必须先在 dev 环境验证，确认无误后方可合并至 prd。',
    '建立可追溯、可回滚、可审计的版本管理流程，保障项目长期迭代的稳定性。',
]
for g in goals:
    doc.add_paragraph(g, style='List Bullet')

# ===== 二、分支策略 =====
doc.add_heading('二、分支策略', level=1)
doc.add_paragraph('采用精简双分支流程，适配单团队、单主干的实际情况：')

table = doc.add_table(rows=3, cols=3)
table.style = 'Light Shading Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ['分支名', '用途', '命名规则']
for i, h_text in enumerate(headers):
    cell = table.rows[0].cells[i]
    cell.text = h_text
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.bold = True

data = [
    ['prd', '生产分支，仅用于部署到生产环境。禁止直接提交代码到此分支。', 'prd（不变）'],
    ['dev', '开发分支，日常集成在此进行。所有修改在此完成测试。', 'dev（不变）'],
]
for r_idx, row_data in enumerate(data):
    for c_idx, cell_text in enumerate(row_data):
        table.rows[r_idx + 1].cells[c_idx].text = cell_text

doc.add_paragraph()

# ===== 三、环境架构 =====
doc.add_heading('三、环境架构', level=1)
doc.add_paragraph('项目维护两套独立环境，通过服务器实例、域名、数据库文件三方面完全隔离：')

table = doc.add_table(rows=3, cols=5)
table.style = 'Light Shading Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ['环境', '域名', '服务器端口', '数据库', '用途']
for i, h_text in enumerate(headers):
    cell = table.rows[0].cells[i]
    cell.text = h_text
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.bold = True

env_data = [
    ['开发环境 (dev)', 'dev.zhichangxuan.com', '5001', '/opt/longmarch-dev/data/longmarch.db', '集成测试、验收测试'],
    ['生产环境 (prd)', 'zhichangxuan.com / www.zhichangxuan.com', '5000', '/opt/longmarch-map/data/longmarch.db', '正式对外服务'],
]
for r_idx, row_data in enumerate(env_data):
    for c_idx, cell_text in enumerate(row_data):
        table.rows[r_idx + 1].cells[c_idx].text = cell_text

doc.add_paragraph()

p = doc.add_paragraph()
run = p.add_run('关键隔离策略：')
run.bold = True

isolations = [
    '服务器实例隔离：生产环境和开发测试环境运行在独立的服务器进程（不同端口），不共享进程。',
    '数据库隔离：两套环境各自使用独立的 SQLite 数据库文件，物理上互不干扰。',
    '域名隔离：prd 使用主域名，dev 使用 dev. 子域名。',
    '配置文件隔离：通过独立 config 文件和部署目录区分两套环境的参数。',
    '媒体文件隔离：上传的图片/音频文件分别存储在各自目录下。',
]
for s in isolations:
    doc.add_paragraph(s, style='List Bullet')

# ===== 四、工作流程 =====
doc.add_heading('四、工作流程', level=1)

doc.add_heading('4.1 日常开发流程', level=2)
steps = [
    '在 dev 分支上进行所有开发工作（功能开发、Bug 修复、数据更新）。',
    '本地开发完成后，推送到 GitHub dev 分支。',
    '服务器 dev 环境（dev.zhichangxuan.com）拉取最新 dev 分支代码并部署测试。',
    '在 dev 环境上验证所有改动，包括功能、数据、样式等。',
]
for i, s in enumerate(steps, 1):
    doc.add_paragraph(f'Step {i}: {s}')

doc.add_paragraph()

doc.add_heading('4.2 合并到生产流程', level=2)
p = doc.add_paragraph()
run = p.add_run('关键规则：由用户提出合并，不得自行操作。')
run.bold = True
run.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)

steps = [
    '用户在 dev 环境验收通过。',
    '用户确认后，执行合并：dev 合并到 prd。',
    '生产环境（zhichangxuan.com）拉取最新 prd 分支代码并部署。',
    '观察生产环境 10-15 分钟，确认无异常。',
]
for i, s in enumerate(steps, 1):
    doc.add_paragraph(f'Step {i}: {s}')

doc.add_paragraph()

doc.add_heading('4.3 泄漏回滚流程', level=2)
p = doc.add_paragraph()
run = p.add_run('当合并到 prd 后出现严重泄露（功能损坏、数据错误等）时的处理流程：')
run.font.size = Pt(11)

steps = [
    '立即将 prd 回滚到上一版本的 prd 提交（通过 git revert 或重置到上一次已知稳定的 prd commit）。',
    '生产环境部署回滚后的版本，恢复服务。',
    '在 dev 分支上复现该泄露问题。',
    '在 dev 分支上修复问题并验证通过。',
    '由用户确认修复有效后，再次提出合并到 prd。',
]
for i, s in enumerate(steps, 1):
    doc.add_paragraph(f'Step {i}: {s}')

doc.add_paragraph()

p = doc.add_paragraph()
run = p.add_run('注意：')
run.bold = True
p.add_run('回滚不删除泄露分支上的修改。泄露在 dev 上复现和修复，不走反向合并。prd 始终只从 dev 的单向合并接收稳定代码。')

# ===== 五、版本号命名规范 =====
doc.add_heading('五、版本号命名规范', level=1)
doc.add_paragraph('采用语义化版本号（SemVer）：')
p = doc.add_paragraph()
run = p.add_run('{主版本}.{次版本}.{修订号}')
run.bold = True
p.add_run('    例如：v1.3.2')

table = doc.add_table(rows=4, cols=3)
table.style = 'Light Shading Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ['版本类型', '变更条件', '示例']
for i, h_text in enumerate(headers):
    cell = table.rows[0].cells[i]
    cell.text = h_text
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.bold = True

ver_data = [
    ['主版本', '重大架构变更、不兼容的 API 改动或里程碑式发布', 'v2.0.0'],
    ['次版本', '新增功能、新增节点、新增路线等向下兼容的更新', 'v1.3.0'],
    ['修订号', 'Bug 修复、素材替换、文档修正等细微变更', 'v1.3.2'],
]
for r_idx, row_data in enumerate(ver_data):
    for c_idx, cell_text in enumerate(row_data):
        table.rows[r_idx + 1].cells[c_idx].text = cell_text

doc.add_paragraph()
doc.add_paragraph('Tag 格式：v{主版本}.{次版本}.{修订号}    例如：git tag v1.3.2')

# ===== 六、日常操作流程 =====
doc.add_heading('六、日常操作流程', level=1)

doc.add_heading('6.1 功能开发与 Bug 修复', level=2)
steps = [
    '确保当前在 dev 分支：git checkout dev',
    '在 dev 分支上直接开发或创建临时本地分支开发。',
    '本地测试通过后，提交到 dev 分支并推送到 GitHub。',
    '登录服务器，在 dev 环境拉取最新 dev 代码并重启服务。',
    '在 dev.zhichangxuan.com 验证改动。',
]
for i, s in enumerate(steps, 1):
    doc.add_paragraph(f'{i}. {s}')

doc.add_paragraph()

doc.add_heading('6.2 合并到生产 (由用户发起)', level=2)
steps = [
    '用户确认 dev 环境验收通过。',
    '用户指令执行合并：git checkout prd && git merge dev',
    '本地 / 服务器 prd 环境拉取最新 prd 代码。',
    '重启生产服务。',
    '在 zhichangxuan.com 验证。',
    '打版本 Tag：git tag vX.Y.Z && git push origin vX.Y.Z',
]
for i, s in enumerate(steps, 1):
    doc.add_paragraph(f'{i}. {s}')

doc.add_paragraph()

doc.add_heading('6.3 回滚 (泄漏时)', level=2)
steps = [
    '登录生产服务器，回滚 prd 到上一稳定版本。',
    '部署回滚版并验证恢复。',
    '在 dev 分支复现问题、修复、测试。',
    '用户确认修复后重新发起合并流程。',
]
for i, s in enumerate(steps, 1):
    doc.add_paragraph(f'{i}. {s}')

# ===== 七、数据库版本管理 =====
doc.add_heading('七、数据库版本管理', level=1)
doc.add_paragraph('数据库变更通过迁移脚本执行，生产数据库不允许直接手动修改。')

p = doc.add_paragraph()
run = p.add_run('数据库备份策略：')
run.bold = True

table = doc.add_table(rows=4, cols=4)
table.style = 'Light Shading Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ['备份类型', '内容', '频率', '存储']
for i, h_text in enumerate(headers):
    cell = table.rows[0].cells[i]
    cell.text = h_text
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.bold = True

backup_data = [
    ['全量备份', '生产数据库 .db 文件', '每次发布前', '本地 + 云端双份'],
    ['增量备份', '迁移脚本', '随代码提交', 'Git 仓库'],
    ['归档备份', '完整 .db + 媒体文件', '每周日 03:00', '云端，保留 4 周'],
]
for r_idx, row_data in enumerate(backup_data):
    for c_idx, cell_text in enumerate(row_data):
        table.rows[r_idx + 1].cells[c_idx].text = cell_text

# ===== 八、质量门禁 =====
doc.add_heading('八、发布前检查清单', level=1)
checks = [
    '确认 prd 分支已包含本次发布的所有变更（检查 git log）。',
    '[ ] 在 dev 环境完成全功能回归测试并截图留证。',
    '[ ] 获取生产数据库全量备份（cp prod.db prod.db.bak.vX.Y.Z）。',
    '[ ] 执行生产环境部署：从 prd 分支拉取代码，安装依赖，运行数据库迁移。',
    '[ ] 执行冒烟测试：访问首页、加载节点、切换底图、尝试搜索。',
    '[ ] 观察生产日志 10-15 分钟，确认无异常错误。',
    '[ ] 打版本 Tag 并推送到 GitHub。',
    '[ ] 通知相关方发布完成。',
]
for c in checks:
    doc.add_paragraph(c, style='List Bullet')

# ===== 九、回滚策略 =====
doc.add_heading('九、回滚策略', level=1)

doc.add_heading('9.1 代码回滚', level=2)
items = [
    'Git 回滚优先用 Tag，确保精确恢复：git checkout v1.2.1',
    '若无 Tag，回滚到上一次已知稳定的 prd commit。',
    '生产回滚后必须立即在 dev 环境验证修复。',
]
for i in items:
    doc.add_paragraph(i, style='List Bullet')

doc.add_heading('9.2 数据库回滚', level=2)
items = [
    '结构变更（表/字段）：执行迁移脚本的 down 操作。',
    '数据内容：恢复部署前的备份文件（prod.db.bak）。',
    '媒体文件：从备份目录复制恢复。',
]
for i in items:
    doc.add_paragraph(i, style='List Bullet')

# ===== 十、常用命令参考 =====
doc.add_heading('十、常用命令快速参考', level=1)

cmds = [
    ('本地开发 & 推送', [
        'git checkout dev',
        '# 开发...',
        'git add .',
        'git commit -m "feat: xxx"',
        'git push origin dev',
    ]),
    ('合并到生产（用户发起）', [
        'git checkout prd',
        'git merge dev',
        'git push origin prd',
        '# 服务器上：cd /opt/longmarch-map && git pull origin prd && bash ./006\\ build/deploy.sh',
    ]),
    ('回滚 prd', [
        'git checkout prd',
        'git log --oneline -5        # 找到上一个稳定版本 hash',
        'git revert HEAD             # 或 git reset --hard <上版本hash>',
        'git push --force-with-lease origin prd',
        '# 服务器部署回滚版本',
    ]),
    ('数据库备份', [
        'cp /opt/longmarch-map/001\\ 项目源码/data/longmarch.db \\',
        '   /opt/longmarch-map/001\\ 项目源码/data/longmarch.db.bak.$(date +%Y%m%d)',
    ]),
    ('服务器部署', [
        'cd /opt/longmarch-map',
        'git pull origin prd',
        'source venv/bin/activate',
        'pip install -r "001 项目源码/requirements.txt" -q',
        'bash "./006 build/deploy.sh"',
    ]),
]

for title_text, cmd_list in cmds:
    p = doc.add_paragraph()
    run = p.add_run(title_text)
    run.bold = True
    for cmd in cmd_list:
        p = doc.add_paragraph(cmd)
        p.style = 'No Spacing'
        for run in p.runs:
            run.font.name = 'Consolas'
            run.font.size = Pt(9)

# ===== 版本历史 =====
doc.add_heading('附录：版本历史记录', level=1)
table = doc.add_table(rows=4, cols=4)
table.style = 'Light Shading Accent 1'
table.alignment = WD_TABLE_ALIGNMENT.CENTER
headers = ['版本号', '发布日期', '变更说明', '负责人']
for i, h_text in enumerate(headers):
    cell = table.rows[0].cells[i]
    cell.text = h_text
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.bold = True

hist_data = [
    ['V1.0', '2026-07-22', '版本管理方案初稿（过渡承诺版）', '技术负责人'],
    ['V2.2', '2026-07-22', 'V2.2 务实优化版：移除超前承诺，新增 migrate.py 等', '技术负责人'],
    ['V2.3', datetime.date.today().strftime('%Y-%m-%d'), '修正域名，简化分支策略为 prd/dev 双分支，新增泄漏回滚流程', '技术负责人'],
]
for r_idx, row_data in enumerate(hist_data):
    for c_idx, cell_text in enumerate(row_data):
        table.rows[r_idx + 1].cells[c_idx].text = cell_text

# ===== 保存 =====
output_path = 'D:\\长征文化\\004 项目文档\\长征文化数字地图_版本管理方案_V2.3.docx'
doc.save(output_path)
print(f'Document saved to: {output_path}')
