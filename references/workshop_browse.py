#!/usr/bin/env python3
"""Wallpaper Engine (Steam 431960) 创意工坊浏览菜单：抓列表→取详情→下载预览→拼编号网格图。

环境变量：
  DSH_WE_API_KEY    必填，Steam Web API Key
  DSH_WE_PROXY      必填，SOCKS5 代理（出口 IP 需与账号常住地一致）
  WE_BROWSE_OUTDIR  选填，预览/网格图输出目录（默认当前目录 ./we_browse）

用法（把结果发给用户挑编号，再批量下载）：
  workshop_browse.py popular | trend | recent | search <关键词> [--n 数量]
"""
import json
import os
import subprocess
import sys
import urllib.parse

from PIL import Image, ImageDraw, ImageFont

KEY = os.environ.get("DSH_WE_API_KEY", "")
PROXY = os.environ.get("DSH_WE_PROXY", "")
APPID = 431960
UA = "Mozilla/5.0 (X11; Linux x86_64) Chrome/126.0"
WORK = os.environ.get("WE_BROWSE_OUTDIR", os.path.join(os.getcwd(), "we_browse"))
PREVIEWS = os.path.join(WORK, "previews")
SORTS = {"popular": "totaluniquesubscribers", "trend": "trend", "recent": "recent",
         "toprated": "toprated", "score": "score"}


def curl(url, out=None, timeout=30):
    cmd = ["curl", "-s", "--max-time", str(timeout), "-x", PROXY, "-A", UA]
    if out:
        cmd += ["-o", out]
    cmd.append(url)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 15).returncode


def query_files(sort_method, search_text, num):
    params = {"key": KEY, "appid": APPID, "numperpage": str(num), "page": "1",
              "sortmethod": sort_method, "format": "json"}
    if search_text:
        params["search_text"] = search_text
    url = "https://api.steampowered.com/IPublishedFileService/QueryFiles/v1/?" + \
        urllib.parse.urlencode(params)
    raw = subprocess.run(["curl", "-s", "--max-time", "30", "-x", PROXY, "-A", UA, url],
                         capture_output=True, text=True, timeout=40).stdout
    return json.loads(raw).get("response", {})


def get_details(ids):
    out = {}
    for p in range(0, len(ids), 20):
        chunk = ids[p:p + 20]
        cmd = ["curl", "-s", "--max-time", "40", "-x", PROXY, "-A", UA, "-X", "POST",
               "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/",
               "--data-urlencode", f"itemcount={len(chunk)}"]
        for j, pid in enumerate(chunk):
            cmd += ["--data-urlencode", f"publishedfileids[{j}]={pid}"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        try:
            d = json.loads(r.stdout)
        except json.JSONDecodeError:
            continue
        for it in d.get("response", {}).get("publishedfiledetails", []):
            if it.get("result") == 1:
                out[it["publishedfileid"]] = it
    return out


def download_preview(pid, url, idx):
    if not url:
        return None
    path = os.path.join(PREVIEWS, f"{idx:02d}_{pid}.jpg")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return path
    if curl(url, out=path, timeout=25) != 0 or not os.path.exists(path) or os.path.getsize(path) < 500:
        return None
    return path


def make_grid(items, cols=3):
    cell = 300
    rows = (len(items) + cols - 1) // cols
    W, H = cols * cell, rows * cell
    grid = Image.new("RGB", (W, H), (20, 22, 28))
    draw = ImageDraw.Draw(grid)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except Exception:
        font = small = ImageFont.load_default()
    for i, (pid, img, title) in enumerate(items):
        x, y = (i % cols) * cell, (i // cols) * cell
        try:
            im = Image.open(img).convert("RGB")
            im.thumbnail((cell - 8, cell - 40))
            grid.paste(im, (x + (cell - im.width) // 2, y + 6))
        except Exception:
            pass
        badge = str(i + 1)
        bb = draw.textbbox((0, 0), badge, font=font)
        bw, bh = bb[2] - bb[0] + 16, bb[3] - bb[1] + 12
        draw.rounded_rectangle([x + 10, y + 10, x + 10 + bw, y + 10 + bh], 8, fill=(232, 68, 68))
        draw.text((x + 18, y + 10 + (bh - (bb[3] - bb[1])) // 2 - bb[1]), badge, fill=(255, 255, 255), font=font)
        draw.text((x + 10, y + cell - 34), (title or "")[:14], fill=(230, 230, 235), font=small)
        draw.rectangle([x, y, x + cell - 1, y + cell - 1], outline=(60, 64, 78))
    out = os.path.join(WORK, "menu.png")
    grid.save(out)
    return out


def main():
    if not KEY or not PROXY:
        raise SystemExit("缺少 DSH_WE_API_KEY 或 DSH_WE_PROXY（见文件头注释）")
    args = sys.argv[1:]
    mode = args[0] if args else "popular"
    search_text = args[1] if mode == "search" and len(args) > 1 else ""
    num = 15
    if "--n" in args:
        num = int(args[args.index("--n") + 1])
    os.makedirs(PREVIEWS, exist_ok=True)
    resp = query_files(SORTS.get(mode, "totaluniquesubscribers"), search_text, num)
    ids = [f.get("publishedfileid") for f in resp.get("publishedfiledetails", [])]
    print(f"共 {resp.get('total', 0)} 个结果，抓取前 {len(ids)} 个")
    details = get_details(ids)
    items = []
    for i, pid in enumerate(ids, 1):
        d = details.get(pid, {})
        title = d.get("title") or f"(未知 {pid})"
        prev = download_preview(pid, d.get("preview_url"), i)
        items.append((pid, prev, title))
        print(f"[{i:02d}] {title}  | ID={pid}  订阅={d.get('subscriptions') or 0:,}")
    print(f"预览图: {make_grid(items)}")


if __name__ == "__main__":
    main()
