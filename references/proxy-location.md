# 代理出口 IP 检查

```bash
# 本机直连出口
curl -s --max-time 10 https://api.ipify.org; echo
# 走代理的出口 IP —— 必须与账号常住地一致
curl -s --max-time 15 -x socks5h://<代理IP>:<端口> https://api.ipify.org; echo
# 查归属地
curl -s --max-time 12 "https://ipinfo.io/<出口IP>/json"
```

判断：出口归属地 = 账号常住地（例：账号美国凤凰城 → 出口需为 US，如 137.131.x.x）。若不一致，后续登录仍会被 Steam 拦。
