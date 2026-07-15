# 环境搭建指南

## 快速开始

双击 `setup.bat`，脚本会自动：

1. 检查 Python 环境
2. 创建虚拟环境 `.venv`
3. 安装所有 Python 依赖
4. 检查 Git、Doxygen 等可选工具

## 手动安装步骤

### 1. 安装 Python

下载 Python 3.12+（建议 3.14）:
- https://www.python.org/downloads/
- 安装时 **务必勾选** "Add Python to PATH"

检查是否安装成功：
```cmd
python --version
pip --version
```

### 2. 安装 Python 依赖

```cmd
cd "001 项目源码"
pip install -r requirements.txt
```

### 3. 启动应用

```cmd
cd "001 项目源码"
python run.py
```

浏览器访问 http://127.0.0.1:5000

管理员账号：admin / admin123

## 可选工具

| 工具 | 用途 | 获取方式 |
|------|------|---------|
| Git | 版本管理 | https://git-scm.com/downloads |
| Doxygen | 项目文档生成 | `007 项目工具/doxygen-1.17.0.windows.x64.bin/doxygen.exe` |
| HTML Help Workshop | CHM 文档编译 | `007 项目工具/htmlhelp.exe`（安装后启用） |
| 7-Zip | 解压工具 | https://7-zip.org/ |

## 项目文件结构

```
D:\长征文化\
├── 001 项目源码/    — Flask 全栈应用
│   ├── api/         — REST API
│   ├── services/    — 业务逻辑
│   ├── static/      — 前端资源
│   └── templates/   — HTML 模板
├── 002 项目资源/    — 节点照片
├── 004 项目文档/    — 文档（含 Doxygen HTML + CHM）
├── 007 项目工具/    — 开发工具安装包
├── setup.bat        — 一键环境配置脚本
└── .gitignore
```
