#!/bin/bash

# macOS 開發環境自動設定腳本
# 此腳本會檢查每個設定是否已完成，若已完成則跳過

set -e  # 遇到錯誤立即停止

echo "====================================="
echo "開始設定 macOS 開發環境"
echo "====================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 工具函數
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
}

# 1. 設定 oh-my-zsh
setup_oh_my_zsh() {
    print_status "檢查 oh-my-zsh 安裝狀態..."

    if [ -d "$HOME/.oh-my-zsh" ]; then
        print_skip "oh-my-zsh 已安裝，跳過安裝步驟"
    else
        print_status "正在安裝 oh-my-zsh..."
        sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
        print_status "oh-my-zsh 安裝完成"
    fi

    # 檢查並設定 git plugin
    if grep -q "plugins=(git)" "$HOME/.zshrc" 2>/dev/null; then
        print_skip "git plugin 已設定，跳過"
    else
        print_status "設定 oh-my-zsh git plugin..."
        # 備份原始 .zshrc
        cp "$HOME/.zshrc" "$HOME/.zshrc.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
        # 設定 git plugin
        sed -i '' 's/plugins=()/plugins=(git)/' "$HOME/.zshrc" 2>/dev/null || echo 'plugins=(git)' >> "$HOME/.zshrc"
        print_status "git plugin 設定完成"
    fi
}

# 2. 安裝 homebrew 與套件
setup_homebrew() {
    print_status "檢查 Homebrew 安裝狀態..."

    if command -v brew >/dev/null 2>&1; then
        print_skip "Homebrew 已安裝，跳過安裝步驟"
    else
        print_status "正在安裝 Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        print_status "Homebrew 安裝完成"
    fi

    # 更新 Homebrew
    print_status "更新 Homebrew..."
    brew update

    # 安裝套件列表
    packages=(git gh fvm neovim openjdk@17 node@22 cocoapods wget)

    for package in "${packages[@]}"; do
        if brew list "$package" >/dev/null 2>&1; then
            print_skip "$package 已安裝，跳過"
        else
            print_status "正在安裝 $package..."
            brew install "$package"
            print_status "$package 安裝完成"
        fi
    done
}

# 3. 設定環境變數 (~/.zshenv)
setup_environment_variables() {
    print_status "設定環境變數..."

    ZSHENV_FILE="$HOME/.zshenv"
    ZSHENV_CONTENT='export PATH="$PATH":"$HOME/.pub-cache/bin"
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
export JAVA_HOME=/opt/homebrew/opt/openjdk@17
export PATH="/Users/paulwu/fvm/default/bin:$PATH"
export PATH="/Applications/Sublime Text.app/Contents/SharedSupport/bin:$PATH"
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH="/opt/homebrew/opt/node@22/bin:$PATH"'

    if [ -f "$ZSHENV_FILE" ] && grep -q "ANDROID_HOME" "$ZSHENV_FILE"; then
        print_skip "環境變數已設定，跳過"
    else
        print_status "寫入環境變數到 ~/.zshenv..."
        # 備份現有檔案
        [ -f "$ZSHENV_FILE" ] && cp "$ZSHENV_FILE" "$ZSHENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        echo "$ZSHENV_CONTENT" > "$ZSHENV_FILE"
        print_status "環境變數設定完成"
    fi
}

# 4. 設定 Claude Code CLI
setup_claude_code() {
    print_status "檢查 Claude Code CLI 安裝狀態..."

    if command -v claude-code >/dev/null 2>&1; then
        print_skip "Claude Code CLI 已安裝，跳過安裝步驟"
    else
        print_status "正在安裝 Claude Code CLI..."
        npm install -g @anthropic-ai/claude-code
        print_status "Claude Code CLI 安裝完成"
    fi

    # 設定 Claude 目錄
    CLAUDE_DIR="$HOME/.claude"
    mkdir -p "$CLAUDE_DIR"

    # 設定 CLAUDE.md
    CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
    CLAUDE_MD_CONTENT='## 開發偏好與工作流程

### 需求釐清
- 如果需求不清楚或有歧義，必須先提出問題確認
- 優先確理解正確，避免做錯方向的開發

### 任務分解
- 偏好小步驟、小改動的開發方式
- 收到需求後，協助將其拆解為可執行的小任務（tasks）
- 每個 task 應該要：
  - 儘可能小且獨立
  - 有明確的編號（如 Task 1, Task 2...）
  - 有清楚的目標和範圍
  - 可以在短時間內完成
  - 由使用者決定要先執行哪個 task
  - 一次專注於一個 task，完成後再進行下一個

### 回應格式
- 除了技術名詞之外，盡量使用繁體中文回覆'

    if [ -f "$CLAUDE_MD" ]; then
        print_skip "CLAUDE.md 已存在，跳過"
    else
        print_status "創建 CLAUDE.md..."
        echo "$CLAUDE_MD_CONTENT" > "$CLAUDE_MD"
        print_status "CLAUDE.md 設定完成"
    fi

    # 設定 settings.json
    SETTINGS_JSON="$CLAUDE_DIR/settings.json"
    SETTINGS_JSON_CONTENT='{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "open '\''raycast://extensions/raycast/raycast/confetti'\''"
          }
        ]
      },
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "open '\''raycast://extensions/raycast/raycast/confetti'\''"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "open '\''raycast://extensions/raycast/raycast/confetti'\''"
          }
        ]
      }
    ]
  },
  "statusLine": {
    "type": "command",
    "command": "printf \"$(git -C \"$(cat | jq -r '\''.workspace.current_dir'\'')\" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '\''no git'\'')\""
  },
  "model": "sonnet"
}'

    if [ -f "$SETTINGS_JSON" ]; then
        print_skip "settings.json 已存在，跳過"
    else
        print_status "創建 settings.json..."
        echo "$SETTINGS_JSON_CONTENT" > "$SETTINGS_JSON"
        print_status "settings.json 設定完成"
    fi
}

