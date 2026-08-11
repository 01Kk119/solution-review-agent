param(
  [Parameter(Mandatory = $true)]
  [string]$ProjectOutputDir,

  [string]$SummaryRoot = "",
  [string]$ProjectKey = "",
  [string]$ReviewStatus = "pending_tpm_review",
  [string]$RiskLevel = "pending",
  [string]$Owner = "",
  [string]$Decision = "",
  [string]$ReviewResultFile = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function ConvertTo-SafeFileName([string]$value) {
  $safe = $value -replace '[\\/:*?"<>|]', '_'
  $safe = $safe -replace '\s+', '_'
  if (-not $safe) { return "unknown_project" }
  return $safe
}

function Get-PendingText() {
  return ([string]([char]0x5f85) + [string]([char]0x786e) + [string]([char]0x8ba4))
}

function Resolve-OutputArtifact([string]$Directory, [string]$StandardName, [bool]$Required) {
  $standardPath = Join-Path $Directory $StandardName
  if (Test-Path -LiteralPath $standardPath) {
    return (Resolve-Path -LiteralPath $standardPath).Path
  }

  $matches = @(Get-ChildItem -LiteralPath $Directory -File -Filter "*_$StandardName" | Sort-Object Name)
  if ($matches.Count -gt 0) {
    return $matches[0].FullName
  }

  if ($Required) {
    throw "$StandardName not found in: $Directory"
  }
  return ""
}

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$workspaceRoot = Resolve-Path -LiteralPath (Join-Path $scriptRoot "..")
$migrationRoot = Resolve-Path -LiteralPath (Join-Path $workspaceRoot "..\..")
if (-not $SummaryRoot) {
  $runtimeRoot = if ($env:REVIEW_AGENT_RUNTIME_PATH) {
    $env:REVIEW_AGENT_RUNTIME_PATH
  } else {
    Join-Path $migrationRoot "02_项目资料与运行数据\Agent运行数据"
  }
  $SummaryRoot = Join-Path $runtimeRoot ([string]([char]0x9879) + [string]([char]0x76ee) + [string]([char]0x6c47) + [string]([char]0x603b) + [string]([char]0x5305))
}

$projectOutput = Resolve-Path -LiteralPath $ProjectOutputDir
$summaryRootPath = if (Test-Path -LiteralPath $SummaryRoot) {
  Resolve-Path -LiteralPath $SummaryRoot
} else {
  New-Item -ItemType Directory -Force -Path $SummaryRoot
}

$recordsDir = Join-Path $summaryRootPath "records"
New-Item -ItemType Directory -Force -Path $recordsDir | Out-Null

$metadataPath = Resolve-OutputArtifact $projectOutput.Path "metadata.json" $true

$meta = Get-Content -LiteralPath $metadataPath -Encoding UTF8 -Raw | ConvertFrom-Json
if (-not $ProjectKey) {
  if ($meta.project_name -match '\d{3,}') {
    $ProjectKey = $Matches[0]
  } else {
    $ProjectKey = Split-Path -Leaf $projectOutput
  }
}

$safeKey = ConvertTo-SafeFileName $ProjectKey
$missingPath = Resolve-OutputArtifact $projectOutput.Path "missing_info_checklist.md" $false
$openItems = 0
if (Test-Path -LiteralPath $missingPath) {
  $pendingText = Get-PendingText
  $pattern = "\|\s*" + [regex]::Escape($pendingText) + "\s*\|"
  $openItems = (Select-String -LiteralPath $missingPath -Encoding UTF8 -Pattern $pattern -AllMatches).Count
}

$now = (Get-Date).ToString("s")
$packagePath = Resolve-OutputArtifact $projectOutput.Path "project_requirement_package.md" $false
$htmlPath = Resolve-OutputArtifact $projectOutput.Path "project_requirement_package.html" $false
$evidencePath = Resolve-OutputArtifact $projectOutput.Path "evidence_index.json" $false
$reviewResultPath = ""
if ($ReviewResultFile) {
  $reviewResultPath = (Resolve-Path -LiteralPath $ReviewResultFile).Path
} else {
  $reviewResultPath = Resolve-OutputArtifact $projectOutput.Path "review_analysis.md" $false
}

$indexPath = Join-Path $summaryRootPath "project_index.csv"
$row = [pscustomobject]@{
  ProjectKey = $ProjectKey
  ProjectName = $meta.project_name
  Customer = $meta.customer_name
  Region = $meta.region
  VehicleModels = (($meta.vehicle_models | ForEach-Object { [string]$_ }) -join '; ')
  VehicleCount = $meta.vehicle_count
  ReviewStatus = $ReviewStatus
  RiskLevel = $RiskLevel
  Owner = $Owner
  Decision = $Decision
  OpenItems = $openItems
  ProjectOutputDir = $projectOutput.Path
  PackageMarkdown = $packagePath
  PackageHtml = $htmlPath
  EvidenceIndex = $evidencePath
  ReviewResultFile = $reviewResultPath
  UpdatedAt = $now
}

$rows = @()
if (Test-Path -LiteralPath $indexPath) {
  $rows = @(Import-Csv -LiteralPath $indexPath -Encoding UTF8 | Where-Object { $_.ProjectKey -ne $ProjectKey })
}
$rows = @($rows) + $row
$rows | Sort-Object ProjectKey | Export-Csv -LiteralPath $indexPath -Encoding UTF8 -NoTypeInformation

$recordPath = Join-Path $recordsDir "$safeKey.md"
$record = @"
# $($meta.project_name)

| Field | Value |
|---|---|
| ProjectKey | $ProjectKey |
| Customer | $($meta.customer_name) |
| Region | $($meta.region) |
| VehicleModels | $($row.VehicleModels) |
| VehicleCount | $($meta.vehicle_count) |
| ReviewStatus | $ReviewStatus |
| RiskLevel | $RiskLevel |
| Owner | $Owner |
| OpenItems | $openItems |
| UpdatedAt | $now |

## Review Decision

$Decision

## Package Paths

- ProjectOutputDir: ``$($projectOutput.Path)``
- PackageMarkdown: ``$packagePath``
- PackageHtml: ``$htmlPath``
- MissingInfoChecklist: ``$missingPath``
- EvidenceIndex: ``$evidencePath``
- ReviewResultFile: ``$reviewResultPath``

## Maintenance

Run Register-ProjectReview.ps1 again after the review status or decision changes. The project row in project_index.csv will be replaced.
"@

$record | Set-Content -LiteralPath $recordPath -Encoding UTF8

Write-Host "Updated index: $indexPath"
Write-Host "Updated record: $recordPath"
