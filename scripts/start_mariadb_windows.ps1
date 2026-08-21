$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$existing = Get-NetTCPConnection -LocalPort 3306 -State Listen -ErrorAction SilentlyContinue
if ($existing) { Write-Output 'MariaDB já está ativo em 127.0.0.1:3306.'; exit 0 }
$install = Get-ChildItem 'C:\Program Files\MariaDB*' -Directory | Sort-Object Name -Descending | Select-Object -First 1
if (-not $install) { throw 'MariaDB não foi encontrado em C:\Program Files.' }
$exe = Join-Path $install.FullName 'bin\mariadbd.exe'
$data = Join-Path $install.FullName 'data'
$logDir = Join-Path $root '.mariadb-log'
$log = Join-Path $logDir 'mariadb-console.log'
$errorLog = Join-Path $logDir 'mariadb-error.log'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$arguments = @(
  "--datadir=`"$data`"",
  '--port=3306',
  '--bind-address=127.0.0.1',
  '--character-set-server=utf8mb4',
  '--collation-server=utf8mb4_unicode_ci'
)
Start-Process -FilePath $exe -ArgumentList $arguments -WorkingDirectory $data -WindowStyle Hidden -RedirectStandardOutput $log -RedirectStandardError $errorLog | Out-Null
Start-Sleep -Seconds 8
if (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port 3306 -InformationLevel Quiet)) { throw 'MariaDB não abriu a porta 3306.' }
Write-Output 'MariaDB local ativo em 127.0.0.1:3306.'
