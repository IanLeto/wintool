# Wintool 重构计划

## 当前问题
1. 根目录文件混乱，有多个独立脚本和启动脚本
2. data 目录下的文件命名不够清晰
3. 代码中硬编码了数据文件路径

## 整理方案

### 1. 根目录文件整理
**保留在根目录：**
- app.py (主程序)
- requirements.txt (依赖)
- README.md (主文档)
- .gitignore

**移动到 scripts/ 目录：**
- batch_extract_7z.py → scripts/batch_extract_7z.py (独立脚本)
- init_body_weight_db.py → scripts/init_body_weight_db.py (数据库初始化)
- path_picker.py → scripts/path_picker.py (路径选择器)
- fix_mount_d.sh → scripts/fix_mount_d.sh (修复脚本)

**移动到 startup/ 目录：**
- run.sh → startup/run.sh
- stop.sh → startup/stop.sh
- start_wintool_wsl.sh → startup/start_wintool_wsl.sh
- start_wintool.command → startup/start_wintool.command
- stop_wintool.command → startup/stop_wintool.command

**移动到 docs/ 目录：**
- README_batch_extract.md → docs/batch_extract.md
- README_export_dir_structure.md → docs/export_dir_structure.md
- ai回答/ → docs/ai_answers/
- ai语料/ → docs/ai_prompts/

### 2. data 目录文件重命名
**当前 → 新名称 (更清晰的命名)：**
- path_presets.json → common_paths.json (常用路径配置)
- shore_info.json → exam_official_sites.json (考试官网信息)
- provincial_exam.json → exam_announcement_sites.json (省考公告入口)
- body_weight_README.md → body_weight_guide.md (体重管理说明)
- README.md → data_format_guide.md (数据格式说明)

**子目录重命名：**
- media_shelf/ → media_collection/ (影视收藏)
- prompt_bank/ → prompt_library/ (提示词库)
- text_viewer/ → text_documents/ (文本文档)

### 3. 需要同步修改的代码文件
- app.py (path_presets.json 引用)
- tools/shore_info.py (shore_info.json 引用)
- tools/provincial_exam.py (provincial_exam.json 引用)
- tools/media_shelf.py (media_shelf/ 目录引用)
- tools/prompt_bank.py (prompt_bank/ 目录引用)
- tools/text_viewer.py (text_viewer/ 目录引用)
- path_picker.py 的引用位置

## 执行顺序
1. 创建新目录结构
2. 重命名 data 目录下的文件和子目录
3. 更新所有代码中的硬编码路径
4. 移动根目录文件到对应目录
5. 更新启动脚本中的路径引用
6. 测试所有功能
