# push_via_server.ps1 - 通过云服务器中转推送 GitHub
# 用途：本地无法直连 GitHub（TCP 通但 TLS 被重置 / 无代理）时，走"本地 commit -> 服务器中转 -> push GitHub"
# 用法：powershell -ExecutionPolicy Bypass -File "007 项目工具\push_via_server.ps1"
# 前置：本地已 git commit；服务器 SSH 密钥 ~/.ssh/longmarch_ecs 可用；服务器已配置 GitHub 凭据（见脚本末尾注释）
# 网络正常时仍可直接 git push origin develop，本脚本是兜底通道

$ErrorActionPreference = "Stop"
$repo       = "D:\长征文化"
$remote     = "https://github.com/Live-Jerry/longmarch-map.git"
$branch     = "develop"
$sshKey     = "$env:USERPROFILE\.ssh\longmarch_ecs"
$server     = "root@8.133.203.255"
$mirror     = "/root/zcx-git"                 # 服务器中转仓库（首次自动 clone，之后增量 fetch）
$marker     = "$repo\.git\zcx_last_pushed"    # 上次已推送的本地 SHA（git am 会改变 SHA，不能用远程 SHA 做基准）
$tempPatch  = "$env:TEMP\zcx_push_patches"
$tarFile    = "$env:TEMP\zcx_push_patches.tar"

Set-Location $repo

# [1] 读基准 SHA
if (Test-Path $marker) {
    $base = (Get-Content $marker -Raw).Trim()
} else {
    throw "缺少推送基准文件 $marker，首次使用请手动执行：git rev-parse HEAD | Set-Content $marker（前提：当前 HEAD 内容已在 GitHub 上）"
}
Write-Host "[1/6] 基准 SHA: $base"

# [2] 本地确认基准存在 + 有无新提交
git cat-file -e "${base}^{commit}" 2>$null
if ($LASTEXITCODE -ne 0) { throw "本地缺少基准提交 $base，历史异常，需人工检查" }
$revRange = "$base" + "..HEAD"
$newCount = (git log --oneline $revRange | Measure-Object).Count
if ($newCount -eq 0) { Write-Host "      没有新提交，无需推送"; exit 0 }
Write-Host "      待推送提交数: $newCount"

# [3] 生成 patch
Write-Host "[2/6] 生成 patch（$base..HEAD）..."
if (Test-Path $tempPatch) { Remove-Item $tempPatch -Recurse -Force }
New-Item -ItemType Directory -Path $tempPatch | Out-Null
git format-patch $revRange -o $tempPatch --no-stat | Out-Null

# [4] tar + scp 直传服务器
Write-Host "[3/6] 打包传输到服务器..."
tar -cf $tarFile -C $tempPatch .
scp -i $sshKey -o ConnectTimeout=15 -o StrictHostKeyChecking=no $tarFile "${server}:/tmp/zcx_push_patches.tar"
if ($LASTEXITCODE -ne 0) { throw "scp 失败" }

# [5] 服务器：fetch -> reset 到 GitHub 最新 -> am -> push
Write-Host "[4/6] 服务器应用并推送..."
$remoteCmd = @"
set -e
if [ ! -d "$mirror/.git" ]; then
  git clone -q $remote "$mirror"
  cd "$mirror"
  git config user.name '长征文化数字地图项目组'
  git config user.email 'project@longmarch-map.cn'
else
  cd "$mirror"
  git fetch -q origin $branch
fi
git checkout -q $branch 2>/dev/null || git checkout -q -b $branch origin/$branch
git reset --hard -q origin/$branch
rm -rf /tmp/zcx_pd && mkdir /tmp/zcx_pd
tar -xf /tmp/zcx_push_patches.tar -C /tmp/zcx_pd
git am /tmp/zcx_pd/*.patch
git push origin $branch
"@
ssh -i $sshKey -o ConnectTimeout=15 -o StrictHostKeyChecking=no $server $remoteCmd
if ($LASTEXITCODE -ne 0) { throw "服务器推送失败（可能与其他分支推送冲突），需人工处理" }

# [6] 更新基准 + 清理
Write-Host "[5/6] 更新基准并清理..."
git rev-parse HEAD | Set-Content $marker -Encoding ascii
Remove-Item $tempPatch -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $tarFile -Force -ErrorAction SilentlyContinue
ssh -i $sshKey $server "rm -rf /tmp/zcx_pd /tmp/zcx_push_patches.tar" 2>$null

Write-Host "[6/6] 完成！GitHub $branch 已更新到内容 $(git rev-parse --short HEAD)"
Write-Host ""
Write-Host "提示：网络恢复（或开启代理）后可直接 git push origin develop，本脚本仅作兜底。"
Write-Host "服务器 GitHub 凭据存放在 /root/.git-credentials（chmod 600），如需轮换 token 请更新该文件。"
