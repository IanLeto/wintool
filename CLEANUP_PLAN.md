# Wintool 代码清理计划

## 分析结果

### 1. 重复功能的工具（需要合并）

#### ✅ 代码片段管理工具（重复）
- **code_snippets.py** (450行) - 功能完整，UI美观，存储在独立目录
- **command_snippets.py** (551行) - 功能类似，存储在JSON文件

**建议**：保留 `command_snippets.py`，删除 `code_snippets.py`
- `command_snippets.py` 更简洁，使用单个JSON文件存储
- `code_snippets.py` 使用独立目录存储，增加复杂度
- 两者功能高度重叠（都是管理代码/命令片段）

#### ✅ Kafka 工具（可以合并）
- **kafka_consumer.py** (266行) - Kafka消费者
- **kafka_producer.py** (238行) - Kafka生产者

**建议**：合并为 `kafka_tool.py`
- 两个工具都操作Kafka，共享配置逻辑
- 可以在一个页面用标签页切换生产者/消费者
- 减少代码重复（认证配置等）

### 2. 功能相似的工具（需要评估）

#### ⚠️ 考试信息工具
- **shore_info.py** - 上岸信息（考试相关链接）
- **provincial_exam.py** - 省考信息

**建议**：可以合并为统一的"考试信息管理"工具
- 两者都是展示考试相关链接
- 数据结构类似
- 可以用分类区分不同类型的考试

### 3. 无用或重复的文件

#### 📁 数据文件重命名建议
当前 data 目录结构混乱：
```
data/
├── body_weight_guide.md          → 保留（文档）
├── command_snippets.json         → 保留（命令片段数据）
├── common_paths.json             → 保留（路径预设）
├── data_format_guide.md          → 保留（文档）
├── exam_announcement_sites.json  → 合并到 exam_sites.json
├── exam_official_sites.json      → 合并到 exam_sites.json
├── passwords.json                → 保留（密码管理数据）
├── media_collection/             → 重命名为 media_shelf/
├── prompt_library/               → 重命名为 prompt_bank/
└── text_documents/               → 保留
```

### 4. 脚本文件清理

#### scripts/ 目录
```
scripts/
├── fix_mount_d.sh           → 删除（特定环境脚本）
├── init_body_weight_db.py   → 保留（数据库初始化）
├── package_simple.sh        → 删除（已有 package.sh）
├── path_picker.py           → 保留（路径选择功能）
└── README.md                → 保留
```

### 5. 文档文件整理

#### docs/ 目录
```
docs/
├── ARCHITECTURE.md           → 保留
├── batch_extract.md          → 移动到 tools/batch_extract_7z.md
├── export_dir_structure.md   → 移动到 tools/export_dir_structure.md
├── QUICK_START.md            → 保留
└── README.md                 → 新建（文档索引）
```

## 清理步骤

### 第一阶段：删除重复工具
1. ✅ 删除 `tools/code_snippets.py`（保留 command_snippets）
2. ✅ 合并 `kafka_consumer.py` 和 `kafka_producer.py` 为 `kafka_tool.py`

### 第二阶段：合并相似功能
3. ⚠️ 评估是否合并 `shore_info.py` 和 `provincial_exam.py`
4. ✅ 合并考试相关的JSON数据文件

### 第三阶段：数据目录重组
5. ✅ 重命名 `data/media_collection/` → `data/media_shelf/`
6. ✅ 重命名 `data/prompt_library/` → `data/prompt_bank/`
7. ✅ 合并考试相关JSON文件

### 第四阶段：清理脚本和文档
8. ✅ 删除无用脚本
9. ✅ 整理文档结构

## 预期效果

### 代码减少
- 删除 ~450 行（code_snippets.py）
- 合并 Kafka 工具，减少 ~200 行重复代码
- 总计减少约 **650+ 行代码**

### 文件减少
- 工具文件：从 19 个减少到 16 个（-3）
- 数据文件：更清晰的命名和组织
- 脚本文件：从 5 个减少到 3 个（-2）

### 维护性提升
- ✅ 消除功能重复
- ✅ 统一数据存储方式
- ✅ 更清晰的目录结构
- ✅ 更容易理解和扩展

## 风险评估

### 低风险操作
- 删除 `code_snippets.py`（未使用）
- 删除 `fix_mount_d.sh`（特定环境）
- 删除 `package_simple.sh`（已有替代）

### 中风险操作
- 合并 Kafka 工具（需要测试）
- 重命名数据目录（需要更新代码引用）

### 需要用户确认
- 是否合并考试信息工具
- 是否保留某些特定脚本

## 实施建议

1. **先备份**：`git commit -am "backup before cleanup"`
2. **分步执行**：每个阶段单独提交
3. **测试验证**：每步完成后测试相关功能
4. **文档更新**：同步更新 README 和文档
