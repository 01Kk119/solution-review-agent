$ErrorActionPreference = "Stop"

$ConsoleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$CodeRoot = Split-Path -Parent $ConsoleRoot
$Python = if ($env:CODEX_BUNDLED_PYTHON) { $env:CODEX_BUNDLED_PYTHON } else { "python.exe" }
$DistRoot = Join-Path $CodeRoot "dist"
$KnowledgeRoot = Get-ChildItem -LiteralPath $CodeRoot -Directory |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "agent\03_knowledge") } |
    Select-Object -First 1
if ($null -eq $KnowledgeRoot) {
    throw "Knowledge directory not found."
}

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "SolutionReviewAgent" `
    --icon (Join-Path $ConsoleRoot "assets\review-console-v2.ico") `
    --paths $ConsoleRoot `
    --add-data "$(Join-Path $ConsoleRoot 'static');static" `
    --add-data "$($KnowledgeRoot.FullName);knowledge" `
    --hidden-import pypdf `
    --distpath $DistRoot `
    --workpath (Join-Path $CodeRoot "build\pyinstaller") `
    --specpath (Join-Path $CodeRoot "build") `
    (Join-Path $ConsoleRoot "portable_launcher.py")

Write-Host "Built: $(Join-Path $DistRoot 'SolutionReviewAgent.exe')"
