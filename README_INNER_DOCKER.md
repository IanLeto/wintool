# Wintool 内网 Docker 部署指南

## 📋 概述

本指南介绍如何在**没有公网访问**的内网环境中，利用远程开发 Pod 的 `docker-env` 镜像部署 Wintool。

---

## 🎯 适用场景

- ✅ 内网无法访问公网 Docker Hub
- ✅ 内网无法拉取 Python 基础镜像
- ✅ 有一个远程开发 Pod，其镜像为 `docker-env`（包含 Python 环境）
- ✅ 可以通过邮件/U盘/跳板机在内外网之间传输文件

---

## 📦 准备工作

### 需要的文件

1. **docker-env.tar.gz** - 从远程 Pod 导出的基础镜像
2. **wintool 源码** - 本项目的所有文件
3. **Python 依赖** - Flask、Flask-CORS、Werkzeug、kafka-python 的 wheel 文件（可选）

---

## 🚀 部署步骤

### 步骤 1：在远程 Pod 上导出镜像

```bash
# SSH 到远程 Pod（或在 Pod 所在的机器上）
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# 或者如果 Pod 配置了 SSH
ssh user@remote-pod

# 执行导出脚本（如果已上传）
./export_image.sh

# 或者手动导出
docker save docker-env:latest -o docker-env.tar
gzip docker-env.tar
```

**输出**：`docker-env.tar.gz`（可能几百 MB 到几 GB）

---

### 步骤 2：传输文件到内网

#### 方案 A：通过邮件（镜像较小时）

```bash
# 分卷压缩（每个 20MB）
split -b 20M docker-env.tar.gz docker-env.tar.gz.part-

# 通过邮件发送所有 part 文件

# 在内网合并
cat docker-env.tar.gz.part-* > docker-env.tar.gz
```

#### 方案 B：通过 U 盘

```bash
# 直接复制到 U 盘
cp docker-env.tar.gz /Volumes/USB/

# 在内网复制出来
cp /Volumes/USB/docker-env.tar.gz ~/wintool/
```

#### 方案 C：通过跳板机

```bash
# 从远程传到跳板机
scp docker-env.tar.gz user@jumpserver:/tmp/

# 从跳板机传到内网
scp user@jumpserver:/tmp/docker-env.tar.gz ~/wintool/
```

---

### 步骤 3：在内网导入镜像

```bash
cd ~/wintool

# 执行导入脚本
./import_image.sh

# 验证导入成功
docker images | grep docker-env
```

**预期输出**：
```
docker-env    latest    abc123def456    2 weeks ago    500MB
```

---

### 步骤 4：准备 Python 依赖（可选）

如果 `docker-env` 镜像中没有 Flask 等依赖，需要在外网下载：

```bash
# 在外网执行
pip download -d libs/ \
  Flask==2.3.0 \
  Flask-CORS==4.0.0 \
  Werkzeug==2.3.0 \
  kafka-python==3.0.4

# 将 libs/ 目录传输到内网
```

**注意**：如果 `docker-env` 已经包含这些依赖，可以跳过此步骤。

---

### 步骤 5：构建前端（在外网或内网）

#### 在外网构建（推荐）

```bash
cd frontend
npm install
npm run build
cd ..

# 将 frontend/dist/ 目录传输到内网
```

#### 在内网构建（如果有 Node.js）

```bash
cd frontend
npm install
npm run build
cd ..
```

---

### 步骤 6：构建 Wintool 镜像

```bash
# 在内网执行
./build_inner_docker.sh
```

**脚本会自动**：
1. 检查 `docker-env` 镜像是否存在
2. 检查前端构建产物是否存在
3. 构建 Wintool Docker 镜像

**预期输出**：
```
[INFO] 构建完成！
wintool    latest    def789ghi012    Just now    550MB
```

---

### 步骤 7：运行容器

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

# 检查健康状态
docker ps | grep wintool
```

---

### 步骤 8：访问应用

```bash
# 在浏览器中打开
http://localhost:8080

# 或者使用 curl 测试
curl http://localhost:8080/health
```

**预期响应**：
```json
{"status": "healthy"}
```

---

## 📁 文件说明

### 核心文件

| 文件 | 说明 | 用途 |
|------|------|------|
| `Dockerfile.inner` | 内网 Dockerfile | 基于 docker-env 构建 |
| `export_image.sh` | 导出脚本 | 在远程 Pod 上导出镜像 |
| `import_image.sh` | 导入脚本 | 在内网导入镜像 |
| `build_inner_docker.sh` | 构建脚本 | 在内网构建 Wintool |
| `DOCKER_SOLUTION.md` | 详细方案 | 完整技术方案文档 |

### 目录结构

```
wintool/
├── Dockerfile.inner           # 内网 Dockerfile
├── export_image.sh            # 导出镜像脚本
├── import_image.sh            # 导入镜像脚本
├── build_inner_docker.sh      # 构建脚本
├── backend-python/            # Python 后端
│   ├── app.py
│   └── requirements.txt
├── frontend/                  # 前端源码
│   ├── dist/                  # 构建产物（需要）
│   ├── src/
│   └── package.json
├── data/                      # 数据文件
├── libs/                      # Python 依赖（可选）
│   ├── Flask-2.3.0-py3-none-any.whl
│   └── ...
├── kubeconfig.example         # K8s 配置示例
└── README_INNER_DOCKER.md     # 本文档
```

---

## 🔧 常见问题

### Q1: docker-env 镜像太大怎么办？

**A**: 可以压缩或分卷传输

```bash
# 分卷压缩（每个 50MB）
split -b 50M docker-env.tar.gz docker-env.tar.gz.part-

