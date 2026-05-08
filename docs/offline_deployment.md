# Wintool 离线部署指南

本文档说明如何在**内网环境**（无网络连接）部署 Wintool 工具。

## 概述

Wintool 支持完全离线部署，只需要：
- ✅ Python 3.7+ 基础环境
- ✅ pip 包管理工具
- ❌ 无需网络连接
- ❌ 无需额外依赖

## 一、打包准备（在有网络的环境）

### 1.1 环境要求
- Python 3.7+
- pip
- zip 命令
- 网络连接（用于下载依赖包）

### 1.2 执行打包
```bash
cd /path/to/wintool
./scripts/package_offline.sh
```

### 1.3 打包产物
生成文件：`wintool_offline_YYYYMMDD_HHMMSS.zip`

**包含内容：**
- `wintool/` - 完整项目代码
- `vendor/` - Python 依赖包（Flask、PyMySQL 等）
- `install_offline.sh` - Linux/macOS 自动安装脚本
- `install_offline.bat` - Windows 自动安装脚本
- `README_OFFLINE.txt` - 部署说明

**压缩包密码：** `123`

---

## 二、离线部署（在内网环境）

### 2.1 Linux / macOS 部署

#### 步骤 1：解压
```bash
unzip -P 123 wintool_offline_YYYYMMDD_HHMMSS.zip
cd wintool_offline_YYYYMMDD_HHMMSS
```

#### 步骤 2：运行安装脚本
```bash
./install_offline.sh
```

安装脚本会自动：
1. 检测 Python 环境
2. 离线安装依赖包（从 vendor/ 目录）
3. 创建必要的数据目录
4. 设置脚本执行权限

#### 步骤 3：启动服务
```bash
cd wintool
python3 app.py
```

或使用启动脚本：
```bash
cd wintool
./startup/run.sh
```

#### 步骤 4：访问
打开浏览器访问：`http://127.0.0.1:5001`

---

### 2.2 Windows 部署

#### 步骤 1：解压
使用 WinRAR、7-Zip 等工具解压，密码：`123`

#### 步骤 2：运行安装脚本
双击运行：`install_offline.bat`

安装脚本会自动：
1. 检测 Python 环境
2. 离线安装依赖包
3. 创建数据目录

#### 步骤 3：启动服务
```cmd
cd wintool
python app.py
```

或双击运行：`wintool\startup\start_wintool.command`（需先设置）

#### 步骤 4：访问
打开浏览器访问：`http://127.0.0.1:5001`

---

## 三、手动部署（如果自动脚本失败）

### 3.1 手动安装依赖
```bash
cd vendor
python3 -m pip install --no-index --find-links=. Flask-*.whl
python3 -m pip install --no-index --find-links=. PyMySQL-*.whl
```

### 3.2 创建数据目录
```bash
cd wintool
mkdir -p data/media_collection
mkdir -p data/text_documents
mkdir -p data/prompt_library
```

### 3.3 创建配置文件
创建 `data/common_paths.json`：
```json
{
  "presets": [
    {
      "label": "桌面",
      "path": "/Users/你的用户名/Desktop"
    }
  ]
}
```

### 3.4 启动服务
```bash
python3 app.py
```

---

## 四、依赖说明

Wintool 仅依赖两个 Python 包：

| 包名 | 版本 | 用途 |
|------|------|------|
| Flask | ≥3.0.0 | Web 框架 |
| PyMySQL | ≥1.1.0 | MySQL 数据库连接（体重管理功能） |

**注意：** 如果不使用体重管理功能，可以不安装 PyMySQL。

---

## 五、常见问题

### 5.1 Python 版本不兼容
**问题：** 依赖包安装失败，提示版本不兼容

**解决：**
1. 确认 Python 版本：`python3 --version`
2. 建议使用 Python 3.8 - 3.11
3. 如果版本过低，升级 Python 后重新打包

### 5.2 pip 未安装
**问题：** 提示 `pip: command not found`

**解决：**
```bash
# Linux/macOS
python3 -m ensurepip --default-pip

# Windows
python -m ensurepip --default-pip
```

### 5.3 权限问题（Linux/macOS）
**问题：** 脚本无法执行

**解决：**
```bash
chmod +x install_offline.sh
chmod +x wintool/startup/*.sh
```

### 5.4 端口被占用
**问题：** 启动失败，提示端口 5001 被占用

**解决：**
修改 `app.py` 最后一行：
```python
app.run(host="0.0.0.0", port=5002, debug=True)  # 改为其他端口
```

### 5.5 MySQL 连接失败（体重管理）
**问题：** 体重管理功能报错

**解决：**
1. 体重管理功能需要 MySQL 数据库
2. 如果内网无 MySQL，该功能将不可用
3. 其他功能不受影响

---

## 六、目录结构

```
wintool_offline_YYYYMMDD_HHMMSS/
├── wintool/                    # 项目代码
│   ├── app.py                  # 主程序
│   ├── requirements.txt        # 依赖列表
│   ├── tools/                  # 工具模块
│   ├── templates/              # HTML 模板
│   ├── static/                 # 静态资源
│   ├── scripts/                # 脚本工具
│   ├── startup/                # 启动脚本
│   └── data/                   # 数据目录（首次运行创建）
├── vendor/                     # 依赖包（离线）
│   ├── Flask-3.0.0-*.whl
│   ├── PyMySQL-1.1.0-*.whl
│   └── ...（其他依赖）
├── install_offline.sh          # Linux/macOS 安装脚本
├── install_offline.bat         # Windows 安装脚本
└── README_OFFLINE.txt          # 部署说明
```

---

## 七、验证部署

### 7.1 检查服务状态
访问：`http://127.0.0.1:5001`

应该看到 Wintool 主界面，显示所有可用工具。

### 7.2 测试基础功能
1. **文本阅览** - 测试文件读取
2. **导出目录结构** - 测试文件系统操作
3. **提示词收纳** - 测试文件编辑

### 7.3 检查日志
如果有问题，查看终端输出的错误信息。

---

## 八、生产环境建议

### 8.1 使用生产级 WSGI 服务器
默认的 Flask 开发服务器不适合生产环境，建议使用：

**Gunicorn（Linux/macOS）：**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

**Waitress（跨平台）：**
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5001 app:app
```

### 8.2 设置开机自启
创建 systemd 服务（Linux）：
```ini
[Unit]
Description=Wintool Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/wintool
ExecStart=/usr/bin/python3 /path/to/wintool/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 8.3 配置反向代理
使用 Nginx 作为反向代理：
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 九、更新部署

### 9.1 更新代码
1. 在有网络环境重新打包
2. 传输新的离线包到内网
3. 备份旧的 `data/` 目录
4. 解压新包并恢复 `data/` 目录

### 9.2 更新依赖
如果 `requirements.txt` 有变化：
1. 重新执行打包脚本
2. 新的依赖会自动包含在 `vendor/` 目录

---

## 十、安全建议

1. **修改默认密码** - 压缩包密码建议改为更复杂的
2. **限制访问** - 仅监听 127.0.0.1，不对外开放
3. **定期备份** - 备份 `data/` 目录中的重要数据
4. **权限控制** - 设置适当的文件系统权限

---

## 联系支持

如有问题，请查看：
- 项目 README.md
- GitHub Issues
- 项目文档目录 `docs/`
