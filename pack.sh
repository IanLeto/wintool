#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool 内网版本打包脚本
# 用途：将内网版本（Python 后端 + Vue 前端）打包成加密压缩包

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PACKAGE_NAME="wintool-inner-${TIMESTAMP}"
TEMP_DIR="/tmp/${PACKAGE_NAME}"
OUTPUT_FILE="${SCRIPT_DIR}/${PACKAGE_NAME}.zip"
PASSWORD="123"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $*"; }
echo_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
echo_title() { echo -e "${BLUE}$*${NC}"; }

echo_title "========================================="
echo_title "  Wintool 内网版本打包工具"
echo_title "========================================="
echo ""

# 检查 zip 命令
if ! command -v zip >/dev/null 2>&1; then
    echo_error "未找到 zip 命令"
    echo_error "请先安装: brew install zip (macOS) 或 apt-get install zip (Linux)"
    exit 1
fi

# 清理旧的临时目录
if [[ -d "$TEMP_DIR" ]]; then
    echo_info "清理旧的临时目录..."
    rm -rf "$TEMP_DIR"
fi

# 创建临时目录
echo_info "创建临时目录: $TEMP_DIR"
mkdir -p "$TEMP_DIR"

echo ""
echo_info "开始准备文件..."

# 构建前端
echo_info "  [1/6] 构建前端..."
cd "$SCRIPT_DIR/frontend"
if [[ ! -d "node_modules" ]]; then
    echo_warn "      未找到 node_modules，正在安装依赖..."
    npm install
fi
echo_info "      运行 npm run build..."
npm run build
echo_info "      前端构建完成"

# 下载 Python 依赖
echo_info "  [2/6] 下载 Python 依赖..."
mkdir -p "$TEMP_DIR/python-packages"
cd "$TEMP_DIR/python-packages"
echo_info "      下载 Flask 及其依赖..."
pip3 download Flask==2.3.0 Flask-CORS==4.0.0 Werkzeug==2.3.0 -d . 2>&1 | grep -v "Requirement already satisfied" || true
echo_info "      下载 kafka-python..."
pip3 download kafka-python -d . 2>&1 | grep -v "Requirement already satisfied" || true
echo_info "      Python 依赖下载完成（$(ls -1 | wc -l | tr -d ' ') 个包）"

# 复制 Python 后端
echo_info "  [3/6] 复制 Python 后端..."
mkdir -p "$TEMP_DIR/backend-python"
cp -r "$SCRIPT_DIR/backend-python/"* "$TEMP_DIR/backend-python/"

# 复制前端构建产物到 backend-python 同级目录
echo_info "  [4/6] 复制前端构建产物..."
mkdir -p "$TEMP_DIR/backend-python/frontend/dist"
cp -r "$SCRIPT_DIR/frontend/dist/"* "$TEMP_DIR/backend-python/frontend/dist/"

# 复制解压脚本
echo_info "  [5/6] 复制解压脚本..."
cp "$SCRIPT_DIR/extract_wheels.py" "$TEMP_DIR/"

# 创建启动脚本（不使用 pip）
echo_info "  [6/6] 创建启动脚本..."
cat > "$TEMP_DIR/start.sh" << 'STARTEOF'
#!/usr/bin/env bash
# Wintool 内网版本启动脚本（纯 Python，无需 pip）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend-python"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $*"; }
echo_title() { echo -e "${BLUE}$*${NC}"; }

echo_title "========================================="
echo_title "  启动 Wintool 内网版本"
echo_title "  纯 Python 后端 + 静态前端"
echo_title "  无需 pip，完全离线"
echo_title "========================================="
echo ""

# 检查 Python
if ! command -v python3 >/dev/null 2>&1; then
    echo_error "未找到 Python3"
    echo_error "请先安装 Python 3.7+"
    exit 1
fi

echo_info "Python 版本: $(python3 --version)"
echo ""

# 解压依赖包（如果 libs 目录不存在）
if [[ ! -d "$SCRIPT_DIR/libs" ]]; then
    echo_info "解压 Python 依赖包..."
    cd "$SCRIPT_DIR"
    if ! python3 extract_wheels.py; then
        echo_error "解压依赖失败！"
        exit 1
    fi
    echo ""
fi

# 验证依赖
echo_info "验证依赖..."
cd "$SCRIPT_DIR"
if ! python3 -c "import sys; sys.path.insert(0, 'libs'); import flask; import flask_cors; print('Flask 版本:', flask.__version__)" 2>&1; then
    echo_error "Flask 导入失败！"
    echo_error "libs 目录可能损坏，请删除后重试："
    echo_error "  rm -rf libs"
    echo_error "  ./start.sh"
    exit 1
fi

echo_info "依赖验证成功"
echo ""

# 启动服务
echo_info "启动服务..."
cd "$BACKEND_DIR"
python3 app.py

STARTEOF
chmod +x "$TEMP_DIR/start.sh"

# 复制数据目录（如果存在）
if [[ -d "$SCRIPT_DIR/code_snippets" ]]; then
    echo_info "  [6/8] 复制数据文件..."
    cp -r "$SCRIPT_DIR/code_snippets" "$TEMP_DIR/"
else
    echo_info "  [6/8] 创建数据目录..."
    mkdir -p "$TEMP_DIR/code_snippets"
fi

