@echo off
chcp 65001 >nul
setlocal

REM =============================================================================
REM 从 Windows 双击启动 Wintool（实际在 WSL 里跑 Flask）。
REM 请把 WSL_PROJECT 改成你在 WSL 中的项目路径（Linux 风格，如 /home/你的用户名/workdir/wintool）
REM 若默认发行版不是你要用的，取消下一行注释并填写发行版名称（wsl -l -v 查看）
REM =============================================================================
set "WSL_PROJECT=/home/ian/workdir/wintool"
REM set "WSL_DISTRO=Ubuntu"

where wsl >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到 wsl.exe，请先安装并启用 WSL。
    pause
    exit /b 1
)

echo 正在通过 WSL 启动 Wintool...
if defined WSL_DISTRO (
    wsl.exe -d "%WSL_DISTRO%" bash -lc "cd '%WSL_PROJECT%' && exec bash ./start_wintool_wsl.sh"
) else (
    wsl.exe bash -lc "cd '%WSL_PROJECT%' && exec bash ./start_wintool_wsl.sh"
)

set "ERR=%ERRORLEVEL%"
if not "%ERR%"=="0" (
    echo.
    echo 启动脚本返回错误码 %ERR%，请检查 WSL 内路径与依赖（python3 / venv）。
    pause
)
exit /b %ERR%
