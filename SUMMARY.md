# Wintool 版本清理总结

## 已完成的操作

### 1. 删除了纯 Python 实现版本（Legacy 版本）
- ✅ 删除 `/Users/ian/workdir/wintool/legacy/` 目录（包含所有旧版工具）
- ✅ 删除 `/Users/ian/workdir/wintool/run_simply.sh` 启动脚本

### 2. 更新了相关脚本和文档
- ✅ 更新 `all.sh`：移除了 Legacy 版本的启动逻辑
- ✅ 更新 `VERSION_GUIDE.md`：移除了 Legacy 版本的说明
- ✅ 创建 `STARTUP_GUIDE.md`：新增快速启动指南

---

## 当前版本结构

现在项目包含 **2 个核心版本** + **1 个开发测试版本**：

### 1️⃣ 内网版本（Python Flask + Vue 3）
**启动脚本：** `./inner.sh`

**技术栈：**
- 后端：Python Flask
- 前端：Vue 3 + Vite

**服务地址：**
- 前端：http://localhost:5173
- 后端 API：http://localhost:8080

**特点：**
- 启动快速（5-10 秒）
- 无需 JDK/Maven
- 适合内网环境
- 轻量级部署

**依赖：**
- Python 3.7+
- Node.js

**适用场景：**
- 日常开发
- 内网环境部署
- 快速原型验证

---

### 2️⃣ 外网版本（Spring Boot + Vue 3）
**启动脚本：** `./run.sh`

**技术栈：**
- 后端：Java Spring Boot
- 前端：Vue 3（需单独启动或构建）

**服务地址：**
- 后端：http://localhost:8080
- API 文档：http://localhost:8080/swagger-ui.html

**启动方式：**
```bash
# 开发模式
./run.sh dev

# 生产模式（编译后运行）
./run.sh prod
```

**特点：**
- 企业级架构
- 高性能
- 可扩展性强
- 生产就绪

**依赖：**
- Java JDK 8+
- Maven 3.x

**适用场景：**
- 外网生产环境
- 高并发场景
- 企业级应用

---

### 3️⃣ 开发测试版本（All）
**启动脚本：** `./all.sh`

**说明：**
- 同时启动 Spring Boot 后端和 Vue 前端
- 用于开发测试和版本对比
- 资源占用较大
- 不推荐生产使用

---

## 启动方式总结

| 场景 | 启动命令 | 访问地址 |
|------|---------|---------|
| **内网环境**（推荐日常开发） | `./inner.sh` | http://localhost:5173 |
| **外网开发** | `./run.sh dev` | http://localhost:8080 |
| **外网生产** | `./run.sh prod` | http://localhost:8080 |
| **全部启动**（测试用） | `./all.sh` | 多个端口 |

---

## 快速参考

### 内网版本（推荐）
```bash
# 启动
./inner.sh

# 访问
http://localhost:5173    # 前端
http://localhost:8080    # 后端 API

# 停止
按 Ctrl+C
```

### 外网版本
```bash
# 开发模式
./run.sh dev

# 生产模式
./run.sh prod

# 访问
http://localhost:8080              # 后端
http://localhost:8080/swagger-ui.html  # API 文档

# 停止
按 Ctrl+C
```

---

## 版本选择建议

### 选择内网版本（`inner.sh`）如果：
- ✅ 日常开发和测试
- ✅ 内网环境部署
- ✅ 不想安装 JDK/Maven
- ✅ 需要快速启动

### 选择外网版本（`run.sh`）如果：
- ✅ 外网生产环境
- ✅ 对性能要求高
- ✅ 需要企业级架构
- ✅ 高并发场景

---

## 相关文档

- **STARTUP_GUIDE.md** - 详细的启动指南
- **VERSION_GUIDE.md** - 版本详细对比和说明
- **DEPLOY_GUIDE.md** - 部署指南
- **DOCKER_SOLUTION.md** - Docker 部署方案
- **K8S_FEATURE_README.md** - Kubernetes 功能说明

---

**更新时间**: 2026-08-25  
**更新人**: Wintool Team
