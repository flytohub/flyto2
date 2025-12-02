@echo off
chcp 65001 >nul
REM Flyto2 Autonomous Self-Evolving AI - Interactive Setup

echo.
echo ╔════════════════════════════════════════╗
echo ║   Flyto2 Autonomous Evolution AI       ║
echo ║     Interactive Setup & Launcher       ║
echo ╚════════════════════════════════════════╝
echo.

REM ========================================
REM Step 1: Check .env configuration
REM ========================================
if not exist .env (
    echo [1/4] 設定檢查
    echo.
    echo ⚠️  找不到 .env 設定檔！
    echo.
    echo 需要設定以下資訊：
    echo   • Telegram Bot Token
    echo   • Telegram User ID
    echo   • OpenAI API Key ^(可選^)
    echo.
    set /p create_env="是否要創建 .env 檔案？(Y/N): "
    if /i "%create_env%"=="Y" (
        echo.
        echo 正在複製 .env.example 到 .env...
        copy .env.example .env >nul
        echo ✅ 已創建 .env 檔案
        echo.
        echo ⚠️  請先編輯 .env 檔案，填入你的 Token！
        echo    然後重新執行 START_BOT.bat
        echo.
        pause
        exit /b
    ) else (
        echo.
        echo ❌ 沒有 .env 檔案無法啟動
        echo    請參考 SETUP.md 文檔設定
        echo.
        pause
        exit /b
    )
) else (
    echo [1/4] ✅ 設定檔檢查完成
    echo.
)

REM ========================================
REM Step 2: Virtual environment
REM ========================================
echo [2/4] 虛擬環境設定
echo.
if exist venv\Scripts\activate.bat (
    echo ✅ 虛擬環境已存在
    call venv\Scripts\activate.bat
) else (
    set /p create_venv="是否要創建 Python 虛擬環境？(Y/N): "
    if /i "%create_venv%"=="Y" (
        echo.
        echo 正在創建虛擬環境...
        python -m venv venv
        call venv\Scripts\activate.bat
        echo ✅ 虛擬環境創建完成
    ) else (
        echo ❌ 跳過虛擬環境
    )
)
echo.

REM ========================================
REM Step 3: Dependencies
REM ========================================
echo [3/4] 依賴套件安裝
echo.
set /p install_deps="是否要安裝/更新依賴套件？(Y/N): "
if /i "%install_deps%"=="Y" (
    echo.
    echo 正在安裝依賴套件...
    pip install -q -r requirements.txt
    echo ✅ 依賴套件安裝完成
) else (
    echo ⚠️  跳過依賴安裝
)
echo.

REM ========================================
REM Step 4: Select mode
REM ========================================
echo [4/4] 啟動模式選擇
echo.
echo 請選擇啟動模式：
echo.
echo [1] 🤖 完全自動模式 - 每小時自動訓練、進化、學習
echo     • 爬網站練習
echo     • 自動進化循環
echo     • 更新向量資料庫
echo     • Telegram 通知
echo.
echo [2] 💬 只啟動 Telegram 聊天機器人
echo     • 對話功能（Ollama + OpenAI）
echo     • 語言選擇
echo     • 向量資料庫管理
echo     • 手動觸發進化
echo.
echo [3] 🔧 互動式進化模式
echo     • 手動控制每個進化步驟
echo     • 即時審核和修改
echo.
echo [0] ❌ 取消
echo.
set /p mode="請輸入選項 (0-3): "

if "%mode%"=="1" (
    echo.
    echo ╔════════════════════════════════════════╗
    echo ║  🤖 啟動完全自動模式                   ║
    echo ║  • 每小時自動訓練                       ║
    echo ║  • 自動進化和學習                       ║
    echo ║  • Telegram 即時通知                    ║
    echo ╚════════════════════════════════════════╝
    echo.
    set /p confirm="確定要啟動嗎？(Y/N): "
    if /i "%confirm%"=="Y" (
        echo.
        echo ▶️  啟動中... Press Ctrl+C to stop
        echo.
        python scripts\autonomous_bot.py
    ) else (
        echo ❌ 已取消
    )
) else if "%mode%"=="2" (
    echo.
    echo ╔════════════════════════════════════════╗
    echo ║  💬 啟動 Telegram 聊天機器人            ║
    echo ║  • 對話功能（三層策略）                 ║
    echo ║  • 使用 /start 查看所有指令             ║
    echo ╚════════════════════════════════════════╝
    echo.
    set /p confirm="確定要啟動嗎？(Y/N): "
    if /i "%confirm%"=="Y" (
        echo.
        echo ▶️  啟動中... Press Ctrl+C to stop
        echo.
        python scripts\telegram_bot_v2.py
    ) else (
        echo ❌ 已取消
    )
) else if "%mode%"=="3" (
    echo.
    echo ╔════════════════════════════════════════╗
    echo ║  🔧 啟動互動式進化模式                  ║
    echo ║  • 手動控制進化步驟                     ║
    echo ║  • 即時審核修改                         ║
    echo ╚════════════════════════════════════════╝
    echo.
    set /p confirm="確定要啟動嗎？(Y/N): "
    if /i "%confirm%"=="Y" (
        echo.
        echo ▶️  啟動中... Press Ctrl+C to stop
        echo.
        python scripts\interactive_evolution_bot.py
    ) else (
        echo ❌ 已取消
    )
) else if "%mode%"=="0" (
    echo.
    echo ❌ 已取消啟動
) else (
    echo.
    echo ❌ 無效的選項！
)

echo.
pause
