$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$CodeRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$MigrationRoot = Split-Path -Parent $CodeRoot
$DataRoot = Join-Path $MigrationRoot "02_项目资料与运行数据"

$Required = @(
    (Join-Path $CodeRoot "review-console\app.py"),
    (Join-Path $CodeRoot "Agent工作区\skills\solution-review\SKILL.md"),
    (Join-Path $CodeRoot "Agent知识库\agent\03_knowledge"),
    (Join-Path $DataRoot "工作台数据\review_console.db"),
    (Join-Path $DataRoot "项目记录"),
    (Join-Path $DataRoot "Agent运行数据\output")
)

$Missing = @($Required | Where-Object { -not (Test-Path -LiteralPath $_) })
if ($Missing.Count -gt 0) {
    $Missing | ForEach-Object { Write-Host "缺失：$_" -ForegroundColor Red }
    exit 1
}

Write-Host "迁移目录结构完整。" -ForegroundColor Green
Write-Host "程序目录：$CodeRoot"
Write-Host "数据目录：$DataRoot"

