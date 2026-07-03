# 原型文件（Prototypes）使用指南

## 📁 目录结构

### 外网环境（开发/打包）
```
wintool/
├── prototypes/             # 原型文件目录
│   ├── example.html        # 示例原型
│   ├── design1.html        # 你的原型文件
│   └── design2.html        # 更多原型...
├── pack.sh                 # 打包脚本
└── backend-python/
    └── app.py              # 后端服务
```

### 内网环境（解压后）
```
wintool-inner-20260702_162343/
├── prototypes/              # 原型文件目录（自动复制）
│   ├── example.html        # 所有 HTML 文件
│   └── ...
├── backend-python/
│   └── app.py              # 会从 ../prototypes 读取
├── start.sh
└── ...
```

---

## 🚀 使用方法

### 1️⃣ 外网环境：添加原型文件

在打包**之前**，将你的 HTML 原型文件放到 `prototypes/` 目录：

```bash
# 在项目根目录
cd /path/to/wintool

# 复制你的原型文件
cp /path/to/your/design.html prototypes/

# 或者直接在 prototypes 目录创建
vim prototypes/my-prototype.html
```

### 2️⃣ 打包到内网

运行打包脚本，会自动包含 `prototypes/` 目录：

```bash
./pack.sh
```

输出示例：
```
[INFO]   [7/8] 复制原型文件...
[INFO]       已复制 prototypes 目录（3 个 HTML 文件）
```

### 3️⃣ 内网环境：使用原型

解压后，原型文件会在 `prototypes/` 目录：

```bash
# 解压
unzip -P 123 wintool-inner-20260702_162343.zip
cd wintool-inner-20260702_162343

# 查看原型文件
ls prototypes/
# 输出: example.html  design1.html  design2.html

# 启动服务
./start.sh
```

### 4️⃣ 访问原型

启动服务后，通过以下方式访问：

#### 方式1：通过前端界面（推荐）
1. 打开浏览器：`http://localhost:8080`
2. 点击"原型预览"工具
3. 选择要查看的原型文件

#### 方式2：直接访问 API
```bash
# 获取原型列表
curl http://localhost:8080/api/prototypes/list

# 直接访问原型文件
curl http://localhost:8080/prototypes/example.html
```

#### 方式3：浏览器直接打开
```
http://localhost:8080/prototypes/example.html
http://localhost:8080/prototypes/design1.html
```

---

## 📝 后端 API 说明

### 获取原型列表
```http
GET /api/prototypes/list
```

响应示例：
```json
{
  "success": true,
  "prototypes": [
    {
      "name": "example.html",
      "path": "example.html",
      "size": 15349,
      "modified": 1719907128
    }
  ],
  "total": 1
}
```

### 预览原型文件
```http
GET /api/prototypes/view/<file_path>
```

示例：
```
GET /api/prototypes/view/example.html
```

### 直接访问原型
```http
GET /prototypes/<filename>
```

示例：
```
GET /prototypes/example.html
```

---

## 🔧 代码实现

### backend-python/app.py（第 558 行）

```python
# 原型文件目录
PROTOTYPES_DIR = Path(__file__).parent.parent / "prototypes"
```

**路径解析**：
- `Path(__file__).parent` = `backend-python/`
- `.parent` = 项目根目录
- `/ "prototypes"` = `项目根目录/prototypes/`

### pack.sh（第 167-176 行）

```bash
# 复制原型文件目录
echo_info "  [7/8] 复制原型文件..."
if [[ -d "$SCRIPT_DIR/prototypes" ]]; then
    cp -r "$SCRIPT_DIR/prototypes" "$TEMP_DIR/"
    echo_info "      已复制 prototypes 目录（X 个 HTML 文件）"
else
    mkdir -p "$TEMP_DIR/prototypes"
    echo_info "      已创建 prototypes 目录（空）"
fi
```

---

## ✅ 完整工作流程

### 外网环境（开发者）

1. **添加原型文件**
   ```bash
   cp my-design.html prototypes/
   ```

2. **打包**
   ```bash
   ./pack.sh
   # 输出: wintool-inner-20260702_162343.zip
   ```

3. **发送到内网**
   - 通过邮件/U盘等方式传输 zip 文件

### 内网环境（用户）

1. **解压**
   ```bash
   unzip -P 123 wintool-inner-20260702_162343.zip
   cd wintool-inner-20260702_162343
   ```

2. **查看原型文件**
   ```bash
   ls prototypes/
   # example.html  my-design.html
   ```

3. **启动服务**
   ```bash
   ./start.sh
   ```

4. **访问原型**
   - 浏览器打开：`http://localhost:8080`
   - 进入"原型预览"工具
   - 或直接访问：`http://localhost:8080/prototypes/my-design.html`

---

## 🎯 常见问题

### Q1: 我的原型文件应该放在哪里？

**A**: 在**外网环境**打包之前，放到项目根目录的 `prototypes/` 目录。

```bash
wintool/
└── prototypes/          # 这里！
    └── your-file.html
```

### Q2: 打包后原型文件在哪里？

**A**: 解压后在根目录的 `prototypes/` 目录。

```bash
wintool-inner-xxx/
└── prototypes/          # 这里！
    └── your-file.html
```

### Q3: 如何在内网添加新的原型文件？

**A**: 直接复制到 `prototypes/` 目录，无需重启服务：

```bash
# 内网环境
cd wintool-inner-xxx
cp /path/to/new-design.html prototypes/

# 刷新浏览器即可看到新文件
```

### Q4: 支持子目录吗？

**A**: 支持！可以创建子目录组织文件：

```bash
prototypes/
├── mobile/
│   ├── app1.html
│   └── app2.html
└── web/
    ├── dashboard.html
    └── login.html
```

访问方式：
```
http://localhost:8080/prototypes/mobile/app1.html
http://localhost:8080/prototypes/web/dashboard.html
```

### Q5: 原型文件可以引用外部资源吗？

**A**: 可以，但建议使用相对路径或内嵌资源：

```html
<!-- ✅ 推荐：内嵌 CSS/JS -->
<style>
  /* 样式 */
</style>

<!-- ✅ 推荐：CDN 资源（如果内网可访问） -->
<script src="https://cdn.jsdelivr.net/npm/vue@3"></script>

<!-- ⚠️ 注意：相对路径需要放在 prototypes 目录内 -->
<img src="./images/logo.png">  <!-- prototypes/images/logo.png -->
```

---

## 📊 目录对比

| 环境 | 原型文件位置 | 后端代码位置 | 相对路径 |
|------|------------|------------|---------|
| **外网开发** | `wintool/prototypes/` | `wintool/backend-python/app.py` | `../prototypes` |
| **内网运行** | `wintool-inner-xxx/prototypes/` | `wintool-inner-xxx/backend-python/app.py` | `../prototypes` |

**结论**：两个环境的相对路径一致，无需修改代码！

---

## 🎉 总结

### 关键点

1. ✅ **外网打包前**：将 HTML 文件放到 `prototypes/` 目录
2. ✅ **pack.sh 自动复制**：打包时会自动包含 `prototypes/` 目录
3. ✅ **内网解压后**：原型文件在根目录的 `prototypes/` 目录
4. ✅ **访问方式**：通过前端界面或直接访问 `/prototypes/xxx.html`

### 一句话总结

**在外网的 `prototypes/` 目录放 HTML 文件，打包后会自动复制到内网，启动服务后通过浏览器访问即可！**

---

## 📞 技术支持

如有问题，请查看：
- `backend-python/app.py` 第 555-637 行（原型预览 API）
- `pack.sh` 第 167-176 行（原型文件复制逻辑）
