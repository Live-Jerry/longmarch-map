# MEMORY.md — 长征文化数字地图

## 项目概况

项目名称： 我走长征路 — 长征文化数字平台 2.0.0
项目目标： 用交互式卫星地图展示红军长征历史路线，集成多媒体内容（图片、语音、文字）和用户互动功能
技术栈： Python Flask 后端 + Leaflet.js 前端 + SQLite 数据库
状态： V004 版本，生产部署完成（开发测试环境）

##  修改工作规范（不可违背）

1. 先确认，后动手 — 任何修改先确认要改的点、改什么、怎么改，得到确认后再实施
2. 改完即测 — 每次修改完成立刻测试，有问题立即修复
3. 不破坏原有代码 — 新增功能不得影响已有功能，不改动不相关的模块
4. 修改必须正确 — 每次修改经过验证，确保逻辑正确、运行无误
5. 记录在案 — 每次修改在 memory 中记录变更内容、测试结果
6. 操作与用户共同维护的文件（如EC表）三条铁律：
   a) 文件锁着禁止建副本 — PermissionError时禁止建副本或改名操作，提示用户文件被锁，等用户关闭后再操作
   b) 操作前读全文 — 任何操作前必须全部阅读文件全文，不得假定内容不变
   c) 禁止读副本 — 只能读原文件，不得读之前建的副本或临时文件
7. 设计文档修改规则（2026-08-12 用户重申）：知常轩等设计文档（V2.3.docx）只做局部修改，严禁推倒重写；改前通读全文，定点修订，不动的部分一律不碰
8. 细节先入文档（2026-08-12 用户明确）：之前建框架没仔细规划，之后所有细节（模块名、徽标字等）一律先写入设计文档，再改代码
9. 任何更改前必须通读设计文档全文（2026-08-12 用户强调）：改代码/改文档前先通读 V2.3.docx 全文（python-docx dump 后通读），不得凭记忆或片段开工；用户发现过“只顾局部不看全局”的缺陷（如新模块颜色与已有模块重复）

## EC变更跟踪表填写规则（铁律）

### 谁写什么
- 用户写（我绝对不能碰）：序号、类型、来源、问题/需求描述、预期结果、状态、关闭确认
- AI写（我只能写）：影响模块、原因分析、变更方案

### 什么事绝对不能做
- 绝对不能修改用户填写的内容（列1-5、列9-10）
- 绝对不能往状态列和关闭确认列写任何字
- 绝对不能删除/清空/覆盖用户写过的任何列
- 如果分不清哪些列是用户的，先读这条规则，再确认，再动手

## 禁用 Emoji（铁律）

1. 任何地方、任何工作禁用 emoji — 包括但不限于：源代码、注释、文档、提交信息、日志、README、MEMORY.md 本身、以及与我的一切交流。
2. 使用纯文本替代 — 删除或用文字描述代替，不得新增 emoji。

## 注意 工具输出规范（铁律）

1. 输出可以同时包含文本和图片 — 不要因看到"请见附件图片"就否定文本的存在。输出可以既包含文本描述也包含图片附件，两者并行不悖。
2. 工具的文本输出是真实、完整的 — 不要编造"工具异常"来为自己的误读开脱。如果看不懂，先假设自己没读对。

##  工作区结构

```
D:\长征文化\
├── 000 脚本策划/       — 设计文档、照片获取指南
├── 001 项目源码/       — Flask 全栈应用
│   ├── api/            — REST API 路由（5 个蓝图）
│   ├── services/       — 业务逻辑层（6 个管理器）
│   ├── models/         — 数据模型（node/user/media/spark）
│   ├── interfaces/     — API 接口定义文档
│   ├── data/           — SQLite 数据库 + node_data.json
│   ├── static/         — CSS/JS 前端资源
│   └── templates/      — HTML 模板（含管理后台）
├── 002 项目资源/       — 节点照片资源（瑞金、湘江、遵义等）
├── 004 项目文档/       — 额外文档
├── 005 代码备份/       — 初始版本 Python 脚本
└── 008 设计备份/       — 多版本设计文档
```

## Git & GitHub

