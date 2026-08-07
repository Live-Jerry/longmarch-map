# 版本日志

版本日志由项目管理员维护。每次版本变更时，开发者在提交代码的同时更新此文件。

## V2.1.4 (2026-08-07)

新增：首页页脚添加公安备案图标与备案编号，标题栏 logo 替换为含知常轩的新图

变更：
- 新增：index.html #icp-footer 追加公网安备链接（图标 + 陕公网安备61019002004143号）
- 新增：static/img/gongan_badge.png 公安备案图标（36x40，平台下载）
- 变更：static/img/title-banner.png 替换为「我走长征路橙色8」版（含知常轩字样），移除标题栏 .brand-name 文字
- 变更：style.css 删除 .brand-name 样式；静态资源版本号更新

## V2.1.3 (2026-08-05)

新增：标题栏 logo 右侧添加"知常轩"标识文字

变更：
- 新增：index.html 标题栏 logo 图片右侧添加「知常轩」文字
- 新增：style.css 添加 .brand-name 样式（楷体、竖线分隔、移动端自适应）

## V2.1.2 (2026-08-04)

新增：首页添加 ICP 备案号页脚

变更：
- 新增：index.html 底部固定小字条，显示"陕ICP备2026020519号"
- 新增：链接到工信部备案查询系统 https://beian.miit.gov.cn/
- 新增：style.css 添加 #icp-footer 样式，右下角定位，避开地图交互控件

## V2.1.1 (2026-07-30)

修复：重复点击漫游产生多个红点标记

变更：
- 修复：startAutowalk() 重复调用时清理旧标记和动画
- 修复：启动后禁用"开始"按钮，防止再次点击
- 修复：漫游中重新选择速度不会重新启用"开始"按钮
- 修复：漫游进行中不能修改速度，暂停后可改
- EC变更跟踪表第20条已同步更新

## V2.1.0 (2026-07-28)

前端修复与UI优化

变更：
- 修复：点击节点标记地图飞过去(map.instance.flyTo)
- 修复：autowalkState 未导出到 window 导致漫游检测失效
- 修复：移除 bindPopup 弹窗，点击标记直达信息面板
- 修复：showSpeedSelector 中提前展示 play-controls 的逻辑
- 修复：路线起点/终点 circleMarker 多余圆点已清除
- Logo: 更换为 我走长征路橙色6，副标题嵌入图片
- 标题框高度压缩，padding 调整
- EC变更跟踪表第19条已同步更新

## V2.0.1 (2026-07-25)

拆分 nginx 配置为生产和测试独立文件

变更：
- 删除混合配置 zhichangxuan.conf，拆分为 prd_zhichangxuan.conf 和 dev_zhichangxuan.conf
- 两个环境统一使用 zhichangxuan.com 证书

## V2.0.0 (2026-07-23)

生产部署与开发分支就绪

新增：
- develop 分支工作流：日常集成开发，main 分支稳定发布
- 006 build/ 部署目录：deploy.sh, gunicorn_config.py, longmarch.service, wsgi.py
- 阿里云 ECS 生产部署：gunicorn + 6 workers，端口 5000
- Nginx 反代配置：端口 80 代理到 5000，静态文件缓存，Gzip 压缩
- 数据库迁移：从旧部署 /root/longmarch/ 迁移到 /opt/longmarch-map/

修复：
- CHM 编码：CHM_INDEX_ENCODING = UTF-8 -> GBK
- 命名空间"重走长征路"：005 代码备份/ 目录含空格导致 Doxygen EXCLUDE 无效
- 模板标题：admin/*.html, login, register 中"重走长征路" -> "我走长征路"
- help.html 和用户手册文字修正，README.md 项目简介修正
- Gunicorn 入口：wsgi.py 解决 gunicorn 找不到 app 实例问题
- 所有 emoji 和 ** 粗体标记从文档中清除
- 漫游标记与节点偏移（root cause）：route_point 表 22 个节点坐标与 node 表不一致，漫游标记沿 route_point 坐标移动，而地图旗帜标记使用 node 表坐标，两者位置对不上
  - 修复：route_point 中有 node_id 的条目坐标直接覆盖为 node 表坐标
  - 中间插值点按新的节点坐标重新插值，保持路线形状
  - 涉及全部 4 支军队（830 个 route_point），验证后零偏差
- 防御性增强：arriveAtNode 到达节点时 snap 漫游标记到 node 表真实坐标
- 路线点索引映射（nodeRouteIndices）替代模糊坐标匹配

变更：
- 分支策略：develop（日常集成）+ main（稳定发布）
- 部署命令：SECRET_KEY=xxx bash 006 build/deploy.sh
- 登录页副标题：重走长征路 -> 我走长征路

技术栈：
- 生产 WSGI：gunicorn 26.0.0
- Nginx 1.28.3（反向代理）
- Python 3.14.4（阿里云 ECS Ubuntu）

---

## V2.0.0 (2026-07-16)

重大更新：
- 四支军队扩充：从 29 个中央红军节点扩展至 57 个节点
- 四支军队路线：全部 4 条路线 GeoJSON 数据，总计 1099 个路线点
- 军队选择器增强：新增"全部显示"选项，渐变色圆点，路线独立切换
- 星火拾遗去掉登录：无需登录即可提交
- 认证弹窗集成：登录/注册/忘记密码三合一弹窗
- 用户手册上线：/manual
- CHM 文档编码修复

变更说明：
- 版本号：V005/V1.0.1 -> V2.0.0
