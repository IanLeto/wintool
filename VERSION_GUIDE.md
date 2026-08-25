# Wintool 版本梳理与优化指南

## 📋 版本概览

你的项目有 **3 个版本**，每个版本针对不同的使用场景：

| 版本 | 启动脚本 | 技术栈 | 使用场景 | 端口 |
|------|---------|--------|---------|------|
| **1. Spring Boot 版本（外网）** | `run.sh` | Java + Spring Boot + Vue 3 | 生产环境，需要 JDK/Maven | 8080 |
| **2. Python 内网版本** | `inner.sh` | Python Flask + Vue 3 | 内网环境，无需 JDK | 8080 + 5173 |
| **3. All 版本** | `all.sh` | 同时运行以上两个版本 | 开发/测试环境 | 8080 + 5173 |

---

## 🔍 详细版本分析

### 1️⃣ Spring Boot 版本（run.sh）

**技术栈：**
- 后端：Java + Spring Boot + Maven
- 前端：Vue 3 + Vite（需单独启动）
- 数据：关系型数据库（可选）

**特点：**
- ✅ 企业级架构，适合大型项目
- ✅ 性能好，可扩展性强
- ✅ 支持 dev/prod/build/clean 多种模式
- ❌ 需要 JDK 8+ 和 Maven
- ❌ 启动较慢

**启动方式：**
```bash
# 开发模式（默认）
./run.sh dev

# 生产模式（编译后运行）
./run.sh prod

# 仅编译
./run.sh build
```

**适用场景：**
- 生产环境部署
- 需要 Java 生态的项目
- 对性能和稳定性要求高

---

### 2️⃣ Python 内网版本（inner.sh）

**技术栈：**
- 后端：Python 3 + Flask
- 前端：Vue 3 + Vite（构建后的静态文件）
- 数据：JSON 文件存储

**特点：**
- ✅ 轻量级，无需 JDK/Maven
- ✅ 适合内网环境（无公网访问）
- ✅ 自动管理进程（PID 文件）
- ✅ 支持 Ctrl+C 优雅停止
- ✅ 功能完整：代码片段、K8s 管理、Kafka 消费、原型预览
- ❌ 需要 Python 3.7+ 和 Node.js

**启动方式：**
```bash
./inner.sh
# 按 Ctrl+C 停止所有服务
```

**服务列表：**
- Python 后端：http://localhost:8080
- Vue 前端：http://localhost:5173

**适用场景：**
- 内网环境部署
- 不想安装 JDK 的场景
- 快速开发和测试
- **推荐用于日常开发**

---

### 3️⃣ All 版本（all.sh）

**技术栈：**
- 同时运行以上两个版本

**特点：**
- ✅ 一键启动所有服务
- ✅ 自动管理进程
- ✅ 实时监控服务状态
- ❌ 资源占用大
- ❌ 端口冲突风险

**启动方式：**
```bash
./all.sh
# 按 Ctrl+C 停止所有服务
```

**服务列表：**
- 后端 (Spring Boot): http://localhost:8080
- 前端 (Vue 3): http://localhost:5173

**适用场景：**
- 开发环境，需要同时测试多个版本
- 功能对比测试
- **不推荐用于生产环境**

---

## 🎯 版本选择建议

### 日常开发 → **Python 内网版本（inner.sh）**
```bash
./inner.sh
```
- 启动快，资源占用少
- 功能完整，满足大部分需求
- 无需 JDK，环境简单

### 外网生产部署 → **Spring Boot 版本（run.sh）**
```bash
./run.sh prod
```
- 性能好，稳定性高
- 企业级架构
- 适合长期运行
- **适合外网环境**

### 全面测试 → **All 版本（all.sh）**
```bash
./all.sh
```
- 同时测试所有版本
- 功能对比验证

---

## 🔧 优化建议

### 1. 统一后端 API

**问题：**
- `backend-python/app.py`（880 行）功能完整
- `backend/wintool-backend`（Spring Boot）功能可能重复

**建议：**
```bash
# 选择一个主力后端
# 方案 A：以 Python 为主（推荐）
- 保留 backend-python/app.py
- 废弃 backend/wintool-backend
- 优点：轻量、快速、易维护

# 方案 B：以 Spring Boot 为主
- 将 Python 功能迁移到 Spring Boot
- 废弃 backend-python
- 优点：企业级、性能好
```

