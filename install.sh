#!/usr/bin/env bash
# niuma-charger 安装/更新脚本：检查 SwiftBar → 装插件 → 引导配置（重跑即更新，配置保留）
set -euo pipefail

PLUGIN_DIR="$HOME/Library/Application Support/SwiftBar/Plugins"
CONFIG_DIR="$HOME/.config/swiftbar"
CONFIG="$CONFIG_DIR/encourage.json"
HERE="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d /Applications/SwiftBar.app ] && [ ! -d "$HOME/Applications/SwiftBar.app" ]; then
  echo "⚠ 未检测到 SwiftBar，请先安装后重跑本脚本："
  echo "    brew install --cask swiftbar   （或到 https://swiftbar.app 下载）"
  exit 1
fi

mkdir -p "$PLUGIN_DIR"
cp "$HERE/encourage.1m.py" "$PLUGIN_DIR/"
chmod +x "$PLUGIN_DIR/encourage.1m.py"
echo "✓ 插件已安装/更新（$PLUGIN_DIR/encourage.1m.py）"

if [ -f "$CONFIG" ]; then
  echo "✓ 配置已存在，保持不变（${CONFIG}）"
else
  mkdir -p "$CONFIG_DIR"
  read -r -p "月薪（元，直接回车稍后再填）: " SALARY
  case "$SALARY" in ''|*[!0-9]*) SALARY=0 ;; esac
  read -r -p "上下班时间（回车用默认 09:00-18:00，格式：9:30 18:30）: " START END
  START="${START:-09:00}"
  END="${END:-18:00}"
  cat > "$CONFIG" <<EOF
{
  "salary": $SALARY,
  "start": "$START",
  "end": "$END"
}
EOF
  echo "✓ 配置已写入 $CONFIG"
fi

if grep -q '"salary": 0' "$CONFIG"; then
  echo "→ 月薪未设置：编辑 $CONFIG 填入 salary，保存后 1 分钟内生效"
fi
echo "完成，SwiftBar 一分钟内加载菜单栏插件 ⏳"
