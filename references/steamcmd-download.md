# steamcmd + Docker 下载参考

## 容器要点

- 官方镜像 `steamcmd/steamcmd` 自带 32 位库，无需装系统库/root。
- 容器内 steamcmd 装在 `/root/.local/share/Steam/steamcmd`（root 身份）。
- **不要用空目录挂载覆盖该目录**（会 `steamcmd.sh not found`）。用 `+force_install_dir /data` 把内容指向挂载盘。

## 命令

```bash
printf 'SocksProxy <代理IP>:<端口>\n' > ~/Steam/steam.cfg   # 关键：让登录走出口 IP 与账号一致的代理
mkdir -p ~/Steam/steamapps
printf '<密码>\n' | docker run --rm -i --network host \
  -v ~/Steam/steamapps:/data \
  -v ~/Steam/steam.cfg:/root/.local/share/Steam/steamcmd/steam.cfg \
  steamcmd/steamcmd \
  +login <账号> \
  +force_install_dir /data \
  +workshop_download_item 431960 <作品ID> \
  +quit
```

- 落盘：`/data/steamapps/workshop/content/431960/<作品ID>/`。
- 登录：手机令牌 → App 确认（约 2 分钟窗口）；或用 TOTP：`+login 账号 密码 5位码`。
- 密码走 stdin（`printf`），不进进程参数。

## 异地登录拦截

若登录 IP 与账号常住地不符，Steam 会拦（`Steam has blocked this sign in`）。解决：让 steamcmd 走出口 IP 与账号一致的 SOCKS 代理（`steam.cfg` 的 `SocksProxy`）。先 `curl -x socks5h://<代理> https://api.ipify.org` + 查归属地确认。
