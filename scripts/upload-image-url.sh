#!/usr/bin/env bash
#
# 上传图片到 ImgBB 图床，输出公网直链，供 Seedance 等只接受「图片链接」的 API 使用。
# 无需自建服务器，仅需在 .env 中配置 IMGBB_API_KEY（免费申请：https://api.imgbb.com/）。
#
# 用法:
#   ./scripts/upload-image-url.sh <图片路径> [图片路径2 ...]
# 示例:
#   ./scripts/upload-image-url.sh section02/refs/characters/section02_character_ref_03.jpeg
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 从 .env 读取 IMGBB_API_KEY
if [[ -f "$PROJECT_ROOT/.env" ]]; then
  # shellcheck source=/dev/null
  source "$PROJECT_ROOT/.env"
fi
if [[ -z "$IMGBB_API_KEY" ]]; then
  echo "错误: 未设置 IMGBB_API_KEY。" >&2
  echo "请到 https://api.imgbb.com/ 免费申请 API Key，并写入项目根目录 .env 文件：" >&2
  echo "  IMGBB_API_KEY=你的key" >&2
  exit 1
fi

if [[ $# -eq 0 ]]; then
  echo "用法: $0 <图片路径> [图片路径2 ...]"
  echo "示例: $0 section02/refs/characters/section02_character_ref_03.jpeg"
  exit 1
fi

cd "$PROJECT_ROOT"

for one in "$@"; do
  if [[ ! -f "$one" ]]; then
    echo "跳过（不存在）: $one" >&2
    continue
  fi
  path="$(cd "$(dirname "$one")" && pwd)/$(basename "$one")"
  echo -n "上传: $one ... " >&2
  res=$(curl -s -X POST "https://api.imgbb.com/1/upload?key=$IMGBB_API_KEY" -F "image=@$path")
  if command -v jq &>/dev/null; then
    url=$(echo "$res" | jq -r '.data.url // empty')
    err=$(echo "$res" | jq -r '.error.message // empty')
  else
    url=$(echo "$res" | grep -oE 'https://i\.ibb\.co/[^"]+' | head -1)
    err=$(echo "$res" | grep -o '"message":[^}]*' | sed 's/.*"message":[[:space:]]*"\([^"]*\).*/\1/')
  fi
  if [[ -n "$url" ]]; then
    echo "OK" >&2
    echo "$url"
  else
    echo "失败" >&2
    [[ -n "$err" ]] && echo "  $err" >&2
    echo "$res" | head -c 500 >&2
    echo "" >&2
  fi
done
