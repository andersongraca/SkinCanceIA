$ErrorActionPreference = 'Stop'
$projectRoot = (Get-Location).Path
$image = Get-ChildItem -Path (Join-Path $projectRoot 'data\raw\images') -Filter 'ISIC_*.jpg' -File | Select-Object -First 1
if (-not $image) { throw 'Nenhuma imagem HAM10000 ISIC_*.jpg foi encontrada.' }
$bytes = [System.IO.File]::ReadAllBytes($image.FullName)
$dataUrl = 'data:image/jpeg;base64,' + [Convert]::ToBase64String($bytes)

function Invoke-TrpcMutation([string]$procedure, [hashtable]$payload) {
  $body = @{ '0' = @{ json = $payload } } | ConvertTo-Json -Depth 20 -Compress
  Invoke-RestMethod -Method Post -Uri ("http://localhost:3000/api/trpc/{0}?batch=1" -f $procedure) -ContentType 'application/json' -Body $body
}

$uploadResponse = Invoke-TrpcMutation 'diagnosis.uploadImage' @{ fileName = $image.Name; mimeType = 'image/jpeg'; dataUrl = $dataUrl }
$uploadJson = $uploadResponse[0].result.data.json
$classifyResponse = Invoke-TrpcMutation 'diagnosis.classifyStoredImage' @{ imageId = [int]$uploadJson.imageId }
$classifyJson = $classifyResponse[0].result.data.json
Write-Output (ConvertTo-Json -Depth 8 -Compress @{ image = $image.Name; imageId = $uploadJson.imageId; classificationStatus = $classifyJson.status; diagnosisId = $classifyJson.diagnosis.id; hasHeatmaps = [bool]$classifyJson.result.heatmaps; heatmapKeys = @($classifyJson.result.heatmaps.PSObject.Properties.Name) })
