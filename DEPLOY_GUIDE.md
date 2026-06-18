# Wintool 内网部署指南

## 📋 目录

1. [K8s 配置文件位置说明](#k8s-配置文件位置说明)
2. [一键部署到内网服务器](#一键部署到内网服务器)
3. [手动部署流程](#手动部署流程)
4. [常见问题](#常见问题)

---

## 🔧 K8s 配置文件位置说明

### Linux 系统默认位置

Wintool 会自动查找以下位置的 K8s 配置文件：

1. **用户目录**（推荐）
   ```bash
   ~/.kube/config
   # 或
   $HOME/.kube/config
   ```

2. **系统目录**
   ```bash
   /etc/kubernetes/admin.conf
   ```

3. **应用目录**（手动放置）
   ```bash
   /root/workdir/wintool-inner-*/kubeconfig
   ```

### 配置优先级

```
1. 应用目录的 kubeconfig（如果存在）
2. ~/.kube/config（用户配置）
3. /etc/kubernetes/admin.conf（系统配置）
```

### 如何配置

#### **方式1：使用系统默认配置（推荐）**

如果服务器已经配置了 K8s，通常配置文件在 `~/.kube/config`，无需额外操作。

部署脚本会自动创建软链接：
```bash
ln -sf ~/.kube/config ./kubeconfig
```

#### **方式2：手动放置配置文件**

```bash
# 进入应用目录
cd /root/workdir/wintool-inner-*/

# 复制你的 kubeconfig 文件
cp /path/to/your/kubeconfig ./kubeconfig

# 或者创建软链接
ln -sf ~/.kube/config ./kubeconfig
```

#### **方式3：使用环境变量**

```bash
export KUBECONFIG=/path/to/your/kubeconfig
./start.sh
```

### 验证配置

```bash
# 检查配置文件是否存在
ls -la ~/.kube/config

# 测试 kubectl 命令
kubectl config get-contexts

# 查看集群信息
kubectl cluster-info
```

---

## 🚀 一键部署到内网服务器

### 前提条件

- ✅ 已在外网环境打包：`./pack.sh`
- ✅ Windows 电脑可以 SSH 连接到内网 Linux 服务器
- ✅ 服务器已安装 Python 3.7+
- ✅ 服务器已安装 unzip

### 使用方法

#### **1. 修改配置参数**

编辑 `deploy_to_inner.sh`，修改以下参数：

```bash
SERVER_IP="1.1.1.1"           # 服务器 IP
SERVER_USER="root"            # SSH 用户名
SERVER_PASSWORD="123"         # SSH 密码
REMOTE_DIR="/root/workdir"    # 远程部署目录
ZIP_PASSWORD="123"            # 压缩包密码
```

#### **2. 执行部署**

```bash
# 赋予执行权限
chmod +x deploy_to_inner.sh

# 一键部署
./deploy_to_inner.sh
```

### 部署流程

脚本会自动完成以下操作：

1. ✅ 查找最新的打包文件
2. ✅ 通过 SSH 上传到服务器
3. ✅ 远程解压（带密码）
4. ✅ 自动链接 K8s 配置文件
5. ✅ 设置执行权限
6. ✅ 显示启动命令

### 输出示例

```
=========================================
  Wintool 内网部署脚本
=========================================

[INFO] 找到压缩包: wintool-inner-20260618_111059.zip
[INFO] 文件大小: 720K

[INFO] 开始上传到服务器...
[INFO]   服务器: root@1.1.1.1
[INFO]   目标目录: /root/workdir

[INFO] 上传成功！

[INFO] 开始远程部署...
[INFO] 解压文件...
[INFO] 解压成功
[INFO] 配置 K8s...
[INFO] 已链接 K8s 配置: /root/.kube/config

=========================================
  部署完成！
=========================================

[INFO] 部署目录: /root/workdir/wintool-inner-20260618_111059
[INFO] 启动命令: cd /root/workdir/wintool-inner-20260618_111059 && ./start.sh

=========================================
  部署成功！
=========================================

[INFO] 下一步操作：
[INFO]   1. SSH 登录服务器: ssh root@1.1.1.1
[INFO]   2. 进入目录: cd /root/workdir/wintool-inner-20260618_111059
[INFO]   3. 启动服务: ./start.sh
[INFO]   4. 访问应用: http://1.1.1.1:8080
```

---

## 📝 手动部署流程

如果不使用一键部署脚本，可以手动操作：

### 1. 从 Windows 上传到服务器

#### **使用 WinSCP（图形界面）**

1. 打开 WinSCP
2. 连接到服务器（1.1.1.1，用户名 root，密码 123）
3. 上传 `wintool-inner-*.zip` 到 `/root/workdir/`

#### **使用 PowerShell（命令行）**

```powershell
# 使用 scp（需要安装 OpenSSH）
scp wintool-inner-*.zip root@1.1.1.1:/root/workdir/

# 或使用 pscp（PuTTY 工具）
pscp wintool-inner-*.zip root@1.1.1.1:/root/workdir/
```

### 2. SSH 登录服务器

```bash
ssh root@1.1.1.1
# 输入密码: 123
```

### 3. 解压文件

```bash
cd /root/workdir

# 解压（带密码）
unzip -P 123 wintool-inner-*.zip

# 进入目录
cd wintool-inner-*/
```

### 4. 配置 K8s（可选）

```bash
# 如果系统有默认配置，创建软链接
ln -sf ~/.kube/config ./kubeconfig

# 或者手动复制
cp ~/.kube/config ./kubeconfig

# 验证
kubectl --kubeconfig=./kubeconfig config get-contexts
```

### 5. 启动服务

```bash
chmod +x start.sh
./start.sh
```

### 6. 访问应用

```
http://1.1.1.1:8080
```

---

## ❓ 常见问题

### Q1: 如何安装 sshpass？

**macOS:**
```bash
brew install sshpass
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install sshpass

# CentOS/RHEL
sudo yum install sshpass
```

**Windows:**
- 使用 WSL（Windows Subsystem for Linux）
- 或者使用 Git Bash
- 或者手动输入密码（脚本会自动切换到交互模式）

### Q2: 找不到 K8s 配置文件怎么办？

**检查配置文件位置：**
```bash
# 查找配置文件
find ~ -name "config" -path "*/.kube/*"
find /etc -name "admin.conf" 2>/dev/null

# 查看环境变量
echo $KUBECONFIG
```

**手动指定配置文件：**
```bash
# 方式1：复制到应用目录
cp /path/to/your/kubeconfig ./kubeconfig

# 方式2：创建软链接
ln -sf /path/to/your/kubeconfig ./kubeconfig

# 方式3：使用环境变量
export KUBECONFIG=/path/to/your/kubeconfig
./start.sh
```

### Q3: 端口 8080 被占用怎么办？

启动脚本会自动尝试 8080-8089 端口，找到可用端口后启动。

**手动指定端口：**
```bash
# 编辑 backend-python/app.py
vim backend-python/app.py

# 修改最后一行
app.run(host='0.0.0.0', port=8888, debug=False)  # 改为 8888
```

### Q4: Python 依赖安装失败怎么办？

**方式1：使用本地包（推荐）**
```bash
cd python-packages
pip3 install --no-index --find-links=. Flask Flask-CORS Werkzeug --user
```

**方式2：使用国内镜像**
```bash
pip3 install Flask Flask-CORS Werkzeug -i https://pypi.tuna.tsinghua.edu.cn/simple --user
```

**方式3：手动安装 wheel 文件**
```bash
cd python-packages
pip3 install *.whl --user
```

### Q5: 如何在后台运行服务？

**使用 nohup：**
```bash
nohup ./start.sh > wintool.log 2>&1 &

# 查看日志
tail -f wintool.log

# 停止服务
ps aux | grep python3
kill <PID>
```

**使用 screen：**
```bash
# 创建会话
screen -S wintool

# 启动服务
./start.sh

# 分离会话：按 Ctrl+A，然后按 D

# 重新连接
screen -r wintool
```

**使用 systemd（推荐）：**
```bash
# 创建服务文件
sudo vim /etc/systemd/system/wintool.service

# 内容：
[Unit]
Description=Wintool Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/workdir/wintool-inner-20260618_111059/backend-python
ExecStart=/usr/bin/python3 app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start wintool
sudo systemctl enable wintool

# 查看状态
sudo systemctl status wintool
```

### Q6: 如何更新应用？

```bash
# 1. 停止旧服务
ps aux | grep python3
kill <PID>

# 2. 备份数据
cp -r wintool-inner-old/code_snippets wintool-inner-new/

# 3. 启动新服务
cd wintool-inner-new
./start.sh
```

### Q7: 如何查看日志？

```bash
# 启动时的输出
./start.sh

# 如果使用 nohup
tail -f wintool.log

# 如果使用 systemd
sudo journalctl -u wintool -f
```

---

## 📞 技术支持

如有问题，请联系开发团队。

---

**版本**: 1.0.0  
**更新时间**: 2026-06-18  
**适用环境**: Linux 服务器（内网）
