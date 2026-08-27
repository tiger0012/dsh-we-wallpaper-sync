#!/usr/bin/env python3
"""Wallpaper Engine (Steam 431960) 创意工坊搜索 / 浏览。

环境变量：
  DSH_WE_API_KEY   必填，Steam Web API Key（steamcommunity.com/dev/apikey 免费）
  DSH_WE_PROXY     必填，SOCKS5 代理（出口 IP 需与账号常住地一致），如 socks5h://<代理IP>:<端口>

用法：
  DSH_WE_API_KEY=xxx DSH_WE_PROXY=socks5h://ip:port python3 workshop_search.py popular
  workshop_search.py trend | recent | toprated | score | search <关键词>
"""
import json
import os
import subprocess
import sys
import urllib.parse

KEY = os.environ.get("DSH_WE_API_KEY", "")
PROXY = os.environ.get("DSH_WE_PROXY", "")
APPID = 431960
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/126.0"}
SORTS = {"popular": "totaluniquesubscribers", "trend": "trend", "recent": "recent",
         "toprated": "toprated", "score": "score"}


def curl(url, data=None, out=None, timeout=30):
    cmd = ["curl", "-s", "--max-time", str(timeout), "-x", PROXY, "-A", UA["User-Agent"]]
    if data:
        cmd += ["-X", "POST"]
        for k, v in data.items():
            cmd += ["--data-urlencode", f"{k}={v}"]
    if out:
        cmd += ["-o", out]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 15)
    return r.stdout


def fetch(mode, search_text="", page=1, num=15):
    if not KEY or not PROXY:
        raise SystemExit("缺少 DSH_WE_API_KEY 或 DSH_WE_PROXY（见文件头注释）")
    params = {"key": KEY, "appid": APPID, "numperpage": str(num), "page": str(page),
              "sortmethod": SORTS.get(mode, "trend"), "format": "json"}
    if search_text:
        params["search_text"] = search_text
    url = "https://api.steampowered.com/IPublishedFileService/QueryFiles/v1/?" + \
        urllib.parse.urlencode(params)
    return json.loads(curl(url)).get("response", {})


def get_details(ids):
    out = {}
    for p in range(0, len(ids), 20):
        chunk = ids[p:p + 20]
        data = {"itemcount": str(len(chunk))}
        for j, pid in enumerate(chunk):
            data[f"publishedfileids[{j}]"] = pid
        raw = curl("https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/", data=data)
        try:
            d = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for it in d.get("response", {}).get("publishedfiledetails", []):
            if it.get("result") == 1:
                out[it["publishedfileid"]] = it
    return out


def main():
    args = sys.argv[1:]
    mode = args[0] if args else "popular"
    search_text = args[1] if mode == "search" and len(args) > 1 else ""
    resp = fetch(mode, search_text)
    ids = [f.get("publishedfileid") for f in resp.get("publishedfiledetails", [])]
    print(f"共 {resp.get('total', 0)} 个结果，抓取前 {len(ids)} 个（模式: {mode}）")
    details = get_details(ids)
    for i, pid in enumerate(ids, 1):
        d = details.get(pid, {})
        tags = [t.get("tag") for t in (d.get("tags") or [])][:4]
        desc = (d.get("description") or "").replace("\n", " ")[:90]
        print(f"[{i:02d}] {d.get('title') or '(未知)'}")
        print(f"     ID={pid}  订阅={d.get('subscriptions') or 0:,}  标签: {', '.join(tags)}")
        if desc:
            print(f"     简介: {desc}")
        print(f"     预览: {d.get('preview_url', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
