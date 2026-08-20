$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$startScript = Join-Path $PSScriptRoot 'start_mariadb_windows.ps1'
& powershell -NoProfile -ExecutionPolicy Bypass -File $startScript
$install = Get-ChildItem 'C:\Program Files\MariaDB*' -Directory | Sort-Object Name -Descending | Select-Object -First 1
if (-not $install) { throw 'MariaDB não foi encontrado em C:\Program Files.' }
$mysql = Join-Path $install.FullName 'bin\mysql.exe'
$dbName = 'skincancer'
$dbUser = 'skincancer_app'
$dbHost = '127.0.0.1'
$dbPort = 3306
$envPath = Join-Path $root '.env'
$existingUrl = if (Test-Path $envPath) { Get-Content $envPath | Where-Object { $_ -match '^DATABASE_URL=' } | Select-Object -First 1 } else { $null }
$lines = if (Test-Path $envPath) { @(Get-Content $envPath) } else { @() }
if (-not $existingUrl) {
  $bytes = New-Object byte[] 24
  [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
  $dbPass = ([System.BitConverter]::ToString($bytes) -replace '-', '').ToLowerInvariant()
  $sql = @"
CREATE DATABASE IF NOT EXISTS $dbName CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$dbUser'@'localhost' IDENTIFIED BY '$dbPass';
CREATE USER IF NOT EXISTS '$dbUser'@'$dbHost' IDENTIFIED BY '$dbPass';
ALTER USER '$dbUser'@'localhost' IDENTIFIED BY '$dbPass';
ALTER USER '$dbUser'@'$dbHost' IDENTIFIED BY '$dbPass';
GRANT ALL PRIVILEGES ON $dbName.* TO '$dbUser'@'localhost';
GRANT ALL PRIVILEGES ON $dbName.* TO '$dbUser'@'$dbHost';
FLUSH PRIVILEGES;
"@
  $sql | & $mysql --protocol=tcp -h 127.0.0.1 -P $dbPort -u root
  if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar o banco ou o usuário MariaDB.' }
  $lines = @($lines | Where-Object { $_ -notmatch '^DATABASE_URL=' })
  $lines += "DATABASE_URL=mysql://$dbUser`:$dbPass@$dbHost`:$dbPort/$dbName"
  [System.IO.File]::WriteAllLines($envPath, $lines)
  Write-Output 'Banco, usuário e DATABASE_URL criados sem exibir a senha.'
} else {
  Write-Output 'DATABASE_URL existente preservado.'
}
Set-Location $root
corepack pnpm db:push
Write-Output 'Banco local pronto e schema aplicado.'