### 2. 简化启动脚本

**当前问题：**
- 4 个启动脚本，容易混淆
- 功能重叠

**优化方案：**
```bash
# 创建统一启动脚本
./start.sh [mode]

# 模式选项：
./start.sh dev      # 开发模式（Python 后端 + Vue 前端）
./start.sh prod     # 生产模式（Spring Boot）
./start.sh legacy   # Legacy 模式
./start.sh all      # 全部启动
```

### 3. 清理 Legacy 代码

**建议：**
```bash
# 1. 评估 legacy/ 目录中的工具
# 2. 将有用的工具迁移到新架构
# 3. 废弃不再使用的工具
# 4. 归档 legacy/ 目录
```

### 4. 统一数据存储

**当前问题：**
- Python 版本：JSON 文件（`code_snippets/snippets.json`）
- Spring Boot：可能使用数据库

**建议：**
```bash
# 统一使用 JSON 文件存储（简单场景）
# 或统一使用数据库（复杂场景）
```

### 5. 前端构建优化

**当前问题：**
- 前端需要单独启动（开发模式）
- 或需要先构建（生产模式）

**优化方案：**
```bash
# 在启动脚本中自动检测
if [ ! -d "frontend/dist" ]; then
    echo "前端未构建，正在构建..."
    cd frontend && npm run build && cd ..
fi
```

---

## 📊 版本对比表

| 特性 | Spring Boot（外网） | Python 内网 | All |
|------|------------|------------|-----|
| 启动速度 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| 资源占用 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| 功能完整性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 易用性 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 维护性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 生产就绪 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |

---

## 🚀 推荐使用方式

### 场景 1：日常开发
```bash
# 使用 Python 内网版本
./inner.sh

# 访问
http://localhost:5173  # 前端
http://localhost:8080  # 后端 API
```

### 场景 2：外网生产部署
```bash
# 使用 Spring Boot 版本
./run.sh prod

# 访问
http://your-server:8080
```

### 场景 3：内网部署（无 JDK）
```bash
# 1. 打包
./pack.sh

# 2. 上传到内网服务器
./deploy_to_inner.sh

# 3. 在服务器上启动
cd /root/workdir/wintool-inner-*/
./start.sh
```

---

## 📝 下一步行动

### 立即优化（推荐）

1. **确定主力版本**
   ```bash
   # 建议：以 Python 内网版本为主
   # 理由：轻量、功能完整、易维护
   ```

2. **创建统一启动脚本**
   ```bash
   # 创建 start.sh
   ./start.sh dev    # 默认使用 inner.sh
   ./start.sh prod   # 使用 run.sh prod
   ./start.sh legacy # 使用 run_simply.sh
   ```

3. **清理冗余代码**
   ```bash
   # 归档 legacy 目录
   mv legacy legacy.backup
   
   # 或删除不再使用的工具
   ```

4. **更新文档**
   ```bash
   # 更新 README.md
   # 说明各版本的用途和选择建议
   ```

### 长期优化

1. **统一后端架构**
   - 选择 Python 或 Spring Boot 作为唯一后端
   - 迁移功能，废弃另一个

2. **前端优化**
   - 自动构建检测
   - 热更新支持

3. **部署自动化**
   - Docker 化
   - CI/CD 流程

---

## 🆘 常见问题

### Q1: 我应该用哪个版本？
**A**: 日常开发用 `inner.sh`，生产部署用 `run.sh prod`

### Q2: All 版本有什么用？
**A**: 仅用于开发测试，不推荐生产使用

### Q3: 如何快速启动？
**A**: 
```bash
# 内网环境（推荐）
./inner.sh

# 外网生产环境
./run.sh prod
```

### Q4: 内网和外网版本有什么区别？
**A**: 
- **内网版本** (`inner.sh`): Python Flask 后端，无需 JDK，适合内网环境快速部署
- **外网版本** (`run.sh`): Spring Boot 后端，需要 JDK/Maven，性能更好，适合外网生产环境

---

**版本**: 1.0.0  
**更新时间**: 2026-08-03  
**作者**: Wintool Team
