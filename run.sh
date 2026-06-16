#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Wintool 后端启动脚本
# 用途：启动 Spring Boot 后端服务

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend/wintool-backend"

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
echo_title "  启动 Wintool 后端 (Spring Boot)"
echo_title "========================================="
echo ""

# 检查 Java
if ! command -v java >/dev/null 2>&1; then
    echo_error "未找到 Java"
    echo_error "请先安装 Java JDK 8+: https://adoptium.net/"
    exit 1
fi

echo_info "Java 版本: $(java -version 2>&1 | head -n 1)"

# 检查 Maven
if ! command -v mvn >/dev/null 2>&1; then
    echo_error "未找到 Maven"
    echo_error "请先安装 Maven: https://maven.apache.org/"
    exit 1
fi

echo_info "Maven 版本: $(mvn --version | head -n 1)"
echo ""

# 检查后端目录
if [[ ! -d "$BACKEND_DIR" ]]; then
    echo_error "未找到 backend/wintool-backend 目录"
    echo_error "请确保项目结构完整"
    exit 1
fi

# 进入后端目录
cd "$BACKEND_DIR"

# 检查 pom.xml
if [[ ! -f "pom.xml" ]]; then
    echo_error "未找到 pom.xml"
    echo_error "请确保 Spring Boot 项目已正确初始化"
    exit 1
fi

# 启动服务
echo_info "启动后端服务..."
echo_info "访问地址: http://localhost:8080"
echo_info "API 文档: http://localhost:8080/swagger-ui.html"
echo_title "========================================="
echo ""

# 根据参数选择启动方式
case "${1:-dev}" in
    dev|development)
        echo_info "开发模式：使用 Maven 启动"
        mvn spring-boot:run
        ;;
    prod|production)
        echo_info "生产模式：编译并运行 JAR"
        echo_info "编译项目..."
        mvn clean package -DskipTests
        
        JAR_FILE=$(find target -name "*.jar" -not -name "*-sources.jar" | head -n 1)
        if [[ -z "$JAR_FILE" ]]; then
            echo_error "未找到编译后的 JAR 文件"
            exit 1
        fi
        
        echo_info "启动 JAR: $JAR_FILE"
        java -jar "$JAR_FILE"
        ;;
    build)
        echo_info "仅编译项目..."
        mvn clean package -DskipTests
        ;;
    clean)
        echo_info "清理项目..."
        mvn clean
        ;;
    *)
        echo_error "未知参数: $1"
        echo ""
        echo "用法: $0 [dev|prod|build|clean]"
        echo ""
        echo "  dev   - 开发模式启动 (默认)"
        echo "  prod  - 生产模式启动 (编译后运行)"
        echo "  build - 仅编译项目"
        echo "  clean - 清理编译文件"
        exit 1
        ;;
esac