# 5. 安裝 Android SDK
setup_android_sdk() {
    print_status "檢查 Android SDK 安裝狀態..."

    SDK_PATH="$HOME/Library/Android/sdk"

    if [ -d "$SDK_PATH/cmdline-tools" ] && [ -f "$SDK_PATH/cmdline-tools/cmdline-tools/bin/sdkmanager" ]; then
        print_skip "Android SDK 已安裝，跳過安裝步驟"
    else
        print_status "正在安裝 Android SDK..."

        # 創建 Android SDK 目錄
        mkdir -p "$SDK_PATH"

        # 下載 Android SDK 命令行工具
        cd /tmp
        wget -O commandlinetools.zip https://dl.google.com/android/repository/commandlinetools-mac-8092744_latest.zip

        # 解壓到 SDK 目錄
        unzip commandlinetools.zip -d "$SDK_PATH/cmdline-tools"

        # 清理下載的文件
        rm commandlinetools.zip

        # 設定環境變數
        export ANDROID_HOME="$SDK_PATH"
        export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools"

        # 安裝必要的 Android SDK 組件
        SDKMANAGER="$SDK_PATH/cmdline-tools/cmdline-tools/bin/sdkmanager"

        yes | "$SDKMANAGER" --licenses
        "$SDKMANAGER" "platform-tools"
        "$SDKMANAGER" "platforms;android-35"
        "$SDKMANAGER" "build-tools;35.0.0"

        print_status "Android SDK 安裝完成"
    fi
}

