# Wintool 架构文档

## 项目概述

Wintool 是一个基于 Flask 的 Web 工具集合，采用可插拔架构设计，支持快速添加新工具而不影响现有功能。

## 核心设计原则

### 1. 错误隔离
- **工具级隔离**：单个工具的错误不会影响其他工具
- **加载时隔离**：工具加载失败时，其他工具继续正常工作
- **运行时隔离**：工具运行时错误被捕获，不会导致整个应用崩溃

### 2. 统一启动
- **一键启动**：无论开发环境还是生产环境，都使用 `./run.sh` 启动
- **自动检测**：自动检测 Python 环境（虚拟环境 > 系统 Python）
- **依赖管理**：自动检查并安装依赖

### 3. 可插拔架构
- **工具独立**：每个工具都是独立的模块
- **统一接口**：所有工具继承 `BaseTool` 基类
- **自动注册**：工具自动注册到应用中

## 目录结构

```
wintool/
├── app.py                  # 主应用入口
├── run.sh                  # 统一启动脚本
├── package.sh              # 打包脚本
├── requirements.txt        # Python 依赖
├── README.md              # 项目说明
│
├── tools/                  # 工具模块目录
│   ├── __init__.py        # 工具注册
│   ├── base.py            # 基类定义
│   ├── text_viewer.py     # 文本阅览工具
│   ├── media_shelf.py     # 影视收藏工具
│   ├── prompt_bank.py     # 提示词收纳工具
│   ├── body_weight.py     # 体重管理工具
│   └── ...                # 其他工具
│
├── static/                 # 静态资源
│   ├── app.js             # 前端 JavaScript
│   ├── style.css          # 样式文件
│   └── path_helpers.js    # 路径辅助工具
│
├── templates/              # HTML 模板
│   ├── index.html         # 首页
│   └── tool.html          # 工具页面模板
│
├── data/                   # 数据目录
│   ├── text_documents/    # 文本文件
│   ├── work_journals/     # 工作日志
│   ├── media_shelf/       # 影视数据
│   ├── prompt_bank/       # 提示词数据
│   └── ...                # 其他数据
│
├── scripts/                # 辅助脚本
│   └── path_picker.py     # 路径选择器
│
└── docs/                   # 文档目录
    ├── ARCHITECTURE.md    # 架构文档（本文件）
    └── DEVELOPMENT.md     # 开发指南
```

## 工具开发规范

### 1. 创建新工具

每个工具必须：
1. 继承 `BaseTool` 基类
2. 定义 `TOOL_ID` 和 `TOOL_NAME`
3. 实现 `get_form_html()` 方法
4. 实现 `register_routes()` 方法

示例：

```python
from .base import BaseTool
from flask import Blueprint, jsonify, request

class MyTool(BaseTool):
    TOOL_ID = "my_tool"
    TOOL_NAME = "我的工具"
    
    @classmethod
    def get_form_html(cls) -> str:
        return """
        <div class="tool-form">
            <h3>我的工具</h3>
            <button id="my-btn">点击</button>
        </div>
        """
    
    @classmethod
    def register_routes(cls, bp: Blueprint):
        @bp.route("/action", methods=["POST"])
        def action():
            # 处理逻辑
            return jsonify({"ok": True})
```

### 2. 注册工具

在 `tools/__init__.py` 中添加：

```python
from .my_tool import MyTool

TOOLS = [
    # ... 其他工具
    MyTool,
]
```

### 3. 错误处理

工具内部应该捕获并处理错误：

```python
@bp.route("/action", methods=["POST"])
def action():
    try:
        # 业务逻辑
        result = do_something()
        return jsonify({"ok": True, "data": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
```

## 启动流程

### 开发环境

```bash
# 1. 创建虚拟环境（首次）
python3 -m venv .venv

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
./run.sh
```

### 生产环境

```bash
# 1. 打包
./package.sh

# 2. 传输到服务器
scp build/wintool_*.tar.gz user@server:/path/

# 3. 解压
tar -xzf wintool_*.tar.gz

# 4. 启动
cd wintool_*/
./start.sh
```

## 错误隔离机制

### 1. 工具加载隔离

在 `app.py` 中，工具注册使用 try-except 包裹：

```python
def _register_tool_routes():
    for tool_cls in TOOLS:
        try:
            bp = Blueprint(...)
            tool_cls.register_routes(bp)
            app.register_blueprint(bp)
            print(f"✓ 工具已加载: {tool_cls.TOOL_NAME}")
        except Exception as e:
            print(f"✗ 工具加载失败: {tool_cls.TOOL_NAME}")
            print(f"  错误: {str(e)}")
            # 继续加载其他工具
```

### 2. 路由级隔离

每个工具的路由都在独立的 Blueprint 中：