# 在内网合并
cat docker-env.tar.gz.part-* > docker-env.tar.gz
```

---

### Q2: 如何检查 docker-env 镜像中是否有 Python？

**A**: 在远程 Pod 上运行

```bash
docker run --rm -it docker-env:latest /bin/bash

# 检查 Python
python3 --version

# 检查 pip
pip3 --version

# 检查已安装的包
pip3 list
```

---

### Q3: 构建时提示找不到 libs 目录？

**A**: 有两种解决方案

**方案 1**：在外网下载依赖
```bash
pip download -d libs/ Flask Flask-CORS Werkzeug kafka-python
```

**方案 2**：如果 docker-env 已有依赖，选择 `y` 继续构建
```bash
是否继续构建（依赖可能已在 docker-env 中）？[y/N] y
```

---

### Q4: 容器启动失败怎么办？

**A**: 查看日志排查问题

```bash
# 查看容器日志
docker logs wintool

# 进入容器调试
docker exec -it wintool /bin/bash

# 检查 Python 环境
python3 --version
pip3 list

# 检查文件是否存在
ls -la /app/backend-python/
ls -la /app/frontend/dist/
```

---

### Q5: 如何更新 Wintool？

**A**: 重新构建镜像

```bash
# 停止并删除旧容器
docker stop wintool
docker rm wintool

# 删除旧镜像
docker rmi wintool:latest

# 重新构建
./build_inner_docker.sh

# 运行新容器
docker run -d -p 8080:8080 --name wintool wintool:latest
```

---

### Q6: 如何备份数据？

**A**: 数据存储在挂载的卷中

```bash
# 备份数据目录
tar -czf wintool-data-backup.tar.gz data/ code_snippets/

# 恢复数据
tar -xzf wintool-data-backup.tar.gz
```

---

## 🎯 完整部署流程总结

### 在远程 Pod 上（外网）

```bash
# 1. 导出镜像
./export_image.sh

# 2. 构建前端（可选）
cd frontend && npm run build && cd ..

# 3. 下载 Python 依赖（可选）
pip download -d libs/ Flask Flask-CORS Werkzeug kafka-python

# 4. 打包传输
tar -czf wintool-deploy.tar.gz \
  docker-env.tar.gz \
  Dockerfile.inner \
  import_image.sh \
  build_inner_docker.sh \
  backend-python/ \
  frontend/dist/ \
  data/ \
  libs/ \
  kubeconfig.example
```

### 在内网

```bash
# 1. 解压部署包
tar -xzf wintool-deploy.tar.gz
cd wintool

# 2. 导入镜像
./import_image.sh

# 3. 构建 Wintool
./build_inner_docker.sh

# 4. 运行容器
docker run -d -p 8080:8080 --name wintool \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/code_snippets:/app/code_snippets \
  -v $(pwd)/kubeconfig:/app/kubeconfig \
  wintool:latest

# 5. 访问应用
open http://localhost:8080
```

---

## 📊 资源需求

| 资源 | 最小要求 | 推荐配置 |
|------|---------|---------|
| CPU | 1 核 | 2 核 |
| 内存 | 512 MB | 1 GB |
| 磁盘 | 2 GB | 5 GB |
| Docker | 19.03+ | 20.10+ |

---

## 🔒 安全建议

1. **密码管理器数据加密**：使用 Web Crypto API 加密存储
2. **K8s 配置保护**：确保 kubeconfig 文件权限为 600
3. **容器网络隔离**：使用 Docker 网络隔离
4. **定期备份数据**：备份 data/ 和 code_snippets/ 目录

---

## 📝 相关文档

- [DOCKER_SOLUTION.md](./DOCKER_SOLUTION.md) - 详细技术方案
- [NO_PYTHON_ANALYSIS.md](./NO_PYTHON_ANALYSIS.md) - 无 Python 环境分析
- [DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md) - 通用部署指南

---

## 🆘 获取帮助

如果遇到问题：

1. 查看 [常见问题](#常见问题) 章节
2. 查看容器日志：`docker logs wintool`
3. 查看详细方案：[DOCKER_SOLUTION.md](./DOCKER_SOLUTION.md)

---

**祝部署顺利！🎉**
