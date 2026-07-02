#!/bin/bash
set -e

echo "=========================================="
echo "  构建 Wintool 内网 Docker 镜像"
echo "=========================================="

# 检查 docker-env 镜像是否存在
echo "[INFO] 检查基础镜像..."
if ! docker images | grep -q "docker-env"; then
    echo "[ERROR] 基础镜像 docker-env 不存在！"
    echo "[INFO] 请先执行: ./import_image.sh"
    exit 1
fi

# 检查前端构建产物是否存在
if [ ! -d "frontend/dist" ]; then
    echo "[WARN] 前端构建产物不存在，开始构建前端..."
    cd frontend
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        echo "[INFO] 安装前端依赖..."
        npm install
    fi
    
    echo "[INFO] 构建前端..."
    npm run build
    cd ..
else
    echo "[INFO] 前端构建产物已存在"
fi

# 检查 libs 目录是否存在
if [ ! -d "libs" ]; then
    echo "[WARN] Python 依赖目录 libs/ 不存在"
    echo "[INFO] 创建 libs 目录..."
    mkdir -p libs
    
    echo "[WARN] 请确保已下载 Python 依赖到 libs/ 目录"
    echo "[INFO] 可以在外网执行："
    echo "       pip download -d libs/ Flask==2.3.0 Flask-CORS==4.0.0 Werkzeug==2.3.0 kafka-python==3.0.4"
    echo ""
    read -p "是否继续构建（依赖可能已在 docker-env 中）？[y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 构建 Docker 镜像
echo "[INFO] 构建 Docker 镜像..."
docker build -f Dockerfile.inner -t wintool:latest .

echo "[INFO] 构建完成！"
docker images | grep wintool

echo ""
echo "=========================================="
echo "  构建成功！"
echo ""
echo "  运行容器："
echo "  docker run -d -p 8080:8080 --name wintool \\"
echo "    -v \$(pwd)/data:/app/data \\"
echo "    -v \$(pwd)/code_snippets:/app/code_snippets \\"
echo "    -v \$(pwd)/kubeconfig:/app/kubeconfig \\"
echo "    wintool:latest"
echo ""
echo "  查看日志："
echo "  docker logs -f wintool"
echo ""
echo "  访问应用："
echo "  http://localhost:8080"
echo "=========================================="