# 复制原型文件目录
echo_info "  [7/8] 复制原型文件..."
if [[ -d "$SCRIPT_DIR/prototypes" ]]; then
    cp -r "$SCRIPT_DIR/prototypes" "$TEMP_DIR/"
    echo_info "      已复制 prototypes 目录（$(ls -1 "$SCRIPT_DIR/prototypes"/*.html 2>/dev/null | wc -l | tr -d ' ') 个 HTML 文件）"
else
    mkdir -p "$TEMP_DIR/prototypes"
    echo_info "      已创建 prototypes 目录（空）"
fi

# 复制 kubeconfig 示例文件
echo_info "  [8/8] 复制 K8s 配置文件..."
if [[ -f "$SCRIPT_DIR/kubeconfig" ]]; then
    cp "$SCRIPT_DIR/kubeconfig" "$TEMP_DIR/"
    echo_info "      已复制实际 kubeconfig 文件"
elif [[ -f "$SCRIPT_DIR/kubeconfig.example" ]]; then
    cp "$SCRIPT_DIR/kubeconfig.example" "$TEMP_DIR/"
    echo_info "      已复制 kubeconfig 示例文件"
else
    echo_warn "      未找到 kubeconfig 文件，K8s 功能将使用系统默认配置"
fi

# 创建 README
echo_info "  [8/8] 创建说明文档..."
cat > "$TEMP_DIR/README_INNER.md" << 'EOF'
# Wintool 内网版本使用说明

## 📦 包含内容

- `backend-python/` - Python Flask 后端
- `frontend/dist/` - 前端构建产物（静态文件）
- `python-packages/` - Python 依赖包（离线安装）
- `start.sh` - 启动脚本
- `code_snippets/` - 数据存储目录
- `README_INNER.md` - 本说明文档

## 🚀 快速开始

### 1. 环境要求

**只需要 Python！**
- **Python 3.7+** （必需）
- **pip3** （Python 包管理器）

**不需要：**
- ❌ Node.js
- ❌ npm
- ❌ 前端依赖

### 2. 安装依赖

**方式1：从本地包安装（推荐，无需网络）**
```bash
cd python-packages
pip3 install --no-index --find-links=. Flask Flask-CORS Werkzeug --user
```

**方式2：从网络安装（如果内网有外网访问）**
```bash
cd backend-python
pip3 install -r requirements.txt --user
```

或使用国内镜像：
```bash
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --user
```

### 3. 启动服务

```bash
chmod +x start.sh
./start.sh
```

或者直接运行：
```bash
cd backend-python
python3 app.py
```

启动后访问：**http://localhost:8080**

### 4. 停止服务

按 `Ctrl+C` 停止服务

## 📝 功能说明

### 代码片段库
- ✅ 添加/编辑/删除代码片段
- ✅ 搜索和筛选
- ✅ 一键复制代码
- ✅ 数据持久化到本地文件

### 数据存储
所有数据保存在 `code_snippets/snippets.json` 文件中

### 技术架构
- **后端**: Python Flask（提供 API + 静态文件服务）
- **前端**: Vue 3 构建产物（已编译为静态 HTML/JS/CSS）
- **数据**: JSON 文件存储
- **依赖**: 离线 Python 包（无需网络）

## 🔧 故障排除

### Python 依赖安装失败

**方法1：使用本地包（推荐）**
```bash
cd python-packages
pip3 install --no-index --find-links=. Flask Flask-CORS Werkzeug --user
```

**方法2：使用国内镜像（需要网络）**
```bash
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --user
```

**方法3：手动安装**
```bash
cd python-packages
pip3 install *.whl --user
```

### 端口被占用
默认端口：8080

如果端口被占用，可以修改 `backend-python/app.py` 最后一行：
```python
app.run(host='0.0.0.0', port=8080, debug=False)  # 改为其他端口
```

### 无法访问
1. 检查防火墙设置
2. 确认 Python 服务正常启动
3. 查看终端输出的错误信息

## 💡 优势

1. **完全离线** - 包含所有 Python 依赖，无需网络
2. **极简部署** - 只需 Python，无需 Node.js
3. **一键启动** - 运行 start.sh 即可
4. **轻量级** - 压缩包小，启动快
5. **功能完整** - 与外网版本功能一致
6. **数据安全** - 本地文件存储

## 📞 技术支持

如有问题，请联系开发团队

---

**版本**: 1.0.0 (内网版 - 完全离线)  
**打包时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**特点**: 
- ✅ 无需 Node.js，前端已预编译
- ✅ 包含所有 Python 依赖，完全离线安装
- ✅ 只需 Python 3.7+，无需任何网络连接
EOF

echo ""
echo_info "文件复制完成"
echo ""

# 打包
echo_info "开始打包..."
cd /tmp
if zip -r -P "$PASSWORD" "$OUTPUT_FILE" "$PACKAGE_NAME" >/dev/null 2>&1; then
    echo_info "打包成功！"
else
    echo_error "打包失败"
    exit 1
fi

# 清理临时目录
echo_info "清理临时文件..."
rm -rf "$TEMP_DIR"

# 显示结果
echo ""
echo_title "========================================="
echo_title "  打包完成！"
echo_title "========================================="
echo ""
echo_info "输出文件: $OUTPUT_FILE"
echo_info "文件大小: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo_info "压缩密码: $PASSWORD"
echo ""
echo_warn "解压命令: unzip -P $PASSWORD $(basename "$OUTPUT_FILE")"
echo ""
echo_info "可以通过邮件将此文件发送到内网环境"
echo ""