- 远程仓库: https://github.com/Live-Jerry/longmarch-map.git
- 开发分支: develop（日常集成用），main（稳定发布）
- Git 身份: 长征文化数字地图项目组 / project@longmarch-map.cn
- 认证方式: GitHub Personal Access Token（通过 Git Credential Manager 缓存）
- 本地最新提交: bbccbcd — fix: add wsgi.py entry point for gunicorn
- .gitignore 忽略项: `002 项目资源/`, `*.db`, `uploads/`, `004 项目文档/doxygen/`, `*.log`, `~$*`, 临时脚本

### 版本日志维护规则

- CHANGELOG.md 由每次提交代码的人同步更新
- 规则：每次 push 前，检查是否有值得记录的变更，有则加一行
- 版本号格式：V{主}.{次}.{修} (YYYY-MM-DD)
- 条目简洁明了，每个变更一句话，不要大段叙述

##  长征节点（25 个）

按时间线排列（node_id 含义：主序号.子序号）：

| 编号 | 名称 | 时间 | 事件类型 |
|------|------|------|---------|
| 1.1 | 江西瑞金 | 1934.10 | 出发地 |
| 1.2 | 福建长汀 | 1934.09 | 出发地 |
| 1.3 | 江西于都 | 1934.10 | 集结出发地 |
| 2.1 | 湘江战役（道县→全州） | 1934.11 | 惨烈血战 |
| 3.1 | 湖南通道 | 1934.12 | 通道会议 |
| 4.1 | 贵州黎平 | 1934.12 | 黎平会议 |
| 4.2 | 贵州瓮安（猴场） | 1935.01 | 猴场会议+强渡乌江 |
| 4.3 | 贵州遵义 | 1935.01 | 遵义会议+娄山关 |
| 4.4 | 云南扎西 | 1935.02 | 扎西会议 |
| 4.5 | 贵州苟坝 | 1935.03 | 苟坝会议 |
| 5.1 | 四渡赤水 | 1935.01-03 | 得意之笔 |
| 6.1 | 巧渡金沙江 | 1935.05 | 战略胜利 |
| 7.1 | 强渡大渡河（安顺场） | 1935.05 | 天险突破 |
| 7.2 | 飞夺泸定桥 | 1935.05 | 传奇之战 |
| 8.1 | 翻越夹金山 | 1935.06 | 首次雪山 |
| 9.1 | 懋功会师 | 1935.06 | 会师 |
| 9.2 | 两河口会议 | 1935.06 | 北上决策 |
| 9.3 | 芦花会议 | 1935.07 | 组织调整 |
| 10.1 | 毛儿盖/沙窝 | 1935.08 | 过草地准备 |
| 10.2 | 穿越松潘草地 | 1935.08 | 最艰难历程 |
| 10.3 | 巴西会议 | 1935.09 | 与张国焘分裂斗争 |
| 11.1 | 俄界会议 | 1935.09 | 陕甘支队成立 |
| 11.2 | 攻克腊子口 | 1935.09 | 奇袭天险 |
| 11.3 | 哈达铺 | 1935.09 | 发现陕北根据地 |
| 11.4 | 榜罗镇 | 1935.09 | 落脚点最终确定 |
| 12.1 | 翻越六盘山 | 1935.10 | 最后一座高山 |
| 13.1 | 陕西吴起镇 | 1935.10 | 长征胜利结束 |
| 14.1 | 甘肃会宁 | 1936.10 | 三大主力会师 |
| 14.2 | 宁夏将台堡 | 1936.10 | 收官之作 |

##  知常轩模块（12 个，2026-08-12 V2.3.4 调整）

| 序号 | 模块名 | slug | 圈字 |
|------|--------|------|------|
| 1 | 中国哲学 | zhexue | 中 |
| 2 | 经典古籍 | guiji | 经 |
| 3 | 儒道和一（原儒与道） | rudao | 儒 |
| 4 | 书法文化 | shufa | 书 |
| 5 | 诗歌国度 | shige | 诗 |
| 6 | 中国历史（原近现代史） | jindaishi | 史 |
| 7 | 长征精神 | changzheng | 征 |
| 8 | 科学前沿（原当代科学） | kexue | 科 |
| 9 | 西学中用（简称西，欧美经典理论书籍） | xixue | 西 |
| 10 | 编程世界 | biancheng | 编 |
| 11 | 英语学习 | yingyu | 英 |
| 12 | 我的世界（开放话题） | wodeshijie | 我 |

