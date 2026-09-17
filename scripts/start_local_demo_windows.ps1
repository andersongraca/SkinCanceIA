$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root

function Resolve-Python {
  $candidates = @(
    (Join-Path $root '.venv\Scripts\python.exe'),
    'C:\Users\Gabriel\AppData\Local\Programs\Python\Python311\python.exe'
  )

  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
      return (Resolve-Path -LiteralPath $candidate).Path
    }
  }

  $command = Get-Command python -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }

  throw 'Python não encontrado. Instale Python 3.11 ou recrie o ambiente .venv.'
}

function Require-File([string]$path, [string]$label) {
  if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
    throw "$label não encontrado: $path"
  }
}

$python = Resolve-Python
Write-Host "Python selecionado: $python" -ForegroundColor Cyan

& $python -c "import torch, torchvision, PIL, cv2, numpy; print('Dependencias ML OK; torch=' + torch.__version__)"
if ($LASTEXITCODE -ne 0) {
  throw 'O Python selecionado não possui todas as dependências ML. Execute: python -m pip install -r requirements-ml.txt'
}

$cnn = Join-Path $root 'ml_artifacts\ham10000\cnn\best.pt'
$vit = Join-Path $root 'ml_artifacts\ham10000\vit\best.pt'
$hybrid = Join-Path $root 'ml_artifacts\ham10000\hybrid\best.pt'
$weights = Join-Path $root 'ml_artifacts\ham10000\ensemble\weights.json'
$reference = Join-Path $root 'ml_artifacts\ham10000\quality_reference.json'
$segmenter = Join-Path $root 'ml_artifacts\isic2016_segmentation\lesion_segmentation.pt'

Require-File $cnn 'Checkpoint CNN'
Require-File $vit 'Checkpoint ViT'
Require-File $hybrid 'Checkpoint Hybrid'
Require-File $weights 'Pesos do Ensemble'
Require-File $reference 'Referência de qualidade/OOD'
Require-File $segmenter 'Checkpoint do localizador ISIC'

$env:PORT = '3010'
$env:NODE_ENV = 'development'
$env:LOCAL_DEMO_MODE = 'true'
$env:VITE_LOCAL_DEMO_MODE = 'true'
$env:DATABASE_URL = ''
$env:ML_PROJECT_ROOT = $root
$env:ML_PYTHON_PATH = $python
$env:PYTHONPATH = $root
$env:ML_CNN_CHECKPOINT = $cnn
$env:ML_VIT_CHECKPOINT = $vit
$env:ML_HYBRID_CHECKPOINT = $hybrid
$env:ML_ENSEMBLE_WEIGHTS_PATH = $weights
$env:ML_DOMAIN_REFERENCE = $reference
$env:ML_LESION_SEGMENTER_CHECKPOINT = $segmenter
$env:ML_LESION_GATE_MODE = 'balanced'
$env:ML_MODEL_VERSION = 'ham10000-v4-ensemble'
$env:ML_ENTROPY_THRESHOLD = '0.75'
$env:ML_TTA_VARIANCE_THRESHOLD = '0.03'
$env:ML_ENSEMBLE_ABSTAIN_VOTES = '2'
$env:ML_ENSEMBLE_ENTROPY_THRESHOLD = '0.75'
$env:ML_ENSEMBLE_TTA_VARIANCE_THRESHOLD = '0.03'
$env:ML_INFERENCE_TIMEOUT_MS = '600000'

$existing = Get-NetTCPConnection -LocalPort 3010 -State Listen -ErrorAction SilentlyContinue
foreach ($connection in @($existing)) {
  $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($connection.OwningProcess)" -ErrorAction SilentlyContinue
  if ($process -and $process.Name -eq 'node.exe' -and $process.CommandLine -like "*$root*") {
    Write-Host "Encerrando servidor antigo do projeto (PID $($process.ProcessId))..." -ForegroundColor Yellow
    Stop-Process -Id $process.ProcessId -Force
  } else {
    throw "A porta 3010 está ocupada pelo PID $($connection.OwningProcess), que não pertence a este projeto."
  }
}

$runtime = Join-Path $root 'runtime'
New-Item -ItemType Directory -Path $runtime -Force | Out-Null
$log = Join-Path $runtime 'backend.log'
"===== Inicialização $(Get-Date -Format o) =====" | Set-Content -LiteralPath $log -Encoding UTF8

Write-Host 'Configuração validada. Servidor: http://localhost:3010' -ForegroundColor Green
Write-Host "Log: $log" -ForegroundColor Green
Write-Host 'Mantenha este terminal aberto. Use Ctrl+C para parar.' -ForegroundColor Yellow

& pnpm.cmd exec tsx watch server/_core/index.ts 2>&1 | Tee-Object -FilePath $log -Append
