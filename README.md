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
