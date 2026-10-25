# Adds a scheduled task that starts the wake button agent when you sign in.
# Edit $Agent and $HookUrl first.
$Agent   = "$env:USERPROFILE\wake-button\host\wake_button.py"
$HookUrl = 'https://in.wakehook.com/v1/h/REPLACE_ME'

# Stored as a user environment variable, not in the task's command line.
[Environment]::SetEnvironmentVariable('WAKEHOOK_URL', $HookUrl, 'User')

$action   = New-ScheduledTaskAction -Execute 'pythonw.exe' -Argument "`"$Agent`""
$trigger  = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit 0
Register-ScheduledTask -TaskName 'WakeHook wake button' -Action $action -Trigger $trigger -Settings $settings -Force
Start-ScheduledTask -TaskName 'WakeHook wake button'
