param(
    [switch]$Restart
)

$ErrorActionPreference = "Stop"
$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$CodeRoot = Split-Path -Parent $AppRoot
$MigrationRoot = Split-Path -Parent $CodeRoot
$RuntimeRoot = Join-Path $MigrationRoot "02_项目资料与运行数据"

if ([string]::IsNullOrWhiteSpace($env:REVIEW_CONSOLE_DATA_PATH)) {
    $env:REVIEW_CONSOLE_DATA_PATH = Join-Path $RuntimeRoot "工作台数据"
}
if ([string]::IsNullOrWhiteSpace($env:REVIEW_PROJECTS_PATH)) {
    $env:REVIEW_PROJECTS_PATH = Join-Path $RuntimeRoot "项目记录"
}
if ([string]::IsNullOrWhiteSpace($env:OBSIDIAN_VAULT_PATH)) {
    $env:OBSIDIAN_VAULT_PATH = Join-Path $RuntimeRoot "Obsidian运行数据"
}
if ([string]::IsNullOrWhiteSpace($env:REVIEW_KNOWLEDGE_BASE_PATH)) {
    $env:REVIEW_KNOWLEDGE_BASE_PATH = Join-Path $CodeRoot "Agent知识库\agent\03_knowledge"
}

$DatabasePath = Join-Path $env:REVIEW_CONSOLE_DATA_PATH "review_console.db"
$PythonCommand = Get-Command pythonw.exe, python.exe -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($null -eq $PythonCommand) {
    throw "未找到 Python。请先安装 Python 3.10+，并勾选 Add Python to PATH。"
}
$Python = $PythonCommand.Source
$Url = "http://127.0.0.1:8765"
$UserApiKey = [Environment]::GetEnvironmentVariable("DEEPSEEK_API_KEY", "User")
if ([string]::IsNullOrWhiteSpace($UserApiKey)) {
    # One-time compatibility for keys saved by the previous configuration form.
    $UserApiKey = [Environment]::GetEnvironmentVariable("SILICONFLOW_API_KEY", "User")
}
$UserBaseUrl = [Environment]::GetEnvironmentVariable("DEEPSEEK_BASE_URL", "User")
$UserModel = [Environment]::GetEnvironmentVariable("DEEPSEEK_MODEL", "User")
if ([string]::IsNullOrWhiteSpace($UserBaseUrl)) {
    $UserBaseUrl = "https://api.deepseek.com"
}
if ([string]::IsNullOrWhiteSpace($UserModel)) {
    $UserModel = "deepseek-v4-flash"
}
if (-not [string]::IsNullOrWhiteSpace($UserApiKey)) {
    $env:DEEPSEEK_API_KEY = $UserApiKey
}
if (-not [string]::IsNullOrWhiteSpace($UserBaseUrl)) {
    $env:DEEPSEEK_BASE_URL = $UserBaseUrl
}
if (-not [string]::IsNullOrWhiteSpace($UserModel)) {
    $env:DEEPSEEK_MODEL = $UserModel
}

function Get-ReviewConsoleHealth {
    try {
        return Invoke-RestMethod -Uri "$Url/api/health" -TimeoutSec 1
    } catch {
        return $null
    }
}

function Stop-CurrentReviewConsole {
    param($Health)

    # Only stop the process when the service identifies itself as this workspace.
    if ($null -eq $Health -or
        [string]::IsNullOrWhiteSpace($Health.database) -or
        -not [string]::Equals(
            [System.IO.Path]::GetFullPath($Health.database),
            [System.IO.Path]::GetFullPath($DatabasePath),
            [System.StringComparison]::OrdinalIgnoreCase
        )) {
        return $false
    }

    $Listener = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($null -eq $Listener) {
        return $false
    }

    Stop-Process -Id $Listener.OwningProcess -Force -ErrorAction Stop
    for ($Attempt = 0; $Attempt -lt 20; $Attempt++) {
        Start-Sleep -Milliseconds 100
        if (-not (Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue)) {
            return $true
        }
    }
    return $true
}

$Health = Get-ReviewConsoleHealth
$KeyIsConfigured = -not [string]::IsNullOrWhiteSpace($UserApiKey)
$ServiceNeedsKeyRefresh = $Health -and $KeyIsConfigured -and -not $Health.api_key_configured

if ($Health -and ($Restart -or $ServiceNeedsKeyRefresh)) {
    if (Stop-CurrentReviewConsole -Health $Health) {
        $Health = $null
    }
}

try {
    if ($null -eq $Health) {
        throw "Review Console is not running."
    }
} catch {
    Start-Process -FilePath $Python `
        -ArgumentList "`"$(Join-Path $AppRoot 'app.py')`"" `
        -WorkingDirectory $AppRoot `
        -WindowStyle Hidden

    $Ready = $false
    for ($Attempt = 0; $Attempt -lt 30; $Attempt++) {
        Start-Sleep -Milliseconds 250
        try {
            Invoke-WebRequest -Uri "$Url/api/health" -UseBasicParsing -TimeoutSec 1 | Out-Null
            $Ready = $true
            break
        } catch {
            # Wait for the local server.
        }
    }
    if (-not $Ready) {
        Add-Type -AssemblyName PresentationFramework
        [System.Windows.MessageBox]::Show(
            "Review Console failed to start. See review-console\README.md.",
            "Startup failed"
        ) | Out-Null
        exit 1
    }
}

Start-Process $Url