```python
bp = Blueprint(
    f"tool_{tool_cls.TOOL_ID}", 
    __name__, 
    url_prefix=f"/api/tools/{tool_cls.TOOL_ID}"
)
```

### 3. 数据隔离

每个工具的数据存储在独立的目录中：

```
data/
├── text_documents/     # 文本阅览工具
├── work_journals/      # 工作日志工具
├── media_shelf/        # 影视收藏工具
└── prompt_bank/        # 提示词收纳工具
```

## 扩展性设计

### 1. 添加数据库支持

未来可以添加数据库支持，但保持向后兼容：

```python
class BaseTool:
    # 可选的数据库连接
    db = None
    
    @classmethod
    def use_database(cls):
        """工具可以选择是否使用数据库"""
        return False
```

### 2. 前后端分离

当前架构已经支持前后端分离：
- 前端：纯 JavaScript，通过 API 与后端通信
- 后端：Flask REST API

未来可以：
- 将前端迁移到 React/Vue
- 后端保持不变，只提供 API

### 3. 微服务化

每个工具都可以独立部署为微服务：
- 工具之间通过 HTTP API 通信
- 使用 API Gateway 统一入口

## 性能优化

### 1. 静态资源缓存

```python
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1年
```

### 2. 数据库连接池

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
```

### 3. 异步任务

对于耗时操作，使用后台任务：

```python
from threading import Thread

def long_running_task():
    # 耗时操作
    pass

@bp.route("/start-task", methods=["POST"])
def start_task():
    thread = Thread(target=long_running_task)
    thread.start()
    return jsonify({"ok": True, "message": "任务已启动"})
```

## 安全性

### 1. 路径安全

所有文件操作都使用路径验证：

```python
def _realpath_under_data(filename: str) -> str | None:
    base = os.path.realpath(_TEXT_DIR)
    path = os.path.realpath(os.path.join(_TEXT_DIR, filename))
    if not path.startswith(base + os.sep):
        return None  # 防止路径穿越
    return path
```

### 2. 输入验证

所有用户输入都需要验证：

```python
@bp.route("/save", methods=["POST"])
def save():
    data = request.get_json() or {}
    filename = (data.get('filename') or "").strip()
    
    if not filename:
        return jsonify({"ok": False, "error": "缺少文件名"}), 400
    
    # 验证文件名
    if '/' in filename or '\\' in filename:
        return jsonify({"ok": False, "error": "文件名不合法"}), 400
```

### 3. CORS 配置

生产环境应该配置 CORS：

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5001"],
        "methods": ["GET", "POST"],
    }
})
```

## 监控和日志

### 1. 日志配置

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/tmp/wintool.log'),
        logging.StreamHandler()
    ]
)
```

### 2. 错误追踪

```python
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"未处理的异常: {str(e)}", exc_info=True)
    return jsonify({"ok": False, "error": "服务器内部错误"}), 500
```

## 测试策略

### 1. 单元测试

每个工具应该有单元测试：

```python
import unittest
from tools.my_tool import MyTool

class TestMyTool(unittest.TestCase):
    def test_action(self):
        # 测试逻辑
        pass
```

### 2. 集成测试

测试工具之间的交互：

```python
def test_tool_integration():
    # 测试多个工具协同工作
    pass
```

### 3. 端到端测试

使用 Selenium 测试完整流程：

```python
from selenium import webdriver

def test_e2e():
    driver = webdriver.Chrome()
    driver.get("http://localhost:5001")
    # 测试用户操作流程
```

## 部署建议

### 1. 开发环境
- 使用 `./run.sh` 启动
- 开启 debug 模式
- 使用 SQLite 数据库

### 2. 测试环境
- 使用 `./run.sh` 启动
- 关闭 debug 模式
- 使用 MySQL 数据库

### 3. 生产环境
- 使用 `./package.sh` 打包
- 使用 Gunicorn + Nginx
- 使用 MySQL 数据库
- 配置日志轮转
- 配置监控告警

## 常见问题

### Q: 如何添加新工具？
A: 参考"工具开发规范"章节，创建新的工具类并注册。

### Q: 工具加载失败怎么办？
A: 查看启动日志，会显示具体的错误信息。其他工具不受影响。

### Q: 如何升级？
A: 备份 data 目录，更新代码，重启应用。

### Q: 如何迁移数据？
A: 复制 data 目录到新环境即可。

## 未来规划

1. **数据库支持**：添加 MySQL/PostgreSQL 支持
2. **用户系统**：添加用户认证和权限管理
3. **API 文档**：自动生成 API 文档
4. **插件市场**：支持第三方工具插件
5. **Docker 支持**：提供 Docker 镜像
6. **云端部署**：支持一键部署到云平台
