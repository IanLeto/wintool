#!/bin/bash
# 修复D盘挂载问题的脚本

echo "=== WSL外接硬盘挂载修复工具 ==="
echo ""

# 检查D盘是否已经挂载
if mount | grep -q "D:\\ on /mnt/d"; then
    echo "✓ D盘已经挂载"
    ls -lh /mnt/d | head -10
    exit 0
fi

echo "D盘未挂载，尝试修复..."
echo ""

# 方案1: 尝试手动挂载D盘
echo "方案1: 手动挂载D盘"
echo "执行命令: sudo mount -t drvfs D: /mnt/d"
echo ""
echo "请在Windows中确认D盘已连接，然后执行以下命令："
echo ""
echo "  sudo mount -t drvfs D: /mnt/d"
echo ""
echo "如果提示权限问题，可以添加选项："
echo "  sudo mount -t drvfs D: /mnt/d -o metadata,uid=1000,gid=1000"
echo ""

# 方案2: 配置自动挂载
echo "方案2: 配置WSL自动挂载（推荐）"
echo ""
echo "1. 编辑 /etc/wsl.conf 文件："
echo "   sudo nano /etc/wsl.conf"
echo ""
echo "2. 添加以下内容："
echo ""
cat << 'EOF'
[automount]
enabled = true
root = /mnt/
options = "metadata,uid=1000,gid=1000,umask=22,fmask=11"
mountFsTab = true

[boot]
systemd=true
EOF
echo ""
echo "3. 保存后，在Windows PowerShell中重启WSL："
echo "   wsl --shutdown"
echo "   wsl"
echo ""

# 方案3: 使用fstab
echo "方案3: 使用fstab配置（高级）"
echo ""
echo "1. 创建/编辑 /etc/fstab："
echo "   sudo nano /etc/fstab"
echo ""
echo "2. 添加以下行："
echo "   D: /mnt/d drvfs defaults,metadata,uid=1000,gid=1000 0 0"
echo ""
echo "3. 重启WSL"
echo ""

# 检查Windows中D盘状态
echo "=== 诊断信息 ==="
echo ""
echo "当前挂载的Windows盘符："
mount | grep "type 9p" | grep -E "^[A-Z]:"
echo ""
echo "/mnt/d 目录信息："
ls -la /mnt/d
echo ""
echo "如果D盘在Windows中已连接但WSL中看不到，请尝试上述方案。"
