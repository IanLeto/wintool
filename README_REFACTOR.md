# Wintool 重构完成说明

## 已完成的重构工作

### 1. 目录结构整理

**根目录现在更清晰：**
```
wintool/
├── app.py                    # 主程序入口
├── requirements.txt          # Python依赖
├── README.md                 # 主文档
├── .gitignore               # Git忽略配置
├── scripts/                 # 独立脚本目录（新）
│   ├── batch_extract_7z.py
│   ├── init_body_weight_db.py
│   ├── path_picker.py
│   └── fix_mount_d.sh
├── startup/                 # 启动脚本目录（新）
│   ├── run.sh
│   ├── stop.sh
│   ├── start_wintool_wsl.sh
│   ├── start_wintool.command
│   └── stop_wintool.command
├── docs/                    # 文档目录（新）
│   ├── batch_extract.md
│   ├── export_dir_structure.md
│   ├── ai_answers/          # AI回答
│   └── ai_prompts/          # AI语料
├── data/                    # 数据目录（已重命名文件）
├── tools/                   # 工具模块
├── templates/               # HTML模板
├── static/                  # 静态资源
└── windows/                 # Windows启动脚本
```

### 2. data 目录文件重命名

**更清晰的命名方式：**
- `path_presets.json` → `common_paths.json` (常用路径配置)
- `shore_info.json` → `exam_official_sites.json` (考试官网信息)
- `provincial_exam.json` → `exam_announcement_sites.json` (省考公告入口)
- `body_weight_README.md` → `body_weight_guide.md` (体重管理说明)
- `README.md` → `data_format_guide.md` (数据格式说明)

**子目录重命名：**
- `media_shelf/` → `media_collection/` (影视收藏)
- `prompt_bank/` → `prompt_library/` (提示词库)
- `text_viewer/` → `text_documents/` (文本文档)

### 3. 代码同步更新

**已更新所有硬编码路径的文件：**
- ✅ `app.py` - 更新 common_paths.json 和 path_picker 引用
- ✅ `tools/shore_info.py` - 更新 exam_official_sites.json 引用
- ✅ `tools/provincial_exam.py` - 更新 exam_announcement_sites.json 引用
- ✅ `tools/media_shelf.py` - 更新 media_collection/ 目录引用
- ✅ `tools/prompt_bank.py` - 更新 prompt_library/ 目录引用
- ✅ `tools/text_viewer.py` - 更新 text_documents/ 目录引用

**启动脚本已更新：**
- ✅ `startup/run.sh` - 更新项目路径为父目录
- ✅ `startup/start_wintool_wsl.sh` - 更新项目路径为父目录
- ✅ `startup/start_wintool.command` - 更新项目路径为父目录
- ✅ `windows/StartWintool.bat` - 更新启动脚本路径

## 如何使用新的目录结构

### 启动程序

**Linux/WSL:**
```bash
cd /home/ian/workdir/wintool
bash startup/run.sh
```

**macOS:**
```bash
cd /path/to/wintool
bash startup/start_wintool.command
```

**Windows (通过WSL):**
双击 `windows/StartWintool.bat`

### 添加数据

**常用路径配置：**
编辑 `data/common_paths.json`

**考试官网信息：**
编辑 `data/exam_official_sites.json`

**省考公告入口：**
编辑 `data/exam_announcement_sites.json`

**影视收藏：**
在 `data/media_collection/` 目录添加文件

**提示词库：**
在 `data/prompt_library/` 目录添加文件

**文本文档：**
在 `data/text_documents/` 目录添加文件

## 注意事项

1. **所有启动脚本已更新**，可以从 `startup/` 目录运行
2. **数据文件已重命名**，旧的文件名不再使用
3. **代码引用已同步更新**，无需手动修改
4. **目录结构更清晰**，便于后续维护和扩展

## 下一步建议

1. 测试所有功能确保正常运行
2. 更新主 README.md 文档说明新的目录结构
3. 如有需要，可以创建符号链接保持向后兼容
