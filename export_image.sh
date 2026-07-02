#!/bin/bash
set -e

echo "=========================================="
echo "  导出 docker-env 镜像"
echo "=========================================="

IMAGE_NAME="docker-env:latest"
OUTPUT_FILE="docker-env.tar"

echo "[INFO] 检查镜像是否存在..."
if ! docker images | grep -q "docker-env"; then
    echo "[ERROR] 镜像 docker-env 不存在！"
    echo "[INFO] 可用镜像列表："
    docker images
    exit 1
fi

echo "[INFO] 导出镜像: $IMAGE_NAME"
docker save $IMAGE_NAME -o $OUTPUT_FILE

echo "[INFO] 压缩镜像..."
gzip $OUTPUT_FILE

echo "[INFO] 导出完成！"
ls -lh docker-env.tar.gz

echo ""
echo "=========================================="
echo "  下一步："
echo "  1. 将 docker-env.tar.gz 传输到内网"
echo "  2. 在内网执行: ./import_image.sh"
echo "=========================================="
