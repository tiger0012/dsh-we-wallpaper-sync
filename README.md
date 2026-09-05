# dsh-we-wallpaper-sync

把 Wallpaper Engine（小红车壁纸，Steam 应用 `431960`）创意工坊壁纸批量**浏览、搜索、下载并接入 DSH 皮肤中心**的可复用技能。

## 它能做什么

- 用 Steam Web API Key 搜索/浏览 WE 创意工坊（按订阅数、趋势、最新、关键词），抓标题/订阅/预览图并拼成编号网格供用户挑选。
- 用 `steamcmd` + Docker 批量下载作品（免装 Steam/32 位库、无需 root）。
- **绕过国内对 Steam HTTP 的封锁**与**「账号常住地与登录 IP 不符」的异地登录拦截**：让 steamcmd 也走一个出口 IP 与账号常住地一致的代理。
- 落盘到 `~/Steam/steamapps`，把库根目录写进 `~/.dsh/settings.yaml` 的 `skin-wallpaper.weLibraryDirs`，皮肤中心 WE 桥即可扫到并应用为 GUI 背景。

## 主要坑（技能里有完整清单）

1. 国内封 Steam 的 HTTP 域名，但 `steamcmd` 走 Steam CM 网络（不看 HTTP），直连往往能通。
2. Steam 会对比登录 IP 与账号常住地；不匹配会直接拦截登录（`Steam has blocked this sign in`）——用出口 IP 与账号一致的代理走 `steam.cfg` 的 `SocksProxy` 解决。
3. 容器内 steamcmd 目录是 `/root/.local/share/Steam/steamcmd`，别用空目录挂载覆盖（会 `steamcmd.sh not found`）；用 `+force_install_dir` 落盘。
4. 免登录第三方下载站（steamworkshopdownloader.io）后端常 500，别依赖。
5. 皮肤中心 WE 桥扫 `<库根>/steamapps/workshop/content/431960`。

## 使用

安装后调用技能 `dsh-we-wallpaper-sync`，按其步骤执行；也可直接读取 `SKILL.md` 里的命令。

> ⚠️ 技能内用 `<账号>`/`<KEY>`/`<密码>` 占位，**勿硬编码** Steam API Key 或密码。
> ✅ `cordis.patch.yml` 的 `customSkillDirs` 用 `!!js` 在装载时基于 `loader.filename` 动态解析出包内 `skills/` 绝对路径——无论装到哪个 profile 都能自动定位，**无需手动改配置**。

## 市场条目

PR 到 `awesome-dsh-plugin/awesome-dsh-plugin`，新增 `data/plugins/<owner>__dsh-we-wallpaper-sync.yml`（分类 `skill`），见仓库内生成好的该文件。
