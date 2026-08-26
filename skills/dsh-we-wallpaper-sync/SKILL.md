---
name: dsh-we-wallpaper-sync
description: '用于 Agent 把 Wallpaper Engine（小红车/小红书壁纸，Steam 应用 431960）创意工坊壁纸批量浏览、搜索、下载并接入 DSH 皮肤中心：覆盖 Steam Web API 搜索、steamcmd+Docker 下载、绕过国内 Steam HTTP 封锁与「账号常住地与登录 IP 不符」的异地登录拦截、落盘到 ~/Steam/steamapps、把库根目录写进 settings.yaml 让皮肤中心 WE 桥扫描、以及 inventory 验证。'
---

# dsh-we-wallpaper-sync

把 Wallpaper Engine（WE，Steam 应用 `431960`，俗称小红车）创意工坊壁纸下载到本机，并让 DSH 皮肤中心（`@linxin666/dsh-client-ui-skin-center` 的 Wallpaper Engine 桥）能扫到、应用为 GUI 背景的完整流程。

## 适用边界

- 本机需要有 Docker（steamcmd 官方镜像自带 32 位库，无需装系统库、无需 root）。
- 需要用户的 Steam 账号已**购买** Wallpaper Engine（431960），且能通过 Steam Web API Key 或 steamcmd 登录。
- 目标是「拿到壁纸文件 + 接入皮肤中心」，不是跑 WE 本体（WE 是 Windows 应用，Linux 上场景壁纸只能静态帧）。

## 关键事实（这些坑务必记住）

1. **国内网络屏蔽 Steam 的 HTTP 域名**（`steamcommunity.com`、`api.steampowered.com`、`store.steampowered.com` 会超时/被墙），但 **steamcmd 走 Steam CM 网络**（UDP/TCP 27017+），不看 HTTP，直连往往能通。所以「浏览/搜索」要过代理，而 steamcmd 本身直连可能没问题。
2. **异地登录拦截**：Steam 会对比登录来源 IP 与账号常住地。若账号常住美国而 steamcmd 用国内 IP（如四川）登录，Steam 直接拦：`This sign in attempt appears to be a malicious actor or website...`。**解决办法是让 steamcmd 也走一个出口 IP 与账号常住地一致的代理**（经 `steam.cfg` 的 `SocksProxy`）。
3. **先探测、再决定**：任何代理都要先确认它出口 IP 的归属地是否与账号一致，否则白忙。
4. **steamcmd 容器内目录**：官方镜像里 steamcmd 装在 `/root/.local/share/Steam/steamcmd`（以 root 运行）。**不要用空目录挂载覆盖它**，会破坏镜像自更新（`steamcmd.sh not found`）。要用 `+force_install_dir` 把内容落到挂载盘。
5. **免登录第三方下载站不可靠**：`steamworkshopdownloader.io` 前端可达但后端 `POST /api/details/file` 常返回 500，不要依赖。
6. **皮肤中心 WE 桥**会扫 `<库根>/steamapps/workshop/content/431960/`，因此把**库根目录**（含 `steamapps/workshop/content/431960`）写进 `settings.yaml` 的 `skin-wallpaper.weLibraryDirs` 即可。

## 步骤

### 1) 确认代理出口 IP 归属（若需要绕过封锁）

```bash
# 本机直连出口（可能是国内 IP）
curl -s --max-time 10 https://api.ipify.org; echo
# 走代理的出口 IP——必须与账号常住地一致
curl -s --max-time 15 -x socks5h://<代理IP>:<端口> https://api.ipify.org; echo
# 查 IP 归属地
curl -s --max-time 12 "https://ipinfo.io/<出口IP>/json"
```

判断依据：出口 IP 归属地 = 账号常住地（例：账号美国凤凰城 → 出口需为 US，如 `137.131.x.x`）。若一致，后续 steamcmd / Steam API 都走这个代理。

### 2) 浏览 / 搜索创意工坊（Steam Web API，走代理）

需要 **Steam Web API Key**（steamcommunity.com/dev/apikey，免费）。用代理访问，否则被墙。

