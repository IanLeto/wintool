# wintool

ian 自用的个人工具集，支持 macOS/WSL 环境 + 浏览器界面。

## 快速启动

```bash
# 启动服务
./run.sh

# 停止服务
./run.sh stop

# 重启服务
./run.sh restart
```

**特点：**
- ✅ 自动检测环境（本地开发 / 内网打包）
- ✅ 自动检测 Python（虚拟环境 / 系统 Python）
- ✅ 自动检查依赖并安装
- ✅ 自动打开浏览器
- ✅ 支持 macOS / Linux / WSL

### 首次使用

```bash
# 1. 安装依赖（仅本地开发需要）
pip install -r requirements.txt

# 2. 启动
./run.sh
```

浏览器访问 http://localhost:5001

## 内网部署

### 打包

```bash
# 在有网络的环境打包
./scripts/package_simple.sh
```

### 部署

```bash
# 1. 传输生成的 zip 文件到内网
# 2. 解压（密码: 123）
unzip -P 123 wintool_simple_*.zip

# 3. 进入目录并启动
cd wintool
./run.sh
```

**说明：**
- 打包后的压缩包包含所有依赖
- 内网环境只需要 Python 3.7+
- 使用统一的 `run.sh` 脚本启动
- 无需任何安装步骤

## 项目架构

### 可插拔工具设计

- 每个工具是 `tools/` 目录下的独立模块，继承 `BaseTool`
- 新工具只需实现 `TOOL_ID`、`TOOL_NAME`、`get_form_html()`、`register_routes(bp)`
- 主程序自动发现并加载，无需修改 `app.py`
- 单个工具错误不影响其他工具运行

### 目录结构

```
wintool/
├── app.py              # 主应用入口
├── run.sh              # 统一启动脚本
├── requirements.txt    # Python 依赖
├── README.md          # 项目说明（本文件）
│
├── tools/             # 工具模块目录
│   ├── __init__.py   # 工具注册
│   ├── base.py       # 基类定义
│   └── *.py          # 各个工具实现
│
├── static/            # 静态资源
│   ├── app.js        # 前端 JavaScript
│   ├── style.css     # 样式文件
│   └── path_helpers.js
│
├── templates/         # HTML 模板
│   ├── index.html    # 首页
│   └── tool.html     # 工具页面模板
│
├── data/              # 数据目录（不会被打包到内网）
│   └── ...           # 各工具的数据文件
│
└── scripts/           # 辅助脚本
    ├── package_simple.sh  # 打包脚本
    └── path_picker.py     # 路径选择器
```

## 已有工具

### 文件管理工具
1. **递归展平目录**：将指定目录下所有子目录中的文件移动到该目录根下
2. **导出目录结构**：多目录递归或仅一级；先在页面预览树状文本
3. **按 JSON 重命名文件**：根据映射重命名并保留后缀
4. **批量解压**：支持 7z/zip/tar，可选解压密码

### 个人生活工具
5. **体重管理**：BodyOS 个人减脂管理系统，支持每日记录、趋势分析
6. **文本阅览**：快速浏览 `data/text_documents/` 目录下的文本文件
7. **影视收藏**：管理 `data/media_shelf/` 目录下的影视 JSON 文件
8. **提示词收纳**：在 `data/prompt_library/` 保存常用提示词
9. **代码片段管理**：存储内外网传输的代码片段（本地存储，不会被 git 追踪）

### 开发工具
10. **Kafka 生产者**：测试连接、发送消息、SASL 认证
11. **Kafka 消费者**：消费消息、分区信息显示
12. **命令片段管理**：保存常用命令行片段

### 信息查询工具
13. **上岸信息渠道**：读取 `data/shore_info.json` 渲染地区链接
14. **省考公告入口**：读取 `data/provincial_exam.json`
15. **密码管理器**：本地加密存储密码

## 常见问题

### 启动失败？

```bash
# 查看日志
cat /tmp/wintool.log

# 常见原因：
# 1. 端口被占用 -> export PORT=5002 && ./run.sh
# 2. 依赖缺失 -> pip install -r requirements.txt
# 3. 权限问题 -> chmod +x run.sh
```

### 如何备份数据？

```bash
# 备份所有数据
tar -czf wintool_data_backup_$(date +%Y%m%d).tar.gz data/

# 恢复数据
tar -xzf wintool_data_backup_20260605.tar.gz
```

### 如何添加新工具？

1. 在 `tools/` 目录创建新的 Python 文件
2. 继承 `BaseTool` 类并实现必要方法
3. 在 `tools/__init__.py` 中注册新工具
4. 重启应用即可

## 技术支持

- 项目地址：https://github.com/IanLeto/wintool
- 问题反馈：提交 Issue
