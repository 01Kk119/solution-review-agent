param(
  [Parameter(Mandatory = $true)]
  [string]$ProjectOutputDir,

  [Parameter(Mandatory = $true)]
  [string]$OriginalProjectDir,

  [string]$ResultFolderName = "$([char]0x8BC4)$([char]0x4F30)$([char]0x7ED3)$([char]0x679C)",

  [string]$ProjectLabel = "",

  [switch]$Clean
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

$projectOutput = Resolve-Path -LiteralPath $ProjectOutputDir
$originalProject = Resolve-Path -LiteralPath $OriginalProjectDir
$resultDir = Join-Path $originalProject.Path $ResultFolderName

if ([string]::IsNullOrWhiteSpace($ProjectLabel)) {
  $ProjectLabel = Split-Path -Leaf $originalProject.Path
}

$invalidFileNameChars = [System.IO.Path]::GetInvalidFileNameChars()
foreach ($char in $invalidFileNameChars) {
  $ProjectLabel = $ProjectLabel.Replace([string]$char, "_")
}
$ProjectLabel = $ProjectLabel.Trim()
if ([string]::IsNullOrWhiteSpace($ProjectLabel)) {
  $ProjectLabel = "project"
}

$prefixedFiles = @(
  "project_requirement_package.md",
  "project_requirement_package.html",
  "metadata.json",
  "evidence_index.json",
  "missing_info_checklist.md",
  "review_analysis.md",
  "review_analysis.html",
  "version_recommendation.md",
  "version_recommendation.html",
  "custom_development_checklist.md",
  "custom_development_checklist.html",
  "nonstandard_development_items.md",
  "nonstandard_development_items.html",
  "effort_recommendation.md",
  "effort_recommendation.html"
)

$friendlyHtmlNames = @{
  "review_analysis.html" = "$ProjectLabel-$([char]0x65B9)$([char]0x6848)$([char]0x8BC4)$([char]0x5BA1)$([char]0x62A5)$([char]0x544A).html"
  "version_recommendation.html" = "$ProjectLabel-$([char]0x7248)$([char]0x672C)$([char]0x9002)$([char]0x914D)$([char]0x5EFA)$([char]0x8BAE).html"
  "custom_development_checklist.html" = "$ProjectLabel-$([char]0x5B9A)$([char]0x5236)$([char]0x5316)$([char]0x5F00)$([char]0x53D1)$([char]0x6E05)$([char]0x5355).html"
  "nonstandard_development_items.html" = "$ProjectLabel-$([char]0x975E)$([char]0x6807)$([char]0x5224)$([char]0x5B9A)$([char]0x6E05)$([char]0x5355).html"
  "effort_recommendation.html" = "$ProjectLabel-$([char]0x4EBA)$([char]0x65F6)$([char]0x4F30)$([char]0x7B97)$([char]0x6E05)$([char]0x5355).html"
}

if ($Clean -and (Test-Path -LiteralPath $resultDir)) {
  $resolvedResult = Resolve-Path -LiteralPath $resultDir
  $originalPrefix = $originalProject.Path.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
  if (-not $resolvedResult.Path.StartsWith($originalPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to clean result directory outside original project folder: $($resolvedResult.Path)"
  }
  if ((Split-Path -Leaf $resolvedResult.Path) -ne $ResultFolderName) {
    throw "Refusing to clean unexpected directory name: $($resolvedResult.Path)"
  }
  Remove-Item -LiteralPath $resolvedResult.Path -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $resultDir | Out-Null

$excluded = @(
  "project_requirement_package.draft.md",
  "missing_info_checklist.draft.md"
)

Get-ChildItem -LiteralPath $projectOutput.Path -Force | Where-Object {
  $excluded -notcontains $_.Name
} | ForEach-Object {
  $destination = $resultDir
  if (-not $_.PSIsContainer -and $friendlyHtmlNames.ContainsKey($_.Name)) {
    $destination = Join-Path $resultDir $friendlyHtmlNames[$_.Name]
  } elseif (-not $_.PSIsContainer -and ($prefixedFiles -contains $_.Name)) {
    $destination = Join-Path $resultDir ($ProjectLabel + "_" + $_.Name)
  }
  Copy-Item -LiteralPath $_.FullName -Destination $destination -Recurse -Force
}

Write-Host "Review result exported: $resultDir"
