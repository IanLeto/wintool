# Wintool 启动指南

## 🚀 快速启动

### 内网版本（推荐用于日常开发）

**启动命令：**
```bash
./inner.sh
```

**技术栈：**
- 后端：Python Flask
- 前端：Vue 3 + Vite

**访问地址：**
- 前端：http://localhost:5173
- 后端 API：http://localhost:8080

**特点：**
- ✅ 启动快速（约 5-10 秒）
- ✅ 无需 JDK/Maven
- ✅ 适合内网环境
- ✅ 自动管理进程
- ✅ Ctrl+C 优雅停止

**依赖要求：**
- Python 3.7+
- Node.js（用于前端开发）

---

### 外网版本（推荐用于生产环境）

**启动命令：**
```bash
# 开发模式
./run.sh dev

# 生产模式（编译后运行）
./run.sh prod
```

**技术栈：**
- 后端：Java + Spring Boot
- 前端：Vue 3（需单独启动或构建）

**访问地址：**
- 后端：http://localhost:8080
- API 文档：http://localhost:8080/swagger-ui.html

**特点：**
- ✅ 企业级架构
- ✅ 性能优异
- ✅ 可扩展性强
- ✅ 适合外网生产环境

**依赖要求：**
- Java JDK 8+
- Maven 3.x

---

### 全部启动（开发测试用）

**启动命令：**
```bash
./all.sh
```

**说明：**
- 同时启动 Spring Boot 后端和 Vue 前端
- 仅用于开发测试
- 资源占用较大
- 不推荐生产使用

---

## 📋 版本对比

| 特性 | 内网版本 (inner.sh) | 外网版本 (run.sh) |
|------|-------------------|------------------|
| **环境** | 内网 | 外网生产 |
| **后端** | Python Flask | Java Spring Boot |
| **启动速度** | ⭐⭐⭐⭐⭐ 快 | ⭐⭐ 慢 |
| **资源占用** | ⭐⭐⭐⭐ 低 | ⭐⭐ 高 |
| **依赖** | Python + Node.js | JDK + Maven |
| **性能** | ⭐⭐⭐⭐ 良好 | ⭐⭐⭐⭐⭐ 优秀 |
| **适用场景** | 日常开发、内网部署 | 外网生产环境 |

---

## 🔧 停止服务

### 内网版本
```bash
# 按 Ctrl+C 停止所有服务
# 或手动停止：
kill $(cat .pids/backend-python.pid)
kill $(cat .pids/frontend.pid)
```

### 外网版本
```bash
# 按 Ctrl+C 停止
# 或找到进程并停止：
ps aux | grep java | grep wintool
kill <PID>
```

### 全部启动
```bash
# 按 Ctrl+C 停止所有服务
# 或使用停止脚本：
./stop_all.sh
```

---

## ❓ 常见问题

### Q: 我应该用哪个版本？
**A**: 
- 日常开发、内网环境 → `./inner.sh`
- 外网生产环境 → `./run.sh prod`

### Q: 端口被占用怎么办？
**A**: 
```bash
# 查看端口占用
lsof -i :8080
lsof -i :5173

# 停止占用端口的进程
kill <PID>
```

### Q: 如何查看日志？
**A**: 
```bash
# 内网版本
tail -f .pids/backend-python.log
tail -f .pids/frontend.log

# 外网版本（根据实际情况）
tail -f backend/wintool-backend/logs/application.log
```

---

**更新时间**: 2026-08-25  
**版本**: 2.0.0
