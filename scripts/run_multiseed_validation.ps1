param(
  [int[]]$Seeds = @(42, 123, 456),
  [int]$Epochs = 20,
  [int]$BatchSize = 16,
  [int]$ImageSize = 224,
  [switch]$RunTraining,
  [switch]$NoPretrained
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Get-Location).Path
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw "Python local não encontrado em $python" }
$env:PYTHONPATH = Join-Path $projectRoot 'ml'
$dataDir = Join-Path $projectRoot 'data\raw\images'
$metadata = Join-Path $projectRoot 'data\metadata\HAM10000_metadata.csv'
$multiseedRoot = Join-Path $projectRoot 'ml_artifacts\multiseed'
New-Item -ItemType Directory -Force -Path $multiseedRoot | Out-Null

foreach ($seed in $Seeds) {
  $seedRoot = Join-Path $multiseedRoot "seed-$seed"
  $splitRoot = Join-Path $seedRoot 'split_manifest'
  New-Item -ItemType Directory -Force -Path $seedRoot | Out-Null
  & $python (Join-Path $projectRoot 'ml\prepare_ham10000.py') --data-dir $dataDir --metadata-csv $metadata --output-dir $splitRoot --seed $seed
  if ($LASTEXITCODE -ne 0) { throw "Preparação falhou para seed=$seed" }

  if ($RunTraining) {
    $trainArgs = @('-m', 'skin_cancer_ml.train', '--data-dir', $dataDir, '--metadata-csv', $metadata, '--output-dir', $seedRoot, '--model', 'all', '--epochs', $Epochs, '--batch-size', $BatchSize, '--image-size', $ImageSize, '--seed', $seed, '--freeze-backbone', '--unfreeze-backbone-after', '5', '--balanced-sampler')
    if ($NoPretrained) { $trainArgs += '--no-pretrained' }
    & $python @trainArgs
    if ($LASTEXITCODE -ne 0) { throw "Treinamento falhou para seed=$seed" }

    foreach ($model in @('cnn','vit','hybrid')) {
      & $python (Join-Path $projectRoot 'ml\evaluate_test.py') --checkpoint (Join-Path $seedRoot "$model\best.pt") --test-csv (Join-Path $seedRoot "$model\test.csv") --batch-size 32
      if ($LASTEXITCODE -ne 0) { throw "Avaliação falhou para seed=$seed modelo=$model" }
    }
    & $python (Join-Path $projectRoot 'ml\ensemble.py') --root $seedRoot --test-csv (Join-Path $seedRoot 'cnn\test.csv') --batch-size 32
    if ($LASTEXITCODE -ne 0) { throw "Ensemble falhou para seed=$seed" }
    & $python (Join-Path $projectRoot 'ml\bootstrap_metrics.py') --predictions (Join-Path $seedRoot 'ensemble\test_predictions.npz') --output (Join-Path $seedRoot 'ensemble\bootstrap_metrics.json') --repeats 1000 --seed 42
    if ($LASTEXITCODE -ne 0) { throw "Bootstrap falhou para seed=$seed" }
  }
}

$aggregateOutput = Join-Path $multiseedRoot 'aggregate.json'
& $python (Join-Path $projectRoot 'ml\aggregate_multiseed.py') --root $multiseedRoot --output $aggregateOutput
if ($LASTEXITCODE -ne 0) { throw 'Agregação multi-semente falhou.' }
Write-Output (ConvertTo-Json -Compress @{ status = 'ok'; trainingExecuted = [bool]$RunTraining; seeds = $Seeds; aggregate = $aggregateOutput })
