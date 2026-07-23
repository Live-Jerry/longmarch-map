#!/bin/bash
#=======================================
# 长征文化数字地图 - 部署脚本
# 用途: 从 develop 分支拉取最新代码并部署到生产环境
# 用法:
#   ./deploy.sh                    # 常规部署
#   ./deploy.sh --init             # 首次部署（创建目录结构等）
#   SECRET_KEY=xxx ./deploy.sh     # 指定密钥部署
#=======================================
set -euo pipefail

APP_NAME="longmarch-map"
BRANCH="develop"
REPO_URL="https://github.com/Live-Jerry/longmarch-map.git"
PROJECT_DIR="/opt/${APP_NAME}"
VENV_DIR="${PROJECT_DIR}/venv"
LOG_DIR="${PROJECT_DIR}/logs"
DATA_DIR="${PROJECT_DIR}/data"
SECRET_KEY="${SECRET_KEY:-longmarch-secret-key-2026}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

#=======================================
# 首次初始化
#=======================================
do_init() {
    log "首次部署初始化..."

    # 安装系统依赖
    apt-get update -y
    apt-get install -y python3 python3-pip python3-venv nginx git

    # 创建项目目录
    mkdir -p "${PROJECT_DIR}"
    mkdir -p "${LOG_DIR}"
    mkdir -p "${DATA_DIR}"

    # 克隆项目
    if [ ! -d "${PROJECT_DIR}/.git" ]; then
        git clone -b "${BRANCH}" "${REPO_URL}" "${PROJECT_DIR}"
    fi

    # 创建 Python 虚拟环境
    python3 -m venv "${VENV_DIR}"

    # 创建日志目录
    mkdir -p "${LOG_DIR}"

    log "初始化完成。请设置 SECRET_KEY 环境变量，然后重新运行 deploy.sh"
}

#=======================================
# 部署应用
#=======================================
do_deploy() {
    log "开始部署 ${APP_NAME} (分支: ${BRANCH})..."

    # 检查目录
    [ -d "${PROJECT_DIR}" ] || err "项目目录不存在，请先运行 ./deploy.sh --init"

    cd "${PROJECT_DIR}"

    # 拉取最新代码
    log "拉取最新代码..."
    git fetch origin
    git checkout "${BRANCH}"
    git pull origin "${BRANCH}"

    # 安装/更新 Python 依赖
    log "安装 Python 依赖..."
    "${VENV_DIR}/bin/pip" install --upgrade pip
    "${VENV_DIR}/bin/pip" install -r "${PROJECT_DIR}/001 项目源码/requirements.txt"
    "${VENV_DIR}/bin/pip" install gunicorn  # 生产 WSGI 服务器

    # 确保数据库和上传目录存在
    mkdir -p "${PROJECT_DIR}/001 项目源码/static/uploads"
    mkdir -p "${LOG_DIR}"

    # 停止旧进程
    log "停止旧服务..."
    systemctl stop "${APP_NAME}" 2>/dev/null || true
    pkill -f "gunicorn.*longmarch" 2>/dev/null || true
    sleep 1

    # 启动新服务
    log "启动新服务..."
    cd "${PROJECT_DIR}/001 项目源码"
    export FLASK_ENV=production
    export SECRET_KEY="${SECRET_KEY}"

    "${VENV_DIR}/bin/gunicorn" \
        -c "${PROJECT_DIR}/006 build/gunicorn_config.py" \
        app:app \
        --daemon

    sleep 2

    # 检查是否启动成功
    if pgrep -f "gunicorn.*longmarch" > /dev/null; then
        log "部署成功！应用已在端口 5000 启动"
        log "查看日志: tail -f ${LOG_DIR}/error.log"
    else
        err "启动失败，请检查日志: ${LOG_DIR}/error.log"
    fi
}

#=======================================
# 查看状态
#=======================================
do_status() {
    echo "=== 应用状态 ==="
    if pgrep -f "gunicorn.*longmarch" > /dev/null; then
        echo "状态: 运行中"
        ps aux | grep "gunicorn" | grep -v grep
    else
        echo "状态: 未运行"
    fi
    echo ""
    echo "=== 日志 ==="
    if [ -f "${LOG_DIR}/error.log" ]; then
        tail -5 "${LOG_DIR}/error.log"
    fi
}

#=======================================
# 主入口
#=======================================
case "${1:-}" in
    --init)
        do_init
        ;;
    --status)
        do_status
        ;;
    --help|-h)
        echo "用法: ./deploy.sh [选项]"
        echo "  (无参数)   常规部署（拉取 develop 分支并重启）"
        echo "  --init     首次部署初始化（安装依赖、创建目录）"
        echo "  --status   查看应用状态"
        echo "  --help     显示此帮助"
        ;;
    *)
        do_deploy
        ;;
esac
