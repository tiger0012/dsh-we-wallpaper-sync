# Steam Web API 参考（WE 创意工坊搜索/详情）

需要 Steam Web API Key（steamcommunity.com/dev/apikey，免费）。网络需能访问 api.steampowered.com（国内需走可用代理）。

## 搜索：QueryFiles（GET）

```bash
curl -s -x socks5h://<代理> \
  "https://api.steampowered.com/IPublishedFileService/QueryFiles/v1/?key=<KEY>&appid=431960&numperpage=15&page=1&sortmethod=totaluniquesubscribers&format=json"
```

- `sortmethod`：`totaluniquesubscribers`（总订阅）/ `trend`（近 7 天）/ `recent`（最新）/ `toprated` / `score`
- `search_text`：关键词搜索
- 返回 `response.total` 与 `response.publishedfiledetails`（默认只给 id；标题/预览需下一步）

## 详情：GetPublishedFileDetails（POST，无需 key）

```bash
curl -s -x socks5h://<代理> -X POST \
  --data-urlencode "itemcount=1" --data-urlencode "publishedfileids[0]=<itemid>" \
  "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
```

返回 `publishedfiledetails[0]`：`title`、`subscriptions`、`preview_url`（images.steamusercontent.com）、`tags`、`file_size`、`file_url`、`description`。

## 注意

- WE 创意工坊总超过 300 万个作品；`totaluniquesubscribers` 通常能拿到热门。
- 预览图可下载后拼成编号网格图（Pillow）发给用户挑选。
