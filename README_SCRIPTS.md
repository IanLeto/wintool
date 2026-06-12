# Wintool 启动脚本使用说明

本文档介绍 Wintool 项目中所有启动和管理脚本的使用方法。

## 📜 脚本列表

### 1. `all.sh` - 启动所有服务 ⭐

**用途**：一键启动前端、后端和 Legacy 版本的所有服务。

**使用方法**：
```bash
./all.sh
```

**功能特点**：
- ✅ 自动启动三个服务（后端、前端、Legacy）
- ✅ 后台运行，日志输出到 `.pids/` 目录
- ✅ 实时监控服务状态
- ✅ 按 `Ctrl+C` 可优雅停止所有服务
- ✅ 自动清理已停止的服务

**服务访问地址**：
- 后端 (Spring Boot): http://localhost:8080
- 前端 (Vue 3): http://localhost:5173
- Legacy (Flask): http://localhost:5000

**日志文件位置**：
- 后端日志: `.pids/backend.log`
- 前端日志: `.pids/frontend.log`
- Legacy 日志: `.pids/legacy.log`

---

### 2. `stop_all.sh` - 停止所有服务

**用途**：停止所有正在运行的服务。

**使用方法**：
```bash
./stop_all.sh
```

**功能特点**：
- ✅ 优雅停止所有服务
- ✅ 如果服务无响应，自动强制停止
- ✅ 清理 PID 文件
- ✅ 显示停止的服务数量

---

### 3. `run.sh` - 启动后端服务

**用途**：单独启动 Spring Boot 后端服务。

**使用方法**：
```bash
# 开发模式（默认）
./run.sh
./run.sh dev

# 生产模式（编译后运行）
./run.sh prod

# 仅编译
./run.sh build

# 清理编译文件
./run.sh clean
```

**访问地址**：
- API 服务: http://localhost:8080
- API 文档: http://localhost:8080/swagger-ui.html

---

### 4. `run_frontend.sh` - 启动前端服务

**用途**：单独启动 Vue 3 前端开发服务器。

**使用方法**：
```bash
./run_frontend.sh
```

**功能特点**：
- ✅ 自动检查并安装依赖
- ✅ 热重载支持
- ✅ 自动代理后端 API

**访问地址**：
- 前端页面: http://localhost:5173

---

### 5. `run_simply.sh` - 启动 Legacy 版本

**用途**：启动重构前的 Python Flask 版本。

**使用方法**：
```bash
./run_simply.sh
```

**适用场景**：
- 内网环境部署
- 不依赖 Node.js 和 Java
- 快速启动原有功能

**访问地址**：
- Legacy 服务: http://localhost:5000

---

## 🚀 快速开始

### 场景 1：开发环境 - 启动所有服务

```bash
# 一键启动所有服务
./all.sh

# 按 Ctrl+C 停止所有服务
# 或者在另一个终端执行
./stop_all.sh
```

### 场景 2：只开发前端

```bash
# 启动后端（提供 API）
./run.sh &

# 启动前端
./run_frontend.sh
```

### 场景 3：只开发后端

```bash
# 启动后端
./run.sh
```

### 场景 4：使用 Legacy 版本

```bash
# 启动 Legacy 版本
./run_simply.sh
```

---

## 📁 目录结构

```
wintool/
├── all.sh              # 启动所有服务
├── stop_all.sh         # 停止所有服务
├── run.sh              # 启动后端
├── run_frontend.sh     # 启动前端
├── run_simply.sh       # 启动 Legacy
├── .pids/              # PID 和日志文件目录（自动创建）
│   ├── backend.pid
│   ├── backend.log
│   ├── frontend.pid
│   ├── frontend.log
│   ├── legacy.pid
│   └── legacy.log
├── frontend/           # Vue 3 前端
├── backend/            # Spring Boot 后端
└── legacy/             # Python Flask Legacy 版本
```

---

## 🔧 环境要求

### 前端
- Node.js 14+
- npm 6+

### 后端
- Java JDK 8+
- Maven 3.6+

### Legacy
- Python 3.7+
- pip

---

## 💡 常见问题

### Q1: 端口被占用怎么办？

**前端端口冲突**：
- Vite 会自动尝试其他端口（5174, 5175...）

**后端端口冲突**：
- 修改 `backend/wintool-backend/src/main/resources/application.yml`
- 将 `server.port` 改为其他端口

**Legacy 端口冲突**：
- 修改 `legacy/app.py` 中的端口配置

### Q2: 如何查看服务日志？

```bash
# 查看后端日志
tail -f .pids/backend.log

# 查看前端日志
tail -f .pids/frontend.log

# 查看 Legacy 日志
tail -f .pids/legacy.log
```

### Q3: 服务启动失败怎么办？

1. 检查环境是否满足要求
2. 查看对应的日志文件
3. 确保端口未被占用
4. 尝试单独启动服务进行调试

### Q4: 如何在后台运行服务？

使用 `all.sh` 脚本会自动在后台运行所有服务。

如果需要单独后台运行某个服务：
```bash
# 后台运行后端
nohup ./run.sh > backend.log 2>&1 &

# 后台运行前端
nohup ./run_frontend.sh > frontend.log 2>&1 &
```

---

## 🎯 最佳实践

1. **开发时使用 `all.sh`**：一次性启动所有服务，方便调试
2. **生产环境使用 Docker**：更稳定和可控
3. **定期查看日志**：及时发现和解决问题
4. **使用 `stop_all.sh`**：确保服务完全停止，避免端口占用

---

## 📞 技术支持

如有问题，请查看：
- [主 README](./README.md)
- [重构计划](./REFACTOR_PLAN.md)
- [架构文档](./docs/ARCHITECTURE.md)

或提交 Issue 到项目仓库。
