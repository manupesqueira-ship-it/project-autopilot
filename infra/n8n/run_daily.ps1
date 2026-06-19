<#
  run_daily.ps1 — lo que dispara el Task Scheduler cada manana.

  Hace UNA cosa: si hoy aun no se produjo, corre producir.py (siguiente tema de
  la cola). Pone el "candado 1/dia" para no duplicar, y SOLO marca el dia como
  hecho si producir.py salio 0 (aprobado por Telegram + encolado en la nube).
  Si no hay tema, o lo rechazas, o expira el tap -> NO marca -> reintenta luego.

  El "catch-up" (si la compu estaba apagada a las 7am y la abres 10am) NO se
  maneja aqui: lo hace la propia tarea de Windows con -StartWhenAvailable
  (ver register_task.ps1). Aqui solo esta el candado y el log.

  Uso manual / prueba:
    powershell -ExecutionPolicy Bypass -File run_daily.ps1            # corrida real
    powershell -ExecutionPolicy Bypass -File run_daily.ps1 -DryRun    # $0, no gasta
    powershell -ExecutionPolicy Bypass -File run_daily.ps1 -Carril evergreen
#>
[CmdletBinding()]
param(
  [int]$TimeoutSec = 36000,     # ventana del tap de Telegram (10h: 7am -> 5pm, antes del publish ~8pm)
  [string]$Carril = "",         # opcional: forzar carril (news|evergreen)
  [switch]$DryRun               # pasa --dry-run a producir.py y usa un marker aparte ($0)
)

$ErrorActionPreference = "Stop"
$here   = Split-Path -Parent $MyInvocation.MyCommand.Path
$logdir = Join-Path $here "logs"
$today  = (Get-Date).ToString("yyyy-MM-dd")
$stamp  = (Get-Date).ToString("yyyy-MM-dd_HHmmss")

# marker separado en dry-run para no tocar el candado real
$marker = Join-Path $here (".last_produced" + $(if ($DryRun) { ".dryrun" } else { "" }))

New-Item -ItemType Directory -Force -Path $logdir | Out-Null
$wlog = Join-Path $logdir "run_daily.log"

function Log($m) {
  $line = "{0}  {1}" -f (Get-Date).ToString("yyyy-MM-dd HH:mm:ss"), $m
  Add-Content -Path $wlog -Value $line -Encoding utf8
  Write-Output $line
}

# --- candado 1/dia ---
if (Test-Path $marker) {
  $last = (Get-Content $marker -Raw).Trim()
  if ($last -eq $today) {
    Log "[run_daily] ya se produjo hoy ($today). Candado 1/dia: nada que hacer."
    exit 0
  }
}

# --- localizar python ---
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { Log "[run_daily] ERROR: 'python' no esta en PATH."; exit 1 }

# --- armar args de producir.py ---
$argv = @((Join-Path $here "producir.py"), "--timeout", "$TimeoutSec")
if ($Carril) { $argv += @("--carril", $Carril) }
if ($DryRun) { $argv += "--dry-run" }

$outLog = Join-Path $logdir ("producir_{0}.out.log" -f $stamp)
$errLog = Join-Path $logdir ("producir_{0}.err.log" -f $stamp)

Log ("[run_daily] arrancando: python producir.py {0}" -f ($argv[1..($argv.Length-1)] -join ' '))

# Start-Process evita el wrap de stderr de PS 5.1 (2>&1) y da el ExitCode limpio.
$p = Start-Process -FilePath $py -ArgumentList $argv -NoNewWindow -Wait -PassThru `
       -WorkingDirectory $here -RedirectStandardOutput $outLog -RedirectStandardError $errLog
$rc = $p.ExitCode

if ($rc -eq 0) {
  Set-Content -Path $marker -Value $today -Encoding ascii
  Log "[run_daily] OK rc=0: producido + encolado. Marcado $today. La nube publica ~8pm CDMX. Log: $(Split-Path $outLog -Leaf)"
} else {
  Log "[run_daily] producir.py rc=$rc (sin tema / no aprobado / fallo). NO se marca; reintenta la proxima. Log: $(Split-Path $errLog -Leaf)"
}
exit $rc
