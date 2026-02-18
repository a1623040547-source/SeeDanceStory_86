#!/usr/bin/env bash
#
# 上传图片到 server，并输出可公网访问的 HTTP 链接。
# 使用前：在脚本内或 scripts/upload-config.local 中配置 SSH_HOST、REMOTE_PATH、HTTP_BASE_URL。
#
# 用法:
#   ./scripts/upload-image.sh <图片路径> [图片路径2 ...]
# 示例:
#   ./scripts/upload-image.sh section02/phases/phase08/section02_tail_08.png
#

set -e

# ---------- 配置（可在此修改，或使用 scripts/upload-config.local 覆盖）----------
SSH_HOST="${SSH_HOST:-server}"
# 服务器上存放图片的目录（会按需创建）
REMOTE_PATH="${REMOTE_PATH:-/usr/share/nginx/html/seedance}"
# 对应上述目录的 HTTP 访问基础 URL（生成链接用，不要末尾斜杠）
HTTP_BASE_URL="${HTTP_BASE_URL:-https://your-domain.com/seedance}"

if [[ -f "$(dirname "$0")/upload-config.local" ]]; then
  # shellcheck source=upload-config.local
  source "$(dirname "$0")/upload-config.local"
fi

# ---------- 逻辑 ----------
if [[ $# -eq 0 ]]; then
  echo "用法: $0 <图片路径> [图片路径2 ...]"
  echo "示例: $0 section02/phases/phase08/section02_tail_08.png"
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

for one in "$@"; do
  if [[ ! -f "$one" ]]; then
    echo "跳过（不存在）: $one"
    continue
  fi
  name="$(basename "$one")"
  echo "上传: $one -> ${SSH_HOST}:${REMOTE_PATH}/"
  # 先确保远程目录存在，再上传
  ssh "$SSH_HOST" "mkdir -p $REMOTE_PATH"
  scp "$one" "${SSH_HOST}:${REMOTE_PATH}/"
  # 输出 HTTP 链接（将空格等编码为 %20）
  encoded_name=$(echo -n "$name" | sed 's/ /%20/g')
  echo "  -> ${HTTP_BASE_URL}/${encoded_name}"
done
