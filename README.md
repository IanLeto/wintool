# wintool

ian 自用的个人工具集，支持 macOS/WSL 环境 + 浏览器界面。

## 运行

```bash
pip install -r requirements.txt
python app.py
```

浏览器访问 http://localhost:5001

## macOS 双击启动

项目根目录已提供两个脚本：

- `start_wintool.command`：双击启动服务，并自动打开浏览器
- `stop_wintool.command`：双击停止服务

首次使用如果无法直接双击执行，可在终端执行一次：

```bash
chmod +x start_wintool.command stop_wintool.command
```

## 可插拔工具架构

- 每个工具是 `tools/` 目录下的独立模块，继承 `BaseTool`
- 新工具只需实现 `TOOL_ID`、`TOOL_NAME`、`get_form_html()`、`register_routes(bp)`
- 主程序自动发现并加载，无需修改 `app.py`

## 已有工具

### 文件管理工具
1. **递归展平目录**：将指定目录下所有子目录中的文件移动到该目录根下，重名自动重命名
2. **导出目录结构到文件**：多目录递归或仅一级导出到文本
3. **按 JSON 重命名文件**：根据映射重命名并保留后缀

### 个人生活工具
4. **体重管理**：BodyOS 个人减脂管理系统，支持每日记录、趋势分析、策略版本管理、数据导出；详见 `data/body_weight_README.md`
5. **文本阅览**：快速浏览 `data/text_viewer/` 目录下的文本文件，支持页签切换和搜索过滤
6. **影视收藏**：管理 `data/media_shelf/` 目录下的影视 JSON 文件，支持分类、状态筛选和搜索

### 信息查询工具
7. **上岸信息渠道**：读取 `data/shore_info.json` 渲染地区链接，点击跳转官网；更新数据请编辑该 JSON 后刷新页面
8. **省考公告入口**：读取 `data/provincial_exam.json`，支持单/多官网与说明文字；详见 `data/README.md`
