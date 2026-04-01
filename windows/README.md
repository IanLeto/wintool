# 从 Windows 桌面启动 Wintool

代码在 WSL 里时，可在 **Windows** 侧放一个快捷方式，双击即可在 WSL 中启动服务并（尽量）用系统浏览器打开页面。

## 1. 修改路径

用记事本打开 `StartWintool.bat`，把其中的：

```bat
set "WSL_PROJECT=/home/ian/workdir/wintool"
```

改成你在 WSL 里的真实项目路径（`wsl` 里执行 `pwd` 可见）。

若默认 WSL 发行版不对，取消注释并设置：

```bat
set "WSL_DISTRO=Ubuntu"
```

（名称以 `wsl -l -v` 为准。）

## 2. 放到桌面

- 把 **`StartWintool.bat`** 复制到 Windows 桌面；或  
- 在桌面新建快捷方式，**目标**填该 bat 的完整路径（不要移动 bat 时忘记改快捷方式）。

可选：右键快捷方式 → 属性 → 更改图标，选一个你喜欢的 `.ico`。

## 3. 依赖

- 已安装 WSL，且能在 PowerShell / cmd 里运行 `wsl`。  
- WSL 内项目目录存在 `start_wintool_wsl.sh`（仓库根目录）。  
- 建议在 WSL 里先执行一次：`chmod +x start_wintool_wsl.sh`（从 Windows 用 `wsl bash ./start_wintool_wsl.sh` 时加 `bash` 可不依赖执行位，但直接执行时需要）。  
- Python：使用项目 `.venv` 或系统的 `python3`，与 `start_wintool.command` 相同。

## 4. 端口与日志

与 `start_wintool.command` 一致：**5001**，日志 **`/tmp/wintool.log`**（在 WSL 文件系统内）。

浏览器地址：`http://127.0.0.1:5001`
