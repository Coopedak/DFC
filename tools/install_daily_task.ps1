param(
  [string]$TaskName = 'DFC-Daily-Montague-Report',
  [string]$RunTime = '05:10'
)

$root = Split-Path $PSScriptRoot -Parent
$script = "$root\tools\run_daily_report.ps1"
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`""
$trigger = New-ScheduledTaskTrigger -Daily -At $RunTime
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 20)
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description 'Updates DFC Montague wave/weather report daily' -Force
Write-Output "Installed task: $TaskName at $RunTime"
