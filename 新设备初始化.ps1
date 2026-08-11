$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$CodeRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$MigrationRoot = Split-Path -Parent $CodeRoot
$DataRoot = Join-Path $MigrationRoot "02_项目资料与运行数据"
$Requirements = Join-Path $CodeRoot "Agent工作区\skills\project_requirement_package_builder\requirements.txt"

if (-not (Test-Path -LiteralPath $DataRoot)) {
    throw "未找到数据目录：$DataRoot。请确保两个迁移目录位于同一个父目录。"
}

$Python = Get-Command python.exe -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $Python) {
    throw "未找到 Python。请安装 Python 3.10+ 并加入 PATH。"
}

if (Test-Path -LiteralPath $Requirements) {
    & $Python.Source -m pip install -r $Requirements
    if ($LASTEXITCODE -ne 0) { throw "Python 依赖安装失败。" }
}

& $Python.Source -m pytest (Join-Path $CodeRoot "review-console") -q
if ($LASTEXITCODE -ne 0) { throw "工作台测试未通过。" }

Write-Host ""
Write-Host "初始化完成。请运行 设置智谱API.cmd 配置密钥，然后打开方案评审工作台。"

