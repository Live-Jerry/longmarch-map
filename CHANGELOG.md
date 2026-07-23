# 版本日志

版本日志由项目管理员维护。每次版本变更时，开发者在提交代码的同时更新此文件。

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
