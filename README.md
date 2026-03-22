# wintool

ian 自用的 Windows 文件管理工具，WSL 环境 + 浏览器界面。

## 运行

```bash
pip install -r requirements.txt
python app.py
```

浏览器访问 http://localhost:5000

## 可插拔工具架构

- 每个工具是 `tools/` 目录下的独立模块，继承 `BaseTool`
- 新工具只需实现 `TOOL_ID`、`TOOL_NAME`、`get_form_html()`、`register_routes(bp)`
- 主程序自动发现并加载，无需修改 `app.py`

## 已有工具

1. **递归展平目录**：将指定目录下所有子目录中的文件移动到该目录根下，重名自动重命名
2. **导出目录结构到文件**：多目录递归或仅一级导出到文本
3. **按 JSON 重命名文件**：根据映射重命名并保留后缀
4. **上岸信息渠道**：读取 `data/shore_info.json` 渲染地区链接，点击跳转官网；更新数据请编辑该 JSON 后刷新页面
5. **省考公告入口**：读取 `data/provincial_exam.json`，支持单/多官网与说明文字；详见 `data/README.md`
6. **关键时间节点**：读取 `data/milestones.json`，时间线展示待关注日期；仅展示、无通知；详见 `data/README.md`
