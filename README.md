# Wintool - 前后端分离版本

一个基于 Vue 3 + Spring Boot 的文件处理工具集合。

## 📁 项目结构

```
wintool/
├── legacy/          # 原始 Python Flask 项目（已保留）
├── frontend/        # Vue 3 前端项目
├── backend/         # Spring Boot 后端项目
├── docs/            # 文档
└── README.md        # 本文件
```

## 🚀 快速开始

### 方式一：使用根目录脚本（推荐）

```bash
# 启动 Legacy 版本（重构前的 Python Flask 版本）
./run_simply.sh

# 打包 Legacy 版本（适用于内网部署）
./package.sh

# 启动前端（Vue 3）
./run_frontend.sh

# 启动后端（Spring Boot）
./run.sh              # 开发模式
./run.sh prod         # 生产模式
./run.sh build        # 仅编译
./run.sh clean        # 清理编译文件
```

### 方式二：手动启动

#### 前端开发

```bash
cd frontend
npm install          # 安装依赖（已完成）
npm run dev          # 启动开发服务器 (http://localhost:5173)
npm run build        # 生产构建
```

#### 后端开发

```bash
cd backend/wintool-backend
mvn clean install    # 编译项目
mvn spring-boot:run  # 启动服务 (http://localhost:8080)
```

#### Legacy 版本

```bash
cd legacy
./run.sh             # 启动 Python Flask 版本
./package.sh         # 打包为独立部署包
```

## 📋 技术栈

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite 5
- **UI 框架**: Element Plus
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **HTTP 客户端**: Axios

### 后端
- **框架**: Spring Boot 2.7.x
- **数据访问**: MyBatis + MyBatis-Plus
- **数据库**: MySQL 8.0 (可选)
- **API 文档**: Swagger/OpenAPI 3
- **工具**: Lombok, Hutool

## 📝 环境要求

### 已安装
- ✅ Node.js v22.14.0
- ✅ npm 10.9.2
- ✅ Java OpenJDK 18.0.2
- ✅ Maven 3.6.3

### 可选安装
- MySQL 8.0 (如果需要数据库功能)

## 🔧 开发指南

### 前端开发
1. 前端运行在 `http://localhost:5173`
2. 自动代理后端 API 到 `http://localhost:8080`
3. 支持热更新

### 后端开发
1. 后端运行在 `http://localhost:8080`
2. API 文档访问: `http://localhost:8080/swagger-ui.html`
3. 支持跨域请求

## 📚 文档

- [重构计划](./REFACTOR_PLAN.md) - 详细的重构计划和技术选型
- [架构文档](./docs/ARCHITECTURE.md) - 系统架构说明（待创建）
- [API 文档](./docs/API.md) - API 接口文档（待创建）

## 📜 启动脚本说明

### 根目录脚本

| 脚本 | 用途 | 说明 |
|------|------|------|
| `run_simply.sh` | 启动 Legacy 版本 | 运行重构前的 Python Flask 版本 |
| `package.sh` | 打包 Legacy 版本 | 创建可独立部署的压缩包（内网环境） |
| `run_frontend.sh` | 启动前端 | 运行 Vue 3 开发服务器 |
| `run.sh` | 启动后端 | 运行 Spring Boot 服务（支持多种模式） |

### 注意事项

- **Legacy 版本**：适用于内网环境，不依赖除 Python 外的任何内容
- **前端**：需要 Node.js 和 npm
- **后端**：需要 Java JDK 8+ 和 Maven

## 🎯 当前状态

### ✅ 已完成
- [x] 环境检查和依赖安装
- [x] 项目目录结构创建
- [x] 原始项目备份到 legacy/
- [x] Vue 3 前端项目初始化
- [x] Spring Boot 后端项目初始化
- [x] Element Plus 等前端依赖安装
- [x] 创建统一启动脚本

### 🔄 进行中
- [ ] 配置前端路由和状态管理
- [ ] 配置后端 Spring Boot 依赖
- [ ] 实现第一个示例工具

### 📅 待完成
- [ ] 数据库设计和配置
- [ ] 工具功能迁移
- [ ] Docker 容器化
- [ ] CI/CD 配置

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
