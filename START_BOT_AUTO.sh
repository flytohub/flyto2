#!/bin/bash
# Flyto2 One-Click Auto Setup & Start
# 一鍵自動安裝所有依賴並啟動機器人

set -e  # Exit on error

echo "========================================================================"
echo "🚀 Flyto2 Bot - Auto Setup & Start"
echo "   一鍵安裝所有依賴並啟動"
echo "========================================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "📍 Working directory: $SCRIPT_DIR"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install with progress
install_with_progress() {
    local name=$1
    shift
    echo -e "${YELLOW}⏳ Installing $name...${NC}"
    "$@"
    echo -e "${GREEN}✅ $name installed${NC}"
}

# 1. Check Python
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Checking Python..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found!${NC}"
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi

# 2. Check/Install Homebrew (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "2️⃣  Checking Homebrew..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if command_exists brew; then
        echo -e "${GREEN}✓ Homebrew found${NC}"
    else
        echo -e "${YELLOW}⏳ Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo -e "${GREEN}✅ Homebrew installed${NC}"
    fi
fi

# 3. Check/Install GitHub CLI
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Checking GitHub CLI..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command_exists gh; then
    GH_VERSION=$(gh --version | head -1)
    echo -e "${GREEN}✓ GitHub CLI found: $GH_VERSION${NC}"
else
    echo -e "${YELLOW}⏳ Installing GitHub CLI...${NC}"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gh
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        sudo apt update
        sudo apt install gh
    fi

    echo -e "${GREEN}✅ GitHub CLI installed${NC}"
fi

# Check if authenticated
if gh auth status >/dev/null 2>&1; then
    echo -e "${GREEN}✓ GitHub authenticated${NC}"
else
    echo -e "${YELLOW}⚠️  GitHub not authenticated${NC}"
    echo "   You can authenticate later with: gh auth login"
fi

# 4. Install Python Dependencies
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Installing Python Dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if pip is available
if ! command_exists pip3; then
    echo -e "${YELLOW}⏳ Installing pip...${NC}"
    python3 -m ensurepip --upgrade
fi

echo -e "${YELLOW}⏳ Installing core dependencies...${NC}"
pip3 install --upgrade pip setuptools wheel -q

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt -q --exists-action i
    echo -e "${GREEN}✅ Core dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found, installing essential packages...${NC}"
    pip3 install -q --exists-action i \
        python-telegram-bot \
        playwright \
        openai \
        qdrant-client \
        python-dotenv \
        aiohttp \
        pyyaml \
        requests
    echo -e "${GREEN}✅ Essential packages installed${NC}"
fi

# 5. Install Playwright Browsers
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Installing Playwright Browsers..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if python3 -c "import playwright" 2>/dev/null; then
    echo -e "${YELLOW}⏳ Installing Chromium browser...${NC}"
    playwright install chromium
    echo -e "${GREEN}✅ Playwright browsers installed${NC}"
else
    echo -e "${YELLOW}⚠️  Playwright not found in pip install${NC}"
fi

# 6. Check Environment Variables
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  Checking Environment Variables..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "   Creating template .env file..."

    cat > .env << 'EOF'
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant Cloud
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here

# Ollama (optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# GitHub (optional, for auto PR creation)
GITHUB_TOKEN=your_github_token_here
EOF

    echo -e "${GREEN}✅ Template .env created${NC}"
    echo -e "${YELLOW}   ⚠️  Please edit .env and add your API keys${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"

    # Check for required keys
    source .env

    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" == "your_telegram_bot_token_here" ]; then
        echo -e "${YELLOW}   ⚠️  TELEGRAM_BOT_TOKEN not set${NC}"
    else
        echo -e "${GREEN}   ✓ TELEGRAM_BOT_TOKEN configured${NC}"
    fi

    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" == "your_openai_api_key_here" ]; then
        echo -e "${YELLOW}   ⚠️  OPENAI_API_KEY not set${NC}"
    else
        echo -e "${GREEN}   ✓ OPENAI_API_KEY configured${NC}"
    fi

    if [ -z "$QDRANT_URL" ] || [ "$QDRANT_URL" == "your_qdrant_url_here" ]; then
        echo -e "${YELLOW}   ⚠️  QDRANT credentials not set${NC}"
    else
        echo -e "${GREEN}   ✓ QDRANT credentials configured${NC}"
    fi
fi

# 7. Test Knowledge Base
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  Testing System..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -e "${YELLOW}⏳ Testing module registry...${NC}"
if python3 -c "from src.core.modules.registry import ModuleRegistry; print(f'Modules loaded: {len(ModuleRegistry.list_all())}')"; then
    echo -e "${GREEN}✅ Module registry working${NC}"
else
    echo -e "${RED}✗ Module registry test failed${NC}"
fi

# 8. Summary
echo ""
echo "========================================================================"
echo "📊 Setup Summary"
echo "========================================================================"
echo ""

# Count what's ready
READY_COUNT=0
TOTAL_COUNT=7

if command_exists python3; then ((READY_COUNT++)); fi
if [[ "$OSTYPE" == "darwin"* ]] && command_exists brew; then ((READY_COUNT++)); fi
if command_exists gh; then ((READY_COUNT++)); fi
if command_exists pip3; then ((READY_COUNT++)); fi
if python3 -c "import playwright" 2>/dev/null; then ((READY_COUNT++)); fi
if [ -f ".env" ]; then ((READY_COUNT++)); fi
if python3 -c "from src.core.modules.registry import ModuleRegistry" 2>/dev/null; then ((READY_COUNT++)); fi

echo "✅ Ready: $READY_COUNT/$TOTAL_COUNT"
echo ""

if [ $READY_COUNT -eq $TOTAL_COUNT ]; then
    echo -e "${GREEN}🎉 All dependencies installed!${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🚀 Starting Bot..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Check if bot script exists
    if [ -f "scripts/interactive_evolution_bot.py" ]; then
        python3 scripts/interactive_evolution_bot.py
    else
        echo -e "${YELLOW}⚠️  Bot script not found at scripts/interactive_evolution_bot.py${NC}"
        echo "   Available commands:"
        echo "   - python3 test_end_to_end.py          # Test system"
        echo "   - python3 test_difficult_questions.py # Test AI responses"
        echo "   - python3 test_pr_creation.py         # Test PR creation"
    fi
else
    echo -e "${YELLOW}⚠️  Some dependencies need attention${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your API keys"
    echo "2. If needed: gh auth login"
    echo "3. Run this script again: ./START_BOT_AUTO.sh"
fi

echo ""
echo "========================================================================"
