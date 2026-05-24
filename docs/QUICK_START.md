# Wintool 快速开始指南

## 一键启动

无论你是开发者还是普通用户，都可以通过一个命令启动 Wintool：

```bash
./run.sh
```

就这么简单！脚本会自动：
- ✅ 检测 Python 环境
- ✅ 检查并安装依赖
- ✅ 启动应用
- ✅ 打开浏览器

## 三种使用场景

### 1. 开发环境（推荐开发者）

```bash
# 首次使用：创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 日常使用：直接启动
./run.sh

# 停止服务
./run.sh stop

# 重启服务
./run.sh restart
```

### 2. 打包部署（推荐内网部署）

```bash
# 1. 打包（在开发机器上）
chmod +x package.sh
./package.sh

# 2. 传输到目标机器
scp build/wintool_*.tar.gz user@target:/path/

# 3. 在目标机器上解压并启动
tar -xzf wintool_*.tar.gz
cd wintool_*/
./start.sh
```

### 3. Windows 用户

双击运行 `start.bat`（需要 WSL）

## 打包说明

### 为什么需要打包？

打包后的 Wintool 包含：
- ✅ 完整的 Python 虚拟环境
- ✅ 所有依赖库
- ✅ 应用代码和数据
- ✅ 启动脚本

**优势**：
- 无需网络连接
- 无需手动安装依赖
- 一键部署到任何机器
- 适合内网环境

### 打包步骤

```bash
# 1. 确保在项目根目录
cd /path/to/wintool

# 2. 执行打包脚本
chmod +x package.sh
./package.sh

# 3. 查看打包结果
ls -lh build/
# 输出示例：
# wintool_20260518_224500.tar.gz  (约 50MB)
```

### 打包产物说明

```
build/
└── wintool_20260518_224500/
    ├── start.sh          # Linux/macOS/WSL 启动脚本
    ├── start.bat         # Windows 启动脚本
    ├── stop.sh           # 停止脚本
    ├── run.sh            # 统一启动逻辑
    ├── app.py            # 主程序
    ├── .venv/            # Python 虚拟环境（已包含所有依赖）
    ├── data/             # 数据目录
    ├── static/           # 静态资源
    ├── templates/        # 模板文件
    ├── tools/            # 工具模块
    ├── scripts/          # 辅助脚本
    ├── DEPLOY.md         # 部署说明
    └── README.md         # 项目说明
```

## 统一启动方式

### 核心理念

**一个脚本，适配所有环境**

`run.sh` 会自动检测环境并选择最佳启动方式：

1. **打包环境**：使用打包的虚拟环境
2. **开发环境**：使用本地虚拟环境（.venv）
3. **系统环境**：使用系统 Python

### 启动流程

```
┌─────────────────┐
│  执行 ./run.sh  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 检测打包环境？  │
└────┬───────┬────┘
     │ 是    │ 否
     ▼       ▼
┌─────────┐ ┌─────────────┐
│使用打包 │ │检测虚拟环境│
│的 .venv │ └──┬──────┬───┘
└─────────┘    │ 是   │ 否
               ▼      ▼
          ┌────────┐ ┌──────────┐
          │使用.venv│ │使用系统  │
          │        │ │Python    │
          └────────┘ └──────────┘
               │         │
               └────┬────┘
                    ▼
          ┌──────────────┐
          │ 检查依赖     │
          └──────┬───────┘
                 ▼
          ┌──────────────┐
          │ 启动应用     │
          └──────┬───────┘
                 ▼
          ┌──────────────┐
          │ 打开浏览器   │
          └──────────────┘
```

## 错误隔离保证

### 工具级隔离

即使某个工具出现错误，其他工具仍然可以正常使用：

```
启动日志示例：
✓ 工具已加载: 文本阅览 (text_viewer)
✓ 工具已加载: 影视收藏 (media_shelf)
✗ 工具加载失败: 新工具 (new_tool)
  错误: ModuleNotFoundError: No module named 'xxx'
✓ 工具已加载: 提示词收纳 (prompt_bank)
✓ 工具已加载: 体重管理 (body_weight)

应用启动成功！其他工具不受影响。
```

### 数据隔离

每个工具的数据存储在独立目录：

```
data/
├── text_documents/     # 文本阅览工具
├── media_shelf/        # 影视收藏工具
├── prompt_bank/        # 提示词收纳工具
└── body_weight.db      # 体重管理数据库
```

**好处**：
- 工具之间互不影响
- 数据备份更简单
- 迁移更方便

## 常见问题

### Q1: 启动失败怎么办？

```bash
# 查看日志
cat /tmp/wintool.log

# 常见原因：
# 1. 端口被占用 -> 修改端口：export PORT=5002 && ./run.sh
# 2. 依赖缺失 -> 重新安装：pip install -r requirements.txt
# 3. 权限问题 -> 添加执行权限：chmod +x run.sh
```

### Q2: 如何更换端口？

```bash
# 临时更换
PORT=5002 ./run.sh

# 永久更换（修改 run.sh 中的 PORT 变量）
PORT="${PORT:-5002}"
```

### Q3: 如何备份数据？

```bash
# 备份所有数据
tar -czf wintool_data_backup_$(date +%Y%m%d).tar.gz data/

# 恢复数据
tar -xzf wintool_data_backup_20260518.tar.gz
```

### Q4: 如何升级？

```bash
# 方法1：Git 更新（开发环境）
git pull
./run.sh restart

# 方法2：重新打包部署（生产环境）
# 1. 备份数据
tar -czf data_backup.tar.gz data/

# 2. 获取新版本并解压
tar -xzf wintool_new_version.tar.gz

# 3. 恢复数据
cp -r data_backup/* wintool_new_version/data/

# 4. 启动新版本
cd wintool_new_version/
./start.sh
```

### Q5: 打包后的文件太大？

打包文件包含完整的 Python 虚拟环境，通常 50-100MB。

**优化建议**：
- 移除不必要的依赖
- 使用 `--no-cache-dir` 安装依赖
- 压缩时使用更高的压缩率

### Q6: Windows 用户如何使用？

```batch
REM 方法1：使用 WSL（推荐）
wsl bash run.sh

REM 方法2：双击 start.bat（打包版本）
start.bat
```

## 最佳实践

### 开发环境

```bash
# 1. 使用虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8  # 开发工具

# 3. 启动开发服务器
./run.sh

# 4. 代码格式化
black .

# 5. 运行测试
pytest
```

### 生产环境

```bash
# 1. 打包
./package.sh

# 2. 传输到服务器
scp build/wintool_*.tar.gz user@server:/opt/

# 3. 部署
ssh user@server
cd /opt
tar -xzf wintool_*.tar.gz
cd wintool_*/
./start.sh

# 4. 配置开机自启（可选）
# 创建 systemd 服务
sudo nano /etc/systemd/system/wintool.service
```

### 数据管理

```bash
# 定期备份
0 2 * * * cd /path/to/wintool && tar -czf ~/backups/wintool_$(date +\%Y\%m\%d).tar.gz data/

# 清理旧备份（保留最近7天）
find ~/backups -name "wintool_*.tar.gz" -mtime +7 -delete
```

## 下一步

- 📖 阅读 [架构文档](ARCHITECTURE.md) 了解系统设计
- 🛠️ 查看 [开发指南](DEVELOPMENT.md) 学习如何添加新工具
- 🐛 遇到问题？提交 [Issue](https://github.com/IanLeto/wintool/issues)

## 技术支持

- 项目地址：https://github.com/IanLeto/wintool
- 问题反馈：提交 Issue
- 文档更新：欢迎 PR
