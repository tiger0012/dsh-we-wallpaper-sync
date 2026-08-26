# 结构

```
package.json                    # dsh.bundle（市场可安装性要求）
cordis.patch.yml                # 注册技能（customSkillDirs 需按安装实际路径调整）
skills/dsh-we-wallpaper-sync/   # SKILL.md（技能本体）
references/                     # Steam API / steamcmd / 代理 参考
docs/                           # 用法与结构
LICENSE / README.md
```

分三层：`browse`（Steam Web API 搜索）、`fetch`（steamcmd 下载）、`wire`（写入 settings.yaml 接皮肤中心）。
