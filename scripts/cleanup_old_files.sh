#!/bin/bash
# 清理過時和臨時文件

echo "🗑️ Flyto2 專案清理"
echo "=" | awk '{printf "%60s\n", $0}' | tr ' ' '='

# 1. 刪除過時的文檔
echo ""
echo "1️⃣ 清理過時文檔..."
rm -f COMPLETE_FEATURE_CHECKLIST.md && echo "   ✅ Deleted: COMPLETE_FEATURE_CHECKLIST.md"
rm -f PROJECT_COMPLETENESS_CHECK.md && echo "   ✅ Deleted: PROJECT_COMPLETENESS_CHECK.md"
rm -f QUICKSTART.md && echo "   ✅ Deleted: QUICKSTART.md"
rm -f SETUP.md && echo "   ✅ Deleted: SETUP.md"

# 2. 清理臨時目錄（保留結構，刪除內容）
echo ""
echo "2️⃣ 清理臨時目錄..."
if [ -d "temp" ]; then
    rm -rf temp/*
    echo "   ✅ Cleaned: temp/"
fi

if [ -d "output" ]; then
    count=$(ls -1 output | wc -l | tr -d ' ')
    rm -rf output/*
    echo "   ✅ Cleaned: output/ ($count files)"
fi

# 3. 清理 metrics 舊資料（保留最新的）
echo ""
echo "3️⃣ 清理 metrics 舊資料..."
if [ -d "metrics" ]; then
    # 只保留最新的 5 個 snapshot
    if [ -d "metrics/snapshots" ]; then
        cd metrics/snapshots
        ls -t | tail -n +6 | xargs -I {} rm -rf {}
        cd ../..
        echo "   ✅ Cleaned old snapshots (kept latest 5)"
    fi
fi

# 4. 清理 Python cache（如果還有殘留）
echo ""
echo "4️⃣ 清理 Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null
echo "   ✅ Cleaned Python cache files"

# 5. 清理 examples（如果跟 workflows 重複）
echo ""
echo "5️⃣ 檢查 examples 目錄..."
if [ -d "examples" ]; then
    echo "   ⚠️ examples/ 目錄存在"
    echo "   💡 如果跟 workflows/ 重複，可手動刪除: rm -rf examples/"
else
    echo "   ✅ examples/ 不存在"
fi

# 6. 檢查 config
echo ""
echo "6️⃣ 檢查 config 目錄..."
if [ -d "config" ]; then
    echo "   ⚠️ config/ 目錄存在"
    ls -lh config/
    echo "   💡 如果沒用到，可手動刪除: rm -rf config/"
else
    echo "   ✅ config/ 不存在"
fi

# 總結
echo ""
echo "=" | awk '{printf "%60s\n", $0}' | tr ' ' '='
echo "✅ 清理完成！"
echo ""
echo "保留的重要目錄："
echo "   ✅ qdrant_storage/ - 向量資料庫 (645 points)"
echo "   ✅ src/ - 原始碼"
echo "   ✅ scripts/ - 腳本"
echo "   ✅ workflows/ - YAML workflows"
echo "   ✅ tests/ - 測試"
echo "   ✅ metrics/ - 指標（部分清理）"
echo ""
echo "已刪除："
echo "   🗑️ 過時文檔 (4 files)"
echo "   🗑️ temp/ 內容"
echo "   🗑️ output/ 內容"
echo "   🗑️ Python cache"
echo "   🗑️ 舊 snapshots"
