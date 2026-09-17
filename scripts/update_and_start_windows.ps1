$ErrorActionPreference = 'Stop'

$root = if ((Split-Path -Leaf $PSScriptRoot) -eq 'scripts') {
  Split-Path -Parent $PSScriptRoot
} else {
  $PSScriptRoot
}
Set-Location -LiteralPath $root

$base = 'https://raw.githubusercontent.com/andersongraca/SkinCanceIA/feat/scientific-ml-backend'
$files = @(
  'INICIAR_PROJETO.cmd',
  'scripts/start_local_demo_windows.ps1',
  'server/routers.ts',
  'server/services/PythonInferenceService.ts',
  'client/src/components/diagnosis/types.ts',
  'client/src/components/diagnosis/ResultsTab.tsx',
  'client/src/pages/DiagnosisPage.tsx',
  'client/src/components/diagnosis/UploadTab.tsx',
  'ml/skin_cancer_ml/explain.py',
  'ml/skin_cancer_ml/ensemble_heatmap.py',
  'ml/skin_cancer_ml/lesion_segmentation.py'
)

Write-Host 'Atualizando arquivos críticos do projeto...' -ForegroundColor Cyan
foreach ($file in $files) {
  $destination = Join-Path $root ($file -replace '/', '\')
  $directory = Split-Path -Parent $destination
  New-Item -ItemType Directory -Path $directory -Force | Out-Null
  Invoke-WebRequest -Uri "$base/$file" -OutFile $destination -UseBasicParsing
  Write-Host "OK: $file"
}

$segmenter = Join-Path $root 'ml_artifacts\isic2016_segmentation\lesion_segmentation.pt'
if (-not (Test-Path -LiteralPath $segmenter)) {
  New-Item -ItemType Directory -Path (Split-Path -Parent $segmenter) -Force | Out-Null
  Invoke-WebRequest -Uri "$base/ml_artifacts/isic2016_segmentation/lesion_segmentation.pt" -OutFile $segmenter -UseBasicParsing
  Write-Host 'OK: checkpoint do localizador ISIC'
}

Write-Host 'Atualização concluída. Iniciando validação e servidor...' -ForegroundColor Green
& (Join-Path $root 'scripts\start_local_demo_windows.ps1')
