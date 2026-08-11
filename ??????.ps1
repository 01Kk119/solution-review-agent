$ErrorActionPreference = "Stop"
$CodeRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Targets = @(
    (Join-Path $CodeRoot "Agent工作区\skills\solution-review\SKILL.md"),
    (Join-Path $CodeRoot "Agent工作区\skills\solution-review\references\output-storage-map.md"),
    (Join-Path $CodeRoot "Agent工作区\skills\multi-agent-risk-review\SKILL.md")
)

$Replacements = [ordered]@{
    'Order DATA/Order DATA/projects_input' = '02_项目资料与运行数据/Agent运行数据/projects_input'
    'Order DATA/Order DATA/output' = '02_项目资料与运行数据/Agent运行数据/output'
    'Order DATA/Order DATA/项目汇总包' = '02_项目资料与运行数据/Agent运行数据/项目汇总包'
    'Order DATA/Order DATA/skills' = '01_Agent程序与知识库/Agent工作区/skills'
    'Order DATA/Order DATA/scripts' = '01_Agent程序与知识库/Agent工作区/scripts'
    '.\Order DATA\Order DATA\projects_input' = '.\02_项目资料与运行数据\Agent运行数据\projects_input'
    '.\Order DATA\Order DATA\output' = '.\02_项目资料与运行数据\Agent运行数据\output'
    '.\Order DATA\Order DATA\项目汇总包' = '.\02_项目资料与运行数据\Agent运行数据\项目汇总包'
    '.\Order DATA\Order DATA\skills' = '.\01_Agent程序与知识库\Agent工作区\skills'
    '.\Order DATA\Order DATA\scripts' = '.\01_Agent程序与知识库\Agent工作区\scripts'
}

foreach ($Target in $Targets) {
    if (-not (Test-Path -LiteralPath $Target)) { continue }
    $Text = [System.IO.File]::ReadAllText($Target, [System.Text.Encoding]::UTF8)
    foreach ($Entry in $Replacements.GetEnumerator()) {
        $Text = $Text.Replace($Entry.Key, $Entry.Value)
    }
    $Text = $Text.Replace(
        'Assume the workspace root is the parent of `Order DATA/Order DATA`.',
        'Assume the migration root contains the two sibling folders `01_Agent程序与知识库` and `02_项目资料与运行数据`.'
    )
    [System.IO.File]::WriteAllText($Target, $Text, [System.Text.UTF8Encoding]::new($false))
}

Write-Host "Operational documentation paths updated."
