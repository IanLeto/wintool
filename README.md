# wintool

ian 自用的个人工具集，支持 macOS/WSL 环境 + 浏览器界面。

## 运行

### 在线环境（有网络）

```bash
pip install -r requirements.txt
python app.py
```

浏览器访问 http://localhost:5001

### 离线环境（内网部署）

**适用场景：** 内网环境、无网络连接、仅有 Python 基础环境

```bash
# 1. 在有网络的环境打包
./scripts/package_offline.sh

# 2. 传输生成的 zip 文件到内网
# 3. 在内网解压并安装
unzip -P 123 wintool_offline_*.zip
./install_offline.sh

# 4. 启动
cd wintool && python3 app.py
```

**详细说明：** 查看 [离线部署快速指南](README_OFFLINE_QUICKSTART.md) 或 [完整文档](docs/offline_deployment.md)

## macOS 双击启动

项目根目录已提供两个脚本：

- `start_wintool.command`：双击启动服务，并自动打开浏览器
- `stop_wintool.command`：双击停止服务

首次使用如果无法直接双击执行，可在终端执行一次：

```bash
chmod +x start_wintool.command stop_wintool.command
```

## Windows 桌面双击启动（项目在 WSL 内）

1. 用记事本打开 **`windows/StartWintool.bat`**，把 `WSL_PROJECT` 改成你在 WSL 里的项目路径（如 `/home/你的用户名/workdir/wintool`）；若默认发行版不对，可设置 `WSL_DISTRO`。
2. 将该 bat **复制到 Windows 桌面**（或在桌面建快捷方式指向它），双击即可：通过 `wsl.exe` 运行仓库根目录的 **`start_wintool_wsl.sh`**（行为与 `start_wintool.command` 一致，并尝试用 Windows 默认浏览器打开 **http://127.0.0.1:5001**）。
3. 更细的说明见 **`windows/README.md`**。

## 可插拔工具架构

- 每个工具是 `tools/` 目录下的独立模块，继承 `BaseTool`
- 新工具只需实现 `TOOL_ID`、`TOOL_NAME`、`get_form_html()`、`register_routes(bp)`
- 主程序自动发现并加载，无需修改 `app.py`

### 路径输入（少手打路径）

- 需要填目录/路径的工具，输入框下方提供 **选择文件夹…**（本机 `POST /api/pick-folder`，WSL 下优先弹出 **Windows 文件夹选择器**）、**粘贴 Windows 路径**（`C:\` → `/mnt/c/...`）。
- **`data/path_presets.json`** 可配置常用路径芯片；说明见 `data/README.md`。
- 请用 **http://127.0.0.1:5001** 访问，以便「选择文件夹」接口仅允许本机调用。

## 已有工具

### 文件管理工具
1. **递归展平目录**：将指定目录下所有子目录中的文件移动到该目录根下，重名自动重命名
2. **导出目录结构**：多目录递归或仅一级；先在页面预览树状文本，需要时再写入文件
3. **按 JSON 重命名文件**：根据映射重命名并保留后缀
4. **批量解压**：指定目录或单个压缩包路径，解压到各压缩包所在目录；成功则删除原文件；可选解压密码，错误则跳过；优先 7z，否则 zip/tar 标准库

### 个人生活工具
5. **体重管理**：BodyOS 个人减脂管理系统，支持每日记录、趋势分析、策略版本管理、数据导出；详见 `data/body_weight_README.md`
6. **文本阅览**：快速浏览 `data/text_viewer/` 目录下的文本文件，支持页签切换和搜索过滤
7. **影视收藏**：管理 `data/media_shelf/` 目录下的影视 JSON 文件，支持分类、状态筛选和搜索
8. **AI内容库**：聚合浏览项目根目录下的 `ai回答/` 与 `ai语料/`，支持目录切换、文件筛选、正文预览

### 信息查询工具
9. **上岸信息渠道**：读取 `data/shore_info.json` 渲染地区链接，点击跳转官网；更新数据请编辑该 JSON 后刷新页面
10. **省考公告入口**：读取 `data/provincial_exam.json`，支持单/多官网与说明文字；详见 `data/README.md`
11. **提示词收纳**：在 `data/prompt_bank/` 用本地文件保存常用提示词（后缀不限，不写后缀则默认 `.md`），网页内浏览、编辑、保存、删除；可与「影视收藏」配合使用（目录内附带格式转换提示词示例）