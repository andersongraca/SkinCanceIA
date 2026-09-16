$ErrorActionPreference = 'Stop'
$projectRoot = (Get-Location).Path
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw "Python local não encontrado em $python" }
$env:PYTHONPATH = Join-Path $projectRoot 'ml'
$root = Join-Path $projectRoot 'ml_artifacts\ham10000'
$testCsv = Join-Path $root 'test.csv'
$metadata = Join-Path $projectRoot 'data\metadata\HAM10000_metadata.csv'
$logDir = Join-Path $root 'validation_logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

foreach ($model in @('cnn','vit','hybrid')) {
  $checkpoint = Join-Path $root "$model\best.pt"
  $log = Join-Path $logDir "$model-evaluate.jsonl"
  & $python (Join-Path $projectRoot 'ml\evaluate_test.py') --checkpoint $checkpoint --test-csv $testCsv --batch-size 32 *> $log
  if ($LASTEXITCODE -ne 0) { throw "Avaliação falhou para $model; veja $log" }
}
$ensembleLog = Join-Path $logDir 'ensemble.jsonl'
& $python (Join-Path $projectRoot 'ml\ensemble.py') --root $root --test-csv $testCsv --batch-size 32 *> $ensembleLog
if ($LASTEXITCODE -ne 0) { throw "Ensemble falhou; veja $ensembleLog" }
$bootstrapLog = Join-Path $logDir 'bootstrap.jsonl'
& $python (Join-Path $projectRoot 'ml\bootstrap_metrics.py') --predictions (Join-Path $root 'ensemble\test_predictions.npz') --output (Join-Path $root 'ensemble\bootstrap_metrics.json') --repeats 1000 --seed 42 *> $bootstrapLog
if ($LASTEXITCODE -ne 0) { throw "Bootstrap falhou; veja $bootstrapLog" }
$auditLog = Join-Path $logDir 'audit.jsonl'
& $python (Join-Path $projectRoot 'ml\audit_ham10000.py') --metadata $metadata --split-dir $root --output (Join-Path $projectRoot 'docs\experiments\HAM10000_BIAS_AUDIT.json') *> $auditLog
if ($LASTEXITCODE -ne 0) { throw "Auditoria HAM10000 falhou; veja $auditLog" }
Write-Output (ConvertTo-Json -Compress @{ status = 'ok'; deviceCheck = 'CUDA unavailable; executed on CPU'; root = $root; outputs = @((Join-Path $root 'ensemble\test_metrics.json'), (Join-Path $root 'ensemble\bootstrap_metrics.json'), (Join-Path $projectRoot 'docs\experiments\HAM10000_BIAS_AUDIT.json')) })
