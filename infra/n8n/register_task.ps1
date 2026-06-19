<#
  register_task.ps1 — prende (o apaga) el auto-trigger diario de Windows.

  Registra una Tarea Programada que corre run_daily.ps1 cada manana. Con
  -StartWhenAvailable, si la compu estaba apagada a la hora fijada y la abres mas
  tarde, Windows la corre "lo antes posible" (ese es el catch-up que pediste).
  Corre en TU sesion (cuando estas logueado) para tener la GPU del render.

  ESTO es el unico paso que PRENDE el gasto automatico (voz ElevenLabs ~centavos
  por video) + el gate de Telegram diario. Despues de esto: desbloqueas la compu
  y ya esta. Para apagarlo: -Unregister.

  Uso:
    powershell -ExecutionPolicy Bypass -File register_task.ps1                 # prende, 7:00am
    powershell -ExecutionPolicy Bypass -File register_task.ps1 -Time 06:30
    powershell -ExecutionPolicy Bypass -File register_task.ps1 -Carril evergreen
    powershell -ExecutionPolicy Bypass -File register_task.ps1 -Unregister     # apaga
    Get-ScheduledTask -TaskName DineroLATAM-Producir | Get-ScheduledTaskInfo   # estado
#>
[CmdletBinding()]
param(
  [string]$Time = "07:00",
  [string]$TaskName = "DineroLATAM-Producir",
  [string]$Carril = "",
  [switch]$Unregister
)

$ErrorActionPreference = "Stop"
$here    = Split-Path -Parent $MyInvocation.MyCommand.Path
$wrapper = Join-Path $here "run_daily.ps1"

if ($Unregister) {
  if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Output "Tarea '$TaskName' eliminada. El auto-trigger quedo APAGADO."
  } else {
    Write-Output "No existe la tarea '$TaskName'. Nada que apagar."
  }
  return
}

if (-not (Test-Path $wrapper)) { throw "No encuentro run_daily.ps1 junto a este script ($wrapper)." }

# argumentos que la tarea le pasa al wrapper
$wrapArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$wrapper`""
if ($Carril) { $wrapArgs += " -Carril $Carril" }

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $wrapArgs -WorkingDirectory $here
$trigger = New-ScheduledTaskTrigger -Daily -At $Time

# -StartWhenAvailable = catch-up si se perdio el inicio (compu apagada).
# -MultipleInstances IgnoreNew = candado extra: si ya hay una corrida viva, no abre otra.
# -ExecutionTimeLimit 12h = no la mates mientras espera tu tap de Telegram.
$settings = New-ScheduledTaskSettingsSet `
  -StartWhenAvailable `
  -MultipleInstances IgnoreNew `
  -ExecutionTimeLimit (New-TimeSpan -Hours 12) `
  -DontStopIfGoingOnBatteries `
  -AllowStartIfOnBatteries

# corre como tu usuario, solo cuando estas logueado (necesita la sesion + GPU)
$principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
  -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
  -Settings $settings -Principal $principal -Force | Out-Null

$cstr = if ($Carril) { " carril=$Carril" } else { "" }
Write-Output "OK. Tarea '$TaskName' registrada: diaria $Time + catch-up (StartWhenAvailable)$cstr."
Write-Output "Auto-trigger PRENDIDO. Desbloquea la compu y producira solo; tu unica accion es el tap de Telegram."
Write-Output "Apagar: powershell -ExecutionPolicy Bypass -File register_task.ps1 -Unregister"
