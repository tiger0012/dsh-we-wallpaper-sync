#!/bin/bash
# 小红车（Wallpaper Engine，Steam 431960）创意工坊壁纸批量下载（steamcmd + Docker）。
# 免装 Steam/32 位库，使用官方 steamcmd 镜像。
#
# 前置环境变量：
#   STEAM_USER    必填，你的 Steam 账号名（密码走 stdin 交互输入，不进进程参数）
#   DSH_WE_PROXY  选填，SOCKS5 代理，出口 IP 需与账号常住地一致（如 socks5h://<代理IP>:<端口>）
#                 若账号常住地与国内 IP 不符（异地登录会被 Steam 拦截），必须设置。
#
# 用法：
#   export STEAM_USER=你的账号
#   export DSH_WE_PROXY=socks5h://<代理IP>:<端口>
#   ./we_download.sh <作品ID1> <作品ID2> ... 

set -euo pipefail

: "${STEAM_USER:?请先 export STEAM_USER=你的Steam账号名}"
PROXY="${DSH_WE_PROXY:-}"

if [ -z "${1:-}" ]; then
  echo "用法: $0 <作品ID> [作品ID ...]"
  echo "例:   $0 3509243656 3470764447"
  exit 1
fi

mkdir -p "$HOME/Steam/steamcmd" "$HOME/Steam/steamapps"

# 可选：走代理（steamcmd 通过 steam.cfg 读 SocksProxy）
EXTRA_MOUNTS=()
if [ -n "$PROXY" ]; then
  host="${PROXY#*://}"
  printf 'SocksProxy %s\n' "$host" > "$HOME/Steam/steam.cfg"
  EXTRA_MOUNTS=( -v "$HOME/Steam/steam.cfg:/root/.local/share/Steam/steamcmd/steam.cfg" )
  echo ">> 启用代理 $PROXY"
fi

ARGS=()
for id in "$@"; do ARGS+=( "+workshop_download_item" "431960" "$id" ); done

echo ">> 账号: $STEAM_USER   下载 ${#@} 个作品"
echo ">> 登录后逐个下载，耐心等每个 Progress 走完。（开手机令牌会要求 App 确认，请在手机上点允许）"
# 注意：不要挂载空目录覆盖容器内 /root/.local/share/Steam/steamcmd（会破坏自更新）
#      用 +force_install_dir 让内容落到挂载的落盘目录。
docker run --rm -i --network host \
  -v "$HOME/Steam/steamapps:/data" \
  "${EXTRA_MOUNTS[@]}" \
  steamcmd/steamcmd \
  +login "$STEAM_USER" \
  +force_install_dir /data \
  "${ARGS[@]}" +quit

echo
echo ">> 完成！落盘: $HOME/Steam/steamapps/steamapps/workshop/content/431960/"
echo ">> 接入皮肤中心：把库根目录 $HOME/Steam/steamapps 写进 ~/.dsh/settings.yaml 的 skin-wallpaper.weLibraryDirs"
