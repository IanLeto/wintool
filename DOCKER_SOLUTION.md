# 利用远程 Pod 镜像在内网部署 Wintool 的方案

## 🎯 问题分析

**现状**：
- ✅ 远程开发 Pod 有 Python 环境（镜像：`docker-env`）
- ❌ 内网无法访问公网 Python 镜像
- ❌ 内网 Docker build 时找不到 Python 基础镜像
- 🎯 目标：利用远程 Pod 的镜像在内网容器化部署 Wintool

---

## ✅ 解决方案：镜像导出/导入

### 方案概述

1. **在远程 Pod 上**：导出 `docker-env` 镜像为 tar 文件
2. **传输到内网**：通过邮件/U盘/内网传输工具
3. **在内网**：导入镜像，基于此镜像构建 Wintool

---

## 📋 详细步骤

### 步骤 1：在远程 Pod 上导出镜像

```bash
# SSH 到远程 Pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# 或者直接 SSH（如果配置了）
ssh user@remote-pod

# 查看镜像
docker images | grep docker-env

# 导出镜像为 tar 文件
docker save docker-env:latest -o docker-env.tar

# 或者指定完整镜像名（如果有 registry）
docker save registry.example.com/docker-env:latest -o docker-env.tar

# 压缩以减小体积（可选）
gzip docker-env.tar
# 生成 docker-env.tar.gz

# 查看文件大小
ls -lh docker-env.tar*
```

**注意事项**：
- 镜像可能很大（几百 MB 到几 GB）
- 如果太大，考虑压缩或分卷压缩
- 确保有足够的磁盘空间

---

### 步骤 2：传输镜像到内网

#### 方案 A：通过邮件（如果镜像不大）

```bash
# 分卷压缩（每个 20MB）
split -b 20M docker-env.tar.gz docker-env.tar.gz.part-

# 生成多个文件：
# docker-env.tar.gz.part-aa
# docker-env.tar.gz.part-ab
# docker-env.tar.gz.part-ac
# ...

# 在内网合并
cat docker-env.tar.gz.part-* > docker-env.tar.gz
gunzip docker-env.tar.gz
```

#### 方案 B：通过 U 盘或内网文件传输

```bash
# 直接复制 docker-env.tar 或 docker-env.tar.gz
cp docker-env.tar.gz /path/to/usb/
```

#### 方案 C：通过 SCP/SFTP（如果内网和外网有跳板机）

```bash
# 从远程 Pod 传到跳板机
scp docker-env.tar.gz user@jumpserver:/tmp/

# 从跳板机传到内网
scp user@jumpserver:/tmp/docker-env.tar.gz /path/to/inner/
```

---

### 步骤 3：在内网导入镜像

```bash
# 解压（如果压缩了）
gunzip docker-env.tar.gz

# 导入镜像
docker load -i docker-env.tar

# 验证导入成功
docker images | grep docker-env

# 输出示例：
# docker-env    latest    abc123def456    2 weeks ago    500MB
```

---

### 步骤 4：创建 Wintool Dockerfile（基于导入的镜像）

创建 `Dockerfile.inner`：

```dockerfile
# 使用导入的 docker-env 镜像作为基础镜像
FROM docker-env:latest

# 设置工作目录
WORKDIR /app

# 复制 Wintool 文件
COPY backend-python/ /app/backend-python/
COPY frontend/dist/ /app/frontend/dist/
COPY data/ /app/data/
COPY kubeconfig.example /app/kubeconfig

# 安装 Python 依赖（如果 docker-env 没有）
# 注意：docker-env 可能已经有 Python，检查是否需要安装依赖
RUN python3 -m pip install --no-cache-dir \
    Flask==2.3.0 \
    Flask-CORS==4.0.0 \
    Werkzeug==2.3.0 \
    kafka-python==3.0.4 || true

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python3", "/app/backend-python/app.py"]
```

**如果 docker-env 镜像没有 pip**，使用离线安装：

