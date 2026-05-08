# Wintool 离线部署快速指南

## 📦 打包（有网络环境）

```bash
cd /path/to/wintool
./scripts/package_offline.sh
```

生成文件：`wintool_offline_YYYYMMDD_HHMMSS.zip`（密码：123）

---

## 🚀 部署（内网环境）

### Linux / macOS

```bash
# 1. 解压
unzip -P 123 wintool_offline_*.zip
cd wintool_offline_*

# 2. 安装
./install_offline.sh

# 3. 启动
cd wintool
python3 app.py
```

### Windows

```cmd
REM 1. 解压（使用 WinRAR/7-Zip，密码：123）

REM 2. 安装
双击运行 install_offline.bat

REM 3. 启动
cd wintool
python app.py
```

---

## 🌐 访问

浏览器打开：**http://127.0.0.1:5001**

---

## ✅ 环境要求

- ✅ Python 3.7+（必须）
- ✅ pip（必须）
- ❌ 无需网络
- ❌ 无需其他依赖

---

## 📋 包含内容

- **wintool/** - 完整项目代码
- **vendor/** - Python 依赖包（Flask、PyMySQL）
- **install_offline.sh** - Linux/macOS 安装脚本
- **install_offline.bat** - Windows 安装脚本
- **README_OFFLINE.txt** - 详细说明

---

## 🔧 常见问题

### Python 未安装
```bash
# 检查
python3 --version

# 如果未安装，请先安装 Python 3.7+
```

### pip 未安装
```bash
python3 -m ensurepip --default-pip
```

### 端口被占用
修改 `wintool/app.py` 最后一行：
```python
app.run(host="0.0.0.0", port=5002, debug=True)  # 改端口
```

### 权限问题（Linux/macOS）
```bash
chmod +x install_offline.sh
chmod +x wintool/startup/*.sh
```

---

## 📚 详细文档

查看完整文档：`wintool/docs/offline_deployment.md`

---

## 🎯 功能特性

Wintool 提供以下工具：

### 文件管理
- 递归展平目录
- 导出目录结构
- 按 JSON 重命名文件
- 批量解压

### 个人工具
- 体重管理（需 MySQL）
- 文本阅览
- 影视收藏
- 提示词收纳
- 密码管理
- 命令片段

### 信息查询
- 上岸信息渠道
- 省考公告入口

---

## 🔐 安全提示

1. 压缩包密码：`123`（建议修改）
2. 默认仅监听本地：`127.0.0.1`
3. 生产环境建议使用 Gunicorn/Waitress

---

## 📞 支持

- 详细文档：`docs/offline_deployment.md`
- 项目 README：`README.md`
- GitHub Issues
