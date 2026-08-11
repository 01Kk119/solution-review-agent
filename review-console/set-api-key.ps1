$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$Form = New-Object System.Windows.Forms.Form
$Form.Text = "Connect DeepSeek Official API"
$Form.Size = New-Object System.Drawing.Size(540, 220)
$Form.StartPosition = "CenterScreen"
$Form.FormBorderStyle = "FixedDialog"
$Form.MaximizeBox = $false
$Form.MinimizeBox = $false

$Label = New-Object System.Windows.Forms.Label
$Label.Text = "Paste your DeepSeek API Key:"
$Label.Location = New-Object System.Drawing.Point(24, 24)
$Label.AutoSize = $true
$Form.Controls.Add($Label)

$Input = New-Object System.Windows.Forms.TextBox
$Input.Location = New-Object System.Drawing.Point(24, 52)
$Input.Size = New-Object System.Drawing.Size(475, 30)
$Input.UseSystemPasswordChar = $true
$Form.Controls.Add($Input)

$Hint = New-Object System.Windows.Forms.Label
$Hint.Text = "The key is stored in Windows user environment variables, not in the project database."
$Hint.Location = New-Object System.Drawing.Point(24, 88)
$Hint.Size = New-Object System.Drawing.Size(475, 38)
$Hint.ForeColor = [System.Drawing.Color]::DimGray
$Form.Controls.Add($Hint)

$Save = New-Object System.Windows.Forms.Button
$Save.Text = "Save and restart"
$Save.Location = New-Object System.Drawing.Point(355, 132)
$Save.Size = New-Object System.Drawing.Size(144, 34)
$Save.DialogResult = [System.Windows.Forms.DialogResult]::OK
$Form.AcceptButton = $Save
$Form.Controls.Add($Save)

$Cancel = New-Object System.Windows.Forms.Button
$Cancel.Text = "Cancel"
$Cancel.Location = New-Object System.Drawing.Point(255, 132)
$Cancel.Size = New-Object System.Drawing.Size(88, 34)
$Cancel.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
$Form.CancelButton = $Cancel
$Form.Controls.Add($Cancel)

$Result = $Form.ShowDialog()
if ($Result -ne [System.Windows.Forms.DialogResult]::OK) {
    exit 0
}

$PlainKey = $Input.Text.Trim()
if ($PlainKey.Length -lt 12 -or ($PlainKey.ToCharArray() | Where-Object { [int]$_ -lt 32 }).Count -gt 0) {
    [System.Windows.Forms.MessageBox]::Show(
        "The API Key is incomplete. Copy the full key and try again.",
        "Invalid API Key",
        "OK",
        "Error"
    ) | Out-Null
    exit 1
}

[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", $PlainKey, "User")
[Environment]::SetEnvironmentVariable("DEEPSEEK_BASE_URL", "https://api.deepseek.com", "User")
[Environment]::SetEnvironmentVariable("DEEPSEEK_MODEL", "deepseek-v4-flash", "User")
$env:DEEPSEEK_API_KEY = $PlainKey
$env:DEEPSEEK_BASE_URL = "https://api.deepseek.com"
$env:DEEPSEEK_MODEL = "deepseek-v4-flash"

# start.ps1 verifies that the listener belongs to this workspace before replacing it.
& (Join-Path $PSScriptRoot "start.ps1") -Restart
$PlainKey = $null
