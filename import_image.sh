#!/bin/bash
set -e

echo "=========================================="
echo "  导入 docker-env 镜像"
echo "=========================================="

TAR_FILE="docker-env.tar.gz"

if [ ! -f "$TAR_FILE" ]; then
    echo "[ERROR] 文件 $TAR_FILE 不存在！"
    echo "[INFO] 请确保已将 docker-env.tar.gz 传输到当前目录"
    exit 1
fi

echo "[INFO] 解压镜像..."
gunzip -k $TAR_FILE  # -k 保留原文件

echo "[INFO] 导入镜像..."
docker load -i docker-env.tar

echo "[INFO] 清理临时文件..."
rm -f docker-env.tar

echo "[INFO] 验证导入..."
docker images | grep docker-env

echo ""
echo "=========================================="
echo "  导入完成！"
echo "  下一步："
echo "  1. 构建 Wintool: ./build_inner_docker.sh"
echo "  2. 运行容器: docker run -d -p 8080:8080 --name wintool wintool:latest"
echo "=========================================="
