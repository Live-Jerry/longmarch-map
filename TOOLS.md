# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## Related

- [Agent workspace](/concepts/agent-workspace)

## GitHub 推送（本地网络无法直连 GitHub 时）

- 本地 commit 后运行：powershell -ExecutionPolicy Bypass -File "007 项目工具\push_via_server.ps1"
- 原理：本地生成 patch -> scp 直传云服务器 -> 服务器 git am + push GitHub（服务器访问 GitHub 正常，凭据在 /root/.git-credentials）
- 基准文件：.git/zcx_last_pushed（记录上次已推送的本地 SHA，git am 会改变 SHA 所以不能用远程 SHA）
- 网络正常时仍直接 git push origin develop

