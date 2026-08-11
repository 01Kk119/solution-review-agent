param(
  [Parameter(Mandatory = $true)]
  [string]$InputDir,

  [Parameter(Mandatory = $true)]
  [string]$ProjectKey,

  [Parameter(Mandatory = $true)]
  [string]$ProjectName,

  [string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path -LiteralPath (Join-Path $scriptRoot "..")
$migrationRoot = Resolve-Path -LiteralPath (Join-Path $workspaceRoot "..\..")
$skillCli = Join-Path $workspaceRoot "skills\project_requirement_package_builder\src\index.py"

if (-not $OutputRoot) {
  $OutputRoot = if ($env:REVIEW_AGENT_RUNTIME_PATH) {
    $env:REVIEW_AGENT_RUNTIME_PATH
  } else {
    Join-Path $migrationRoot "02_项目资料与运行数据\Agent运行数据"
  }
  $OutputRoot = Join-Path $OutputRoot "output"
}

$inputPath = Resolve-Path -LiteralPath $InputDir
$outputDir = Join-Path $OutputRoot $ProjectKey
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

python $skillCli extract --input $inputPath --output $outputDir --project-name $ProjectName
python $skillCli scaffold --output $outputDir --project-name $ProjectName

Write-Host ""
Write-Host "Stage-1 extract and scaffold completed: $outputDir"
Write-Host "Next: follow SKILL.md to produce project_requirement_package.md, missing_info_checklist.md, metadata.json, and evidence_index.json."