```bash
# 搜索（QueryFiles，GET）：按订阅数/趋势/最新排序，或关键词
curl -s -x socks5h://<代理> \
  "https://api.steampowered.com/IPublishedFileService/QueryFiles/v1/?key=<KEY>&appid=431960&numperpage=15&page=1&sortmethod=totaluniquesubscribers&format=json"
# 取详情（标题/订阅/预览图）：GetPublishedFileDetails（POST）
curl -s -x socks5h://<代理> -X POST \
  --data-urlencode "itemcount=1" --data-urlencode "publishedfileids[0]=<itemid>" \
  "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
```

- `sortmethod`：`totaluniquesubscribers` / `trend` / `recent` / `toprated` / `score`。
- 预览图字段：`preview_url`（`images.steamusercontent.com/...`）。
- 可把预览图拼成编号网格发给用户挑选（Pillow）。

### 3) 下载（steamcmd + Docker，登录走代理）

```bash
# 写 steam.cfg 指向可用代理（steamcmd 读取它）
printf 'SocksProxy <代理IP>:<端口>\n' > ~/Steam/steam.cfg

mkdir -p ~/Steam/steamapps
# 说明：-v 只挂载落盘目录；不要把 steamcmd 目录挂成空目录
printf '<密码>\n' | docker run --rm -i --network host \
  -v ~/Steam/steamapps:/data \
  -v ~/Steam/steam.cfg:/root/.local/share/Steam/steamcmd/steam.cfg \
  steamcmd/steamcmd \
  +login <账号> \
  +force_install_dir /data \
  +workshop_download_item 431960 <作品ID1> \
  +workshop_download_item 431960 <作品ID2> ... \
  +quit
```

- **登录**：账号开了手机令牌会要求 App 确认（`Please confirm the login in the Steam Mobile app`）——让用户立刻在手机 App 点「允许」（约 2 分钟窗口）；或改用 TOTP 验证码（`+login 账号 密码 5位码`）。
- **落盘**：`/data/steamapps/workshop/content/431960/<作品ID>/`，即宿主机 `~/Steam/steamapps/steamapps/workshop/content/431960/<ID>/`。
- 密码走 stdin（`printf`），不进进程参数。

### 4) 接入皮肤中心

把**库根目录**写进 `~/.dsh/settings.yaml`：

```yaml
skin-wallpaper:
  weLibraryDirs:
    - /home/<user>/Steam/steamapps
```

（`settings.yaml` 热加载；WE 桥会扫 `<库根>/steamapps/workshop/content/431960`。）

### 5) 验证

```bash
curl -s http://127.0.0.1:3080/api/skin-center/we/inventory
# 期望 total 为已下载数量，wallpapers 列出标题/type/source=workshop
```

浏览器中到 **设置 → 皮肤中心 → 壁纸面板** 即可看到并应用。scene 类型在 Linux 上为静态帧；video / web 类型可真动态。

## 失败排查

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| Steam API / steamcommunity 超时(000) | 国内屏蔽 Steam HTTP | 走可用代理（步骤 1 确认出口 IP） |
| `Steam has blocked this sign in` | 登录 IP 与账号常住地不符 | 让 steamcmd 走出口 IP 与账号一致的代理；不要再直连重试 |
| `Timed out waiting for confirmation` | App 确认窗口(约 2min)过了 | 重试并提前让用户拿好手机；或用 TOTP 验证码 |
| `steamcmd.sh not found` | 空目录覆盖了容器内 steamcmd 目录 | 不要挂载覆盖 `/root/.local/share/Steam/steamcmd`；改用 `+force_install_dir` |
| `steamworkshopdownloader.io` 返回 500 | 第三方后端不可靠 | 弃用，用 steamcmd 官方通道 |
| `Insufficient Balance` | 调用的模型 API 账户余额不足 | 充值或换有余量的 key（与技能/代码无关） |

## 相关脚本（本机 workspace 参考）

- `we_download.sh`：steamcmd+Docker 批量下载（含代理 steam.cfg、force_install_dir）。
- `workshop_search.py`：QueryFiles/GetPublishedFileDetails 搜索（curl 子进程，走代理）。
- `workshop_browse.py`：抓列表→取详情→下载预览→拼编号网格图。

将 `<KEY>`/`<密码>`/`<账号>` 替换为实际值；**勿在技能文件里硬编码 API Key 或密码**。