- 首页导航与模块网格同数据源（module 表，context_processor 注入），自动一致
- 互动模块（首页深色条）：资源中心 / 家长学堂，不在主导航，首页入口+页脚承接
- 资源中心：按模块分组展示（module_id+column_name 栏目），每模块有「上传资料」入口（status=0 待审，先审后发）
- 日常任务（cron 每周一 09:30）：根据百度云「001 孩子教育与终身学习资源」充实各模块，文本直接更新，图片/视频大文件先确认（V2.3 文档 11.5 机制）

##  技术架构

### 备案信息
- ICP 备案号：陕ICP备2026020519号（主体：刘福财）
- ICP 备案查询：https://beian.miit.gov.cn/
- 公安网安备案：已通过（2026-08-06 高新分局网安大队，新增主体/新办网站/安全评估三项全过；8-04 雁塔分局 4 条被拒或撤销）
- 公安备案号：陕公网安备61019002004143号（网站：知常轩 / zhichangxuan.com）
- 公安备案查询：https://beian.mps.gov.cn/#/query/webSearch?code=61019002004143
- 公安备案图标：`001 项目源码/static/img/gongan_badge.png`（36x40，平台下载）
- 页脚位置：index.html 右下角固定小字（#icp-footer），不遮挡 Leaflet 缩放和右侧控制栏

### 后端 (Flask)
- 认证系统： JWT（HMAC-SHA256），注册/登录/令牌验证；角色: guest/user/admin/super
- 节点管理： 完整 CRUD，分页搜索、附近查询、JSON 导入导出、时间线
- 路线引擎： 4 支军队的路线数据（中央红军、红二/四方面军、红25军），GeoJSON 输出，自动漫游路径计算（haversine公式）
- 素材管理： 文件上传（图片/音频/视频），MIME校验，审核工作流
- 星火拾遗： 用户贡献内容，提交→待审核→通过/拒绝 流程
- TTS服务： 基于 Web Speech API 的配置参数生成

### 前端 (Leaflet.js)
- ArcGIS 卫星底图 + OSM 浅色/深色切换
- 滴水形红色标记，Catmull-Rom 样条平滑路线
- 5步信息面板（时间→战役→会议→事件→意义）
- 自动漫游：沿路线移动，模拟30km/h速度
- TTS 朗读：浏览器原生 Speech API，中文语音
- 留言板+军队选择器

### 数据库 (SQLite)
- 6 张表：user, node, media, spark, comment, route_point

## 开发分支工作流

以《004 项目文档/项目版本通用管理规范.docx》（V4.1，原「长征文化数字地图_版本管理方案_V3.1.docx」改名）为准（严禁 AI 全面更改该文档，只做局部修订），升级前读版本管理文档。
- 项目代码约定（文档「〇、项目代码约定」）：cz=长征项目，zcx=知常轩项目，后续项目按需登记（如 abc）；文档内所有 <项目代码> 为通配符
- tag 前缀区分项目：cz 用 CZ，zcx 用 ZCX（例：ZCXdev+2.3.5+rc、ZCXprd+2.3.5+last-good），按文档 <项目代码> 通配符替换（2026-08-12 用户批评过机械套用 CZ）

- develop 分支：日常开发集成，所有功能分支合并到此测试
- main 分支：稳定发布
- 本地提交后 push origin develop，服务器从 develop 拉取部署

## 部署详情

### 服务器
- 地址: root@8.133.203.255
- SSH 密钥: longmarch_ecs
- 主机名: iZuf61gpktwo4kt3xf09pzZ（仅内网可用，公网用 IP）

### 生产环境 (zhichangxuan.com)
- 域名: `https://zhichangxuan.com` / `https://www.zhichangxuan.com` / `https://cz.zhichangxuan.com`
- 项目路径: `/opt/longmarch-map/`
- Python 虚拟环境: `/opt/longmarch-map/venv/`
- WSGI: gunicorn (配置: `./006 build/gunicorn_config.py wsgi:app --daemon`)
- 后端端口: 5000
- Nginx 反代: 443 HTTPS -> 127.0.0.1:5000（HTTP 80 自动跳转 HTTPS）
- SSL: Let's Encrypt（证书路径: /etc/letsencrypt/live/zhichangxuan.com/）
- 静态文件: 7d 缓存，路径 `/opt/longmarch-map/001 项目源码/static/`
- 日志: `/opt/longmarch-map/logs/{error,access}.log`
- 数据库: `/opt/longmarch-map/001 项目源码/data/longmarch.db`

