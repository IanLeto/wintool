# 打包脚本说明

## package_simple.sh - 内网部署专用（推荐）

**用途：** 打包代码 + 所有依赖源码，内网直接运行，无需安装

**特点：**
- ✅ 包含所有依赖（Flask、PyMySQL等）在 lib/ 目录
- ✅ 解压即用，无需 pip
- ✅ 只需要 Python 3.7+
- ✅ 适合内网环境

**使用：**
```bash
./scripts/package_simple.sh
```

**生成文件：** `wintool_simple_YYYYMMDD_HHMMSS.zip` (约 720KB)

**内网部署：**
```bash
unzip -P 123 wintool_simple_*.zip
cd wintool
python3 run_simple.py
```

---

## 已删除的脚本

- ~~package_wintool.sh~~ - 只打包代码，不含依赖（已删除，不适合内网）
- ~~package_offline.sh~~ - 复杂的离线方案（已删除）
- ~~install_manual.py~~ - 手动安装脚本（已删除）

---

**结论：只用 package_simple.sh 即可！**
