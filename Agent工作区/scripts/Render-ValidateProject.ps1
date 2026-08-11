param(
  [Parameter(Mandatory = $true)]
  [string]$ProjectOutputDir
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path -LiteralPath (Join-Path $scriptRoot "..")
$skillCli = Join-Path $workspaceRoot "skills\project_requirement_package_builder\src\index.py"
$outputDir = Resolve-Path -LiteralPath $ProjectOutputDir

python $skillCli render --output $outputDir
python $skillCli validate --output $outputDir

Write-Host ""
Write-Host "Render and validate completed: $outputDir"