### 开发/测试环境 (dev.zhichangxuan.com)
- 域名: `https://dev.zhichangxuan.com`
- 项目路径: `/opt/longmarch-dev/`
- Python 虚拟环境: `/opt/longmarch-dev/venv/`
- WSGI: gunicorn --workers=3 --bind=0.0.0.0:5001 --timeout=60 wsgi:app --daemon
- 后端端口: 5001
- Nginx 反代: 443 HTTPS -> 127.0.0.1:5001（HTTP 80 自动跳转 HTTPS）
- SSL: Let's Encrypt（共用生产证书）
- 静态文件: 无缓存（expires 0），路径 `/opt/longmarch-dev/001 项目源码/static/`
- 日志: `/opt/longmarch-dev/logs/{error,access}.log`
- 数据库: `/opt/longmarch-dev/001 项目源码/data/longmarch.db`

### 知常轩（2026-08-10 域名重新划分）
- 测试域名：`https://zcxdev.zhichangxuan.com`（知常轩测试环境！注意：dev.zhichangxuan.com 是长征测试，勿混淆）
- 主域名: `https://zhichangxuan.com` / `https://www.zhichangxuan.com` → 知常轩主站
- 长征域名: 只用 `https://cz.zhichangxuan.com`（生产）+ `https://dev.zhichangxuan.com`（测试）
- 测试版路径: `/opt/zhichangxuan-dev/`，venv: `/opt/zhichangxuan-dev/venv/`，端口 5003
- systemd 服务: zhichangxuan-dev.service（gunicorn，wsgi:app）
- 静态文件: `/opt/zhichangxuan-dev/001 项目源码/static/`，道德经子页 static/ddj/
- 数据库: `/opt/zhichangxuan-dev/001 项目源码/data/zhichangxuan.db`（init_db.py 可重建）
- Nginx 配置: `/etc/nginx/sites-enabled/zhichangxuan`（三个 server 块），旧配置备份 `/etc/nginx/zhichangxuan.bak.*`

### 旧部署（已停用）
- 路径: `/root/longmarch/longmarch_app/`
- 说明: 数据已迁移至新环境，进程已停止

### 部署命令（生产）
cd /opt/longmarch-map && SECRET_KEY=<key> bash ./006\ build/deploy.sh（升级流程按版本管理文档，升级前读文档）

### 部署备选路径（GitHub 不可达时）
2026-08-04 发现本机网络无法连接 github.com:443，但服务器本身可以走通。备选流程：
1. 本地提交后 `git format-patch -1 HEAD -o .` 生成 patch 文件
2. `scp patch root@8.133.203.255:/tmp/` 传上去
3. SSH 上服务器：`cd /opt/longmarch-map && git checkout develop && git am /tmp/patch`
4. `systemctl restart longmarch-map` 重启服务
注意：服务器可能无 git 身份，需要先 `git config user.email/name`。
注：服务器上 github push 可能会报 “Invalid username or token”，表明远程仓库 token 失效，这个是另一个待解问题（不影响本路径）。

## 待办事项

- [x] 补充素材 — 各节点的高清历史照片（97张，覆盖全部29个节点）
- [x] 照片入库 — media 表 97 条记录，type=image, status=approved
- [x] develop 分支搭建 — 日常集成工作流就绪
- [x] 006 build/ 部署脚本 — deploy.sh, gunicorn_config.py, longmarch.service, wsgi.py
- [x] 服务器部署 — develop 分支部署到阿里云 ECS (8.133.203.255)，gunicorn 运行中
- [x] 数据库迁移 — 从旧部署 /root/longmarch/ 迁移到 /opt/longmarch-map/
- [ ] 增强数据 — 部分节点（长汀、通道、黎平等）诗词文章、典型故事为空，需补充
- [ ] 路线数据 — route_point 表可能为空，需初始化路线点
- [ ] 生产部署 — SECRET_KEY 安全加固、Nginx 反代配置、HTTPS
- [ ] 前端优化 — 留言板后端接口、星火投稿流程、管理后台完善

## 参考资源
- `照片获取指南.txt` — 百度百科各节点词条链接
- `node_data.json` — 完整的 25 节点历史数据
- `requirements.txt` — 仅 Flask + Werkzeug 依赖