```dockerfile
FROM docker-env:latest

WORKDIR /app

# 复制预下载的 wheel 文件
COPY libs/*.whl /tmp/wheels/

# 离线安装
RUN python3 -m pip install --no-index --find-links=/tmp/wheels/ \
    Flask Flask-CORS Werkzeug kafka-python

# 复制应用文件
COPY backend-python/ /app/backend-python/
COPY frontend/dist/ /app/frontend/dist/
COPY data/ /app/data/
COPY kubeconfig.example /app/kubeconfig

EXPOSE 8080

CMD ["python3", "/app/backend-python/app.py"]
```

---

### 步骤 5：构建 Wintool 镜像

```bash
# 在内网构建
docker build -f Dockerfile.inner -t wintool:latest .

# 验证构建成功
docker images | grep wintool
```

---

### 步骤 6：运行容器

```bash
# 运行容器
docker run -d \
  --name wintool \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/code_snippets:/app/code_snippets \
  -v $(pwd)/kubeconfig:/app/kubeconfig \
  wintool:latest

# 查看日志
docker logs -f wintool

# 访问
curl http://localhost:8080/health
```

---

## 🔧 完整自动化脚本

### 1. 远程 Pod 导出脚本 (`export_image.sh`)

```bash
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
echo "  2. 在内网执行: docker load -i docker-env.tar"
echo "=========================================="
```

### 2. 内网导入脚本 (`import_image.sh`)

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "  导入 docker-env 镜像"
echo "=========================================="

TAR_FILE="docker-env.tar.gz"

if [ ! -f "$TAR_FILE" ]; then
    echo "[ERROR] 文件 $TAR_FILE 不存在！"
    exit 1
fi

echo "[INFO] 解压镜像..."
gunzip $TAR_FILE

echo "[INFO] 导入镜像..."
docker load -i docker-env.tar

echo "[INFO] 验证导入..."
docker images | grep docker-env

echo ""
echo "=========================================="
echo "  导入完成！"
echo "  下一步："
echo "  1. 构建 Wintool: docker build -f Dockerfile.inner -t wintool:latest ."
echo "  2. 运行容器: docker run -d -p 8080:8080 wintool:latest"
echo "=========================================="
```

### 3. 内网构建脚本 (`build_inner.sh`)

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "  构建 Wintool 内网镜像"
echo "=========================================="

# 检查 docker-env 镜像是否存在
if ! docker images | grep -q "docker-env"; then
    echo "[ERROR] 基础镜像 docker-env 不存在！"
    echo "[INFO] 请先执行: ./import_image.sh"
    exit 1
fi

# 构建前端
echo "[INFO] 构建前端..."
cd frontend
npm run build
cd ..

# 构建 Docker 镜像
echo "[INFO] 构建 Docker 镜像..."
docker build -f Dockerfile.inner -t wintool:latest .

echo "[INFO] 构建完成！"
docker images | grep wintool

echo ""
echo "=========================================="
echo "  运行容器："
echo "  docker run -d -p 8080:8080 --name wintool wintool:latest"
echo "=========================================="
```

---

## 📦 完整部署包结构

```
wintool-inner-docker/
├── docker-env.tar.gz          # 导出的基础镜像
├── import_image.sh            # 导入镜像脚本
├── build_inner.sh             # 构建脚本
├── Dockerfile.inner           # Dockerfile
├── backend-python/            # Python 后端
│   └── app.py
├── frontend/                  # 前端源码
│   └── dist/                  # 构建产物
├── data/                      # 数据文件
├── libs/                      # Python 依赖（wheel 文件）
│   ├── Flask-2.3.0-py3-none-any.whl
│   ├── Flask_Cors-4.0.0-py2.py3-none-any.whl
│   └── kafka_python-3.0.4-py3-none-any.whl
├── kubeconfig.example         # K8s 配置示例
└── README_DOCKER.md           # 部署说明
```

