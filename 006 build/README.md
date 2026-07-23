# Build & Deploy Scripts

项目构建和部署脚本目录。

## 文件说明

| 文件 | 用途 |
|------|------|
| `deploy.sh` | Linux 部署脚本，拉取 develop 分支并部署 |
| `gunicorn_config.py` | Gunicorn WSGI 生产配置 |
| `longmarch.service` | systemd 服务单元文件 |
| `README.md` | 本文件 |

## 部署流程

首次部署到 Linux 服务器：

```bash
# 1. 上传脚本到服务器，首次初始化
./deploy.sh --init

# 2. 设置安全密钥后部署
SECRET_KEY=your-secure-key-here ./deploy.sh
```

日常更新（服务器上）：

```bash
cd /opt/longmarch-map
./006\ build/deploy.sh
```

## 手动启动

```bash
cd 001 项目源码
gunicorn -c ../006\ build/gunicorn_config.py wsgi:app
```
