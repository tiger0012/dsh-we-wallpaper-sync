#!/bin/bash
# 小红书壁纸下载助手：steamcmd(容器) 批量下载 WE(431960) 创意工坊作品
# 用法: ./scripts/we-download.sh <Steam账号> <作品ID> [作品ID...]
# 环境变量 STEAMCMD_PROXY=1 时走 ~/Steam/steam.cfg 里的 SocksProxy
set -euo pipefail
USER="${1:?usage: we-download.sh <账号> <ID> [ID...]}"; shift
[ $# -ge 1 ] || { echo "至少一个作品 ID"; exit 1; }
mkdir -p ~/Steam/steamapps
ARGS=(); for id in "$@"; do ARGS+=( "+workshop_download_item" "431960" "$id" ); done
printf '<密码>\n' | docker run --rm -i --network host \
  -v ~/Steam/steamapps:/data \
  -v ~/Steam/steam.cfg:/root/.local/share/Steam/steamcmd/steam.cfg \
  steamcmd/steamcmd +login "$USER" +force_install_dir /data "${ARGS[@]}" +quit