---

## 🎯 优化方案

### 方案 A：多阶段构建（推荐）

```dockerfile
# 第一阶段：构建前端
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 第二阶段：运行时
FROM docker-env:latest
WORKDIR /app

# 复制前端构建产物
COPY --from=frontend-builder /app/dist /app/frontend/dist

# 复制后端
COPY backend-python/ /app/backend-python/
COPY data/ /app/data/
COPY kubeconfig.example /app/kubeconfig

# 安装 Python 依赖
COPY libs/*.whl /tmp/wheels/
RUN python3 -m pip install --no-index --find-links=/tmp/wheels/ \
    Flask Flask-CORS Werkzeug kafka-python

EXPOSE 8080
CMD ["python3", "/app/backend-python/app.py"]
```

**问题**：内网可能没有 Node.js 镜像

**解决**：在外网构建前端，只传输 `dist/` 目录

---

### 方案 B：完全离线构建

```bash
# 在外网准备所有依赖
cd frontend
npm run build
cd ..

# 下载 Python 依赖
pip download -d libs/ Flask==2.3.0 Flask-CORS==4.0.0 Werkzeug==2.3.0 kafka-python==3.0.4

# 打包
tar -czf wintool-inner-docker.tar.gz \
  Dockerfile.inner \
  backend-python/ \
  frontend/dist/ \
  data/ \
  libs/ \
  kubeconfig.example \
  build_inner.sh

# 传输到内网
# 1. docker-env.tar.gz（基础镜像）
# 2. wintool-inner-docker.tar.gz（应用代码）
```

---

## ⚠️ 注意事项

### 1. 检查 docker-env 镜像内容

```bash
# 在远程 Pod 上检查
docker run --rm -it docker-env:latest /bin/bash

# 检查 Python 版本
python3 --version

# 检查是否有 pip
pip3 --version

# 检查已安装的包
pip3 list

# 检查系统包管理器
apt --version  # Debian/Ubuntu
yum --version  # CentOS/RHEL
```

### 2. 镜像大小优化

```bash
# 查看镜像大小
docker images docker-env

# 如果太大，考虑：
# 1. 清理不必要的文件
# 2. 使用 docker-slim 压缩
# 3. 分层传输
```

### 3. 权限问题

```bash
# 确保有 Docker 权限
docker ps

# 如果没有权限
sudo usermod -aG docker $USER
# 重新登录
```

---

## 📝 总结

### ✅ 可行性分析

| 方案 | 可行性 | 优点 | 缺点 |
|------|--------|------|------|
| 导出/导入镜像 | ✅ 完全可行 | 简单直接，不需要网络 | 镜像文件大 |
| 多阶段构建 | ⚠️ 需要 Node 镜像 | 自动化程度高 | 内网可能没有 Node |
| 完全离线构建 | ✅ 完全可行 | 最灵活 | 需要手动准备依赖 |

### 🎯 推荐方案

**最佳方案**：导出/导入 + 完全离线构建

1. ✅ 在远程 Pod 导出 `docker-env` 镜像
2. ✅ 在外网构建前端（`npm run build`）
3. ✅ 在外网下载 Python 依赖（`pip download`）
4. ✅ 打包所有文件传输到内网
5. ✅ 在内网导入镜像并构建

**优点**：
- 不依赖内网网络
- 不需要内网有 Node.js
- 完全可控
- 可重复部署

---

## 🚀 快速开始

```bash
# 1. 在远程 Pod 上
./export_image.sh

# 2. 传输到内网
# docker-env.tar.gz

# 3. 在内网
./import_image.sh
./build_inner.sh

# 4. 运行
docker run -d -p 8080:8080 --name wintool wintool:latest

# 5. 访问
http://localhost:8080
```

---

**结论：完全可行！利用远程 Pod 的 `docker-env` 镜像，通过导出/导入的方式，可以在内网实现 Wintool 的容器化部署。**
