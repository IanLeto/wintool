# Wintool 前后端分离重构计划

## 🎯 目标
将现有的 Flask + Jinja2 单体应用重构为：
- **前端**：Vue 3 + Vite + Element Plus
- **后端**：Spring Boot + MyBatis + MySQL

## ✅ 环境检查结果

### 已安装的工具
- ✅ Node.js: v22.14.0
- ✅ npm: 10.9.2
- ✅ Java: OpenJDK 18.0.2
- ✅ Maven: 3.6.3

### 需要安装的工具
- ⚠️ Vue CLI (可选，使用 Vite 更快)
- ⚠️ MySQL (如果需要数据库)

## 📁 新项目结构

```
wintool/
├── legacy/                    # 保留原始 Python 项目
│   ├── app.py
│   ├── tools/
│   ├── templates/
│   ├── static/
│   └── data/
│
├── frontend/                  # Vue 3 前端项目
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   ├── components/       # 通用组件
│   │   ├── api/              # API 接口
│   │   ├── router/           # 路由配置
│   │   ├── store/            # 状态管理
│   │   └── utils/            # 工具函数
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── backend/                   # Spring Boot 后端项目
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/
│   │   │   │   └── com/wintool/
│   │   │   │       ├── controller/    # 控制器
│   │   │   │       ├── service/       # 业务逻辑
│   │   │   │       ├── mapper/        # 数据访问
│   │   │   │       ├── entity/        # 实体类
│   │   │   │       └── config/        # 配置类
│   │   │   └── resources/
│   │   │       ├── application.yml
│   │   │       └── mapper/            # MyBatis XML
│   │   └── test/
│   ├── pom.xml
│   └── data/                  # 数据文件（迁移自原项目）
│
├── docs/                      # 文档
│   ├── ARCHITECTURE.md        # 架构文档
│   ├── API.md                 # API 文档
│   └── MIGRATION.md           # 迁移指南
│
└── README.md                  # 项目说明
```

## 🔧 技术栈详情

### 前端技术栈
- **框架**：Vue 3 (Composition API)
- **构建工具**：Vite 5
- **UI 框架**：Element Plus
- **路由**：Vue Router 4
- **状态管理**：Pinia
- **HTTP 客户端**：Axios
- **代码规范**：ESLint + Prettier

### 后端技术栈
- **框架**：Spring Boot 2.7.x
- **数据访问**：MyBatis + MyBatis-Plus
- **数据库**：MySQL 8.0 (可选，部分工具继续使用文件存储)
- **API 文档**：Swagger/OpenAPI 3
- **安全**：Spring Security (可选)
- **工具**：Lombok, Hutool

## 📝 迁移策略

### 阶段一：环境搭建（当前阶段）
1. ✅ 检查环境依赖
2. 🔄 创建项目目录结构
3. 🔄 初始化 Vue 3 前端项目
4. 🔄 初始化 Spring Boot 后端项目
5. 🔄 配置开发环境

### 阶段二：核心功能迁移
1. 迁移工具基类 (BaseTool → 后端抽象类)
2. 迁移简单工具（文本查看器、提示词管理等）
3. 实现前端通用组件（工具卡片、表单等）
4. 实现后端通用接口（文件上传、下载等）

### 阶段三：复杂功能迁移
1. 迁移体重管理工具（需要数据库）
2. 迁移影视收藏工具
3. 迁移批量解压工具
4. 迁移 Kafka 工具

### 阶段四：优化和部署
1. 性能优化
2. 安全加固
3. Docker 容器化
4. CI/CD 配置

## 🚀 开发流程

### 前端开发
```bash
cd frontend
npm install
npm run dev      # 开发模式（http://localhost:5173）
npm run build    # 生产构建
```

### 后端开发
```bash
cd backend
mvn clean install
mvn spring-boot:run  # 启动服务（http://localhost:8080）
```

### 联调开发
- 前端代理配置：`vite.config.js` 中配置 proxy
- 后端跨域配置：`CorsConfig.java`

## 📊 数据迁移策略

### 文件存储工具（无需数据库）
- 文本查看器 → 继续使用文件系统
- 提示词管理 → 继续使用文件系统
- 影视收藏 → 继续使用 JSON 文件

### 需要数据库的工具
- 体重管理 → 迁移到 MySQL
- 密码管理 → 迁移到 MySQL（加密存储）
- 命令片段 → 可选（文件或数据库）

## 🔐 安全考虑

1. **认证授权**：Spring Security + JWT
2. **数据加密**：敏感数据加密存储
3. **HTTPS**：生产环境强制 HTTPS
4. **CORS**：配置允许的前端域名
5. **文件上传**：限制文件类型和大小

## 📦 部署方案

### 开发环境
- 前端：Vite Dev Server (5173)
- 后端：Spring Boot (8080)

### 生产环境
- 前端：Nginx 静态托管
- 后端：Spring Boot JAR + Systemd
- 数据库：MySQL 8.0

### Docker 部署
```yaml
services:
  frontend:
    image: wintool-frontend
    ports: ["80:80"]
  
  backend:
    image: wintool-backend
    ports: ["8080:8080"]
  
  mysql:
    image: mysql:8.0
    volumes: ["./data:/var/lib/mysql"]
```

## ⚠️ 注意事项

1. **保留原项目**：所有原始代码移动到 `legacy/` 目录
2. **渐进迁移**：一次迁移一个工具，确保功能正常
3. **API 设计**：RESTful 风格，统一响应格式
4. **错误处理**：全局异常处理，友好的错误提示
5. **日志记录**：使用 SLF4J + Logback

## 🎯 下一步行动

1. 创建项目目录结构
2. 初始化 Vue 3 前端项目
3. 初始化 Spring Boot 后端项目
4. 配置开发环境和工具
5. 实现第一个示例工具（文本查看器）