# 6. 設定 VIM
setup_vim() {
    print_status "設定 VIM 環境..."

    # 設定 IdeaVim
    IDEAVIMRC="$HOME/.ideavimrc"
    IDEAVIMRC_CONTENT='source ~/Dropbox/ideavimrc
nmap zso :source /Users/paulwu/.ideavimrc<CR>'

    if [ -f "$IDEAVIMRC" ]; then
        print_skip ".ideavimrc 已存在，跳過"
    else
        print_status "創建 .ideavimrc..."
        echo "$IDEAVIMRC_CONTENT" > "$IDEAVIMRC"
        print_status ".ideavimrc 設定完成"
    fi

    # 設定 NeoVim
    NVIM_CONFIG_DIR="$HOME/.config/nvim"
    NVIM_INIT="$NVIM_CONFIG_DIR/init.lua"
    NVIM_INIT_CONTENT="vim.keymap.set('n', 'll', '\\$', { noremap = true })
vim.keymap.set('n', 'hh', '^', { noremap = true })
vim.keymap.set('n', 'z;', '\\$a;', { noremap = true })
vim.keymap.set('n', 'z,', '\\$a,', { noremap = true })
vim.keymap.set('n', 'zw', 'vf(%', { noremap = true })
vim.keymap.set('n', 'zq', 'vf{%', { noremap = true })

if vim.g.vscode then
    local fold = {
        fold = function()
            vim.fn.VSCodeNotify(\"editor.fold\")
        end,
        unfold = function()
            vim.fn.VSCodeNotify(\"editor.unfold\")
        end,
    }

    local refactor = {
        rename = function()
            vim.fn.VSCodeNotify(\"editor.action.rename\")
        end,
    }

    local close = {
        all = function()
            vim.fn.VSCodeNotify(\"workbench.action.closeAllEditors\")
        end,
        current = function()
            vim.fn.VSCodeNotify(\"workbench.action.closeActiveEditor\")
        end,
    }

    local dart = {
        run = function()
            vim.fn.VSCodeNotify(\"workbench.action.debug.run\")
        end,
        test = function()
            vim.fn.VSCodeNotify(\"testing.runAll\")
        end,
        build = function()
            vim.fn.VSCodeNotify(\"workbench.action.tasks.runTask\", \"build:runner\")
        end,
        buildClean = function()
            vim.fn.VSCodeNotify(\"workbench.action.tasks.runTask\", \"build:runner:clean\")
        end,
    }

    local nav = {
        definition = function()
            vim.fn.VSCodeNotify(\"editor.action.revealDefinition\")
        end,
        back = function()
            vim.fn.VSCodeNotify(\"workbench.action.navigateBack\")
        end,
    }

    vim.keymap.set('n', 'ze', fold.unfold)
    vim.keymap.set('n', 'zc', fold.fold)

    vim.keymap.set('n', 'qa', close.all)
    vim.keymap.set('n', 'qq', close.current)

    vim.keymap.set('n', 'zrr', refactor.rename)
    vim.keymap.set('n', 'zra', dart.run)
    vim.keymap.set('n', 'zrt', dart.test)
    vim.keymap.set('n', 'zrb', dart.build)
    vim.keymap.set('n', 'zrbb', dart.buildClean)

    vim.keymap.set('n', 'zf', nav.definition)
    vim.keymap.set('n', 'zk', nav.back)
else
    -- ordinary Neovim
end"

    if [ -f "$NVIM_INIT" ]; then
        print_skip "NeoVim init.lua 已存在，跳過"
    else
        print_status "創建 NeoVim 設定..."
        mkdir -p "$NVIM_CONFIG_DIR"
        echo "$NVIM_INIT_CONTENT" > "$NVIM_INIT"
        print_status "NeoVim init.lua 設定完成"
    fi
}

# 7. 提示使用者設定機密資料
setup_secrets() {
    print_status "檢查機密資料設定..."

    if grep -q "NOTION_SECRET" "$HOME/.zshrc" 2>/dev/null && grep -q "MEDIUM_TOKEN" "$HOME/.zshrc" 2>/dev/null; then
        print_skip "基本機密資料已設定，跳過"
    else
        print_warning "需要設定機密資料到 ~/.zshrc"
        echo ""
        echo "請手動將以下內容加入到 ~/.zshrc："
        echo ""
        echo 'export NOTION_SECRET="your_notion_secret"'
        echo 'export MEDIUM_TOKEN="your_medium_token"  # 從 Medium Settings -> Security and apps -> Integration tokens 取得'
        echo ""
        read -p "請輸入您的 NOTION_SECRET: " notion_secret
        read -p "請輸入您的 MEDIUM_TOKEN: " medium_token

        # 備份 .zshrc
        cp "$HOME/.zshrc" "$HOME/.zshrc.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true

        # 添加機密資料
        echo "" >> "$HOME/.zshrc"
        echo "# 機密資料設定" >> "$HOME/.zshrc"
        echo "export NOTION_SECRET=\"$notion_secret\"" >> "$HOME/.zshrc"
        echo "export MEDIUM_TOKEN=\"$medium_token\"" >> "$HOME/.zshrc"

        print_status "機密資料已添加到 ~/.zshrc"
    fi

    # 檢查 MEDIUM_USER_ID
    if grep -q "MEDIUM_USER_ID" "$HOME/.zshrc" 2>/dev/null; then
        print_skip "MEDIUM_USER_ID 已設定，跳過"
    else
        print_status "使用 get_medium_user_id.py 取得 Medium User ID..."

        if [ -f "get_medium_user_id.py" ]; then
            # 載入環境變數
            source "$HOME/.zshrc" 2>/dev/null || true

            # 執行腳本取得 User ID
            medium_user_id=$(python3 get_medium_user_id.py 2>/dev/null || echo "")

            if [ -n "$medium_user_id" ]; then
                echo "export MEDIUM_USER_ID=\"$medium_user_id\"" >> "$HOME/.zshrc"
                print_status "MEDIUM_USER_ID 已設定: $medium_user_id"
            else
                print_warning "無法自動取得 MEDIUM_USER_ID，請手動設定"
                read -p "請輸入您的 MEDIUM_USER_ID: " manual_user_id
                echo "export MEDIUM_USER_ID=\"$manual_user_id\"" >> "$HOME/.zshrc"
                print_status "MEDIUM_USER_ID 已手動設定"
            fi
        else
            print_warning "找不到 get_medium_user_id.py 檔案"
            read -p "請輸入您的 MEDIUM_USER_ID: " manual_user_id
            echo "export MEDIUM_USER_ID=\"$manual_user_id\"" >> "$HOME/.zshrc"
            print_status "MEDIUM_USER_ID 已手動設定"
        fi
    fi
}

# 主要執行流程
main() {
    print_status "開始執行 macOS 開發環境設定..."

    setup_oh_my_zsh
    setup_homebrew
    setup_environment_variables
    setup_claude_code
    setup_android_sdk
    setup_vim
    setup_secrets

    echo ""
    echo "====================================="
    echo -e "${GREEN}✅ macOS 開發環境設定完成！${NC}"
    echo "====================================="
    echo ""
    echo "📝 後續步驟："
    echo "1. 重新啟動終端機或執行: source ~/.zshrc"
    echo "2. 確認所有環境變數已正確載入"
    echo "3. 測試各項工具是否正常運作"
    echo ""
}

# 執行主函數
main "$@"