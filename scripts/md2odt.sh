#!/usr/bin/env bash
# Markdown → ODT 轉換器
#
# 用法：
#   ./scripts/md2odt.sh notes/week05-0327.md
#     → 產生 notes/week05-0327.odt
#
#   ./scripts/md2odt.sh notes/week05-0327.md 期末報告.odt
#     → 產生 期末報告.odt
#
#   ./scripts/md2odt.sh --all
#     → 把 notes/ 下所有 .md 一口氣轉成同檔名 .odt
#
# 依賴：pandoc（brew install pandoc）

set -e

if ! command -v pandoc >/dev/null; then
  echo "需要 pandoc。安裝：brew install pandoc" >&2
  exit 1
fi

convert_one() {
  local src="$1"
  local out="${2:-${src%.md}.odt}"
  local src_dir
  src_dir=$(cd "$(dirname "$src")" && pwd)
  pandoc "$src" \
    --from=markdown \
    --to=odt \
    --standalone \
    --toc \
    --toc-depth=2 \
    --resource-path="$src_dir" \
    -o "$out"
  echo "[ok] $src  →  $out"
}

if [[ "$1" == "--all" ]]; then
  shopt -s globstar nullglob
  for f in notes/**/*.md; do
    convert_one "$f"
  done
elif [[ -n "$1" ]]; then
  convert_one "$1" "$2"
else
  echo "用法: $0 <input.md> [output.odt]   或   $0 --all"
  exit 1
fi
