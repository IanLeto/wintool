#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# 一键部署到内网服务器脚本
# 用途：从 Windows 通过 SSH 上传并部署到 Linux 服务器

set -euo pipefail

# 配置参数
SERVER_IP="1.1.1.1"
SERVER_USER="root"
SERVER_PASSWORD="123"
REMOTE_DIR="/root/workdir"
ZIP_PASSWORD="123"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $*"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
echo_title() { echo -e "${BLUE}$*${NC}"; }

echo_title "========================================="
echo_title "  Wintool 内网部署脚本"
echo_title "========================================="
echo ""

# 查找最新的压缩包
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LATEST_ZIP=$(ls -t "$SCRIPT_DIR"/wintool-inner-*.zip 2>/dev/null | head -1)

if [[ -z "$LATEST_ZIP" ]]; then
    echo_error "未找到打包文件"
    echo_error "请先运行: ./pack.sh"
    exit 1
fi

ZIP_NAME=$(basename "$LATEST_ZIP")
echo_info "找到压缩包: $ZIP_NAME"
echo_info "文件大小: $(du -h "$LATEST_ZIP" | cut -f1)"
echo ""

# 检查 sshpass（用于自动输入密码）
if ! command -v sshpass >/dev/null 2>&1; then
    echo_warn "未找到 sshpass，将使用交互式密码输入"
    echo_warn "建议安装 sshpass: brew install sshpass (macOS) 或 apt-get install sshpass (Linux)"
    echo ""
    USE_SSHPASS=false
else
    USE_SSHPASS=true
fi

# 上传文件
echo_info "开始上传到服务器..."
echo_info "  服务器: $SERVER_USER@$SERVER_IP"
echo_info "  目标目录: $REMOTE_DIR"
echo ""

if [[ "$USE_SSHPASS" == true ]]; then
    # 使用 sshpass 自动输入密码
    if sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no "$LATEST_ZIP" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"; then
        echo_info "上传成功！"
    else
        echo_error "上传失败"
        exit 1
    fi
else
    # 交互式输入密码
    echo_warn "请输入服务器密码: $SERVER_PASSWORD"
    if scp -o StrictHostKeyChecking=no "$LATEST_ZIP" "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/"; then
        echo_info "上传成功！"
    else
        echo_error "上传失败"
        exit 1
    fi
fi

echo ""
echo_info "开始远程部署..."

# 远程执行命令
REMOTE_COMMANDS=$(cat <<EOF
cd $REMOTE_DIR

# 检查 unzip
if ! command -v unzip >/dev/null 2>&1; then
    echo "[ERROR] 未找到 unzip 命令"
    echo "[INFO] 请先安装: yum install unzip 或 apt-get install unzip"
    exit 1
fi

# 解压（带密码）
echo "[INFO] 解压文件..."
if unzip -P $ZIP_PASSWORD -o $ZIP_NAME; then
    echo "[INFO] 解压成功"
else
    echo "[ERROR] 解压失败"
    exit 1
fi

# 进入解压目录
EXTRACT_DIR=\$(basename $ZIP_NAME .zip)
cd \$EXTRACT_DIR

# 链接系统默认的 kubeconfig
echo "[INFO] 配置 K8s..."
if [[ -f "\$HOME/.kube/config" ]]; then
    ln -sf "\$HOME/.kube/config" ./kubeconfig
    echo "[INFO] 已链接 K8s 配置: \$HOME/.kube/config"
elif [[ -f "/etc/kubernetes/admin.conf" ]]; then
    ln -sf "/etc/kubernetes/admin.conf" ./kubeconfig
    echo "[INFO] 已链接 K8s 配置: /etc/kubernetes/admin.conf"
else
    echo "[WARN] 未找到 K8s 配置文件"
    echo "[WARN] 请手动创建或链接 kubeconfig 文件"
fi

# 设置权限
chmod +x start.sh

# 显示信息
echo ""
echo "========================================="
echo "  部署完成！"
echo "========================================="
echo ""
echo "[INFO] 部署目录: $REMOTE_DIR/\$EXTRACT_DIR"
echo "[INFO] 启动命令: cd $REMOTE_DIR/\$EXTRACT_DIR && ./start.sh"
echo ""
echo "[INFO] 或者直接运行:"
echo "  cd $REMOTE_DIR/\$EXTRACT_DIR"
echo "  ./start.sh"
echo ""
EOF
)

if [[ "$USE_SSHPASS" == true ]]; then
    # 使用 sshpass 自动输入密码
    if sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "$REMOTE_COMMANDS"; then
        echo ""
        echo_title "========================================="
        echo_title "  部署成功！"
        echo_title "========================================="
        echo ""
        echo_info "下一步操作："
        echo_info "  1. SSH 登录服务器: ssh $SERVER_USER@$SERVER_IP"
        echo_info "  2. 进入目录: cd $REMOTE_DIR/$(basename "$ZIP_NAME" .zip)"
        echo_info "  3. 启动服务: ./start.sh"
        echo_info "  4. 访问应用: http://$SERVER_IP:8080"
        echo ""
    else
        echo_error "远程部署失败"
        exit 1
    fi
else
    # 交互式输入密码
    echo_warn "请输入服务器密码: $SERVER_PASSWORD"
    if ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "$REMOTE_COMMANDS"; then
        echo ""
        echo_title "========================================="
        echo_title "  部署成功！"
        echo_title "========================================="
        echo ""
        echo_info "下一步操作："
        echo_info "  1. SSH 登录服务器: ssh $SERVER_USER@$SERVER_IP"
        echo_info "  2. 进入目录: cd $REMOTE_DIR/$(basename "$ZIP_NAME" .zip)"
        echo_info "  3. 启动服务: ./start.sh"
        echo_info "  4. 访问应用: http://$SERVER_IP:8080"
        echo ""
    else
        echo_error "远程部署失败"
        exit 1
    fi
fi
