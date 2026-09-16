$ErrorActionPreference = "Stop"
$root = "C:\Program Files\MariaDB 12.3"
$data = Join-Path (Get-Location) "runtime\mariadb-data"
New-Item -ItemType Directory -Force $data | Out-Null
$secret = -join (1..8 | ForEach-Object { (New-Guid).Guid.Replace('-', '') })
$installer = Join-Path $root "bin\mariadb-install-db.exe"
& $installer "--datadir=$data" "--password=$secret" "--port=3307" "--default-user"
if ($LASTEXITCODE -ne 0) { throw "MariaDB initialization failed with exit code $LASTEXITCODE" }
$envLines = @(Get-Content .env | Where-Object { $_ -notmatch '^\s*#?\s*DATABASE_URL=' })
$envLines += "DATABASE_URL=mysql://root:$secret@127.0.0.1:3307/skincancer"
Set-Content -Path .env -Value $envLines -Encoding UTF8
Write-Output "Local MariaDB data directory initialized."
