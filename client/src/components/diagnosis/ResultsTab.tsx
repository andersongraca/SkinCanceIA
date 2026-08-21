import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, CheckCircle, Info, ShieldAlert } from 'lucide-react';
import type { ClassificationResponse, ImageEligibility, ModelPrediction } from './types';

interface ResultsTabProps {
  imagePreview: string | null;
  selectedImage: File | null;
  isProcessing: boolean;
  classificationResult: ClassificationResponse | null;
}

function classificationText(classification: 'benign' | 'malignant'): string {
  return classification === 'malignant' ? 'Maligna' : 'Benigna';
}

function classificationVariant(classification: 'benign' | 'malignant'): 'default' | 'destructive' {
  return classification === 'malignant' ? 'destructive' : 'default';
}

function EligibilitySummary({ eligibility }: { eligibility: ImageEligibility }) {
  const quality = eligibility.quality_score;
  const ood = eligibility.ood_score;
  return (
    <Card className="border-slate-200">
      <CardHeader>
        <CardTitle className="text-lg">Triagem de qualidade e domínio</CardTitle>
        <CardDescription>A entrada é elegível somente quando permanece no domínio dermatoscópico de referência.</CardDescription>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
        <div className="rounded-lg bg-slate-50 p-4"><p className="text-slate-500">Status</p><p className="font-semibold text-slate-900">{eligibility.status === 'accepted' ? 'Aceita' : 'Rejeitada'}</p></div>
        <div className="rounded-lg bg-slate-50 p-4"><p className="text-slate-500">Qualidade</p><p className="font-semibold text-slate-900">{typeof quality === 'number' ? quality.toFixed(3) : '—'}</p></div>
        <div className="rounded-lg bg-slate-50 p-4"><p className="text-slate-500">Escore OOD</p><p className="font-semibold text-slate-900">{typeof ood === 'number' ? ood.toFixed(3) : '—'}</p></div>
        <div className="rounded-lg bg-slate-50 p-4"><p className="text-slate-500">Dimensão</p><p className="font-semibold text-slate-900">{eligibility.width && eligibility.height ? `${eligibility.width} × ${eligibility.height}` : '—'}</p></div>
      </CardContent>
    </Card>
  );
}

function ModelCard({ title, scope, result }: { title: string; scope: string; result: ModelPrediction }) {
  const uncertainty = result.uncertainty;
  return (
    <div className="border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between"><h4 className="font-semibold text-slate-900">{title}</h4><Badge variant="outline">{scope}</Badge></div>
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm"><span className="text-slate-600">Classificação:</span><Badge variant={classificationVariant(result.classification)}>{classificationText(result.classification)}</Badge></div>
        <div className="space-y-1"><div className="flex items-center justify-between text-sm"><span className="text-slate-600">Confiança:</span><span className="font-medium">{result.confidence.toFixed(1)}%</span></div><Progress value={result.confidence} className="h-2" /></div>
        <p className="text-xs text-slate-500">Tempo de inferência: {result.inferenceTime} ms</p>
        {uncertainty && <p className="text-xs text-slate-500">Entropia: {uncertainty.predictiveEntropy.toFixed(4)} · Variância TTA: {uncertainty.ttaVariance.toFixed(6)}</p>}
      </div>
    </div>
  );
}

export default function ResultsTab({ imagePreview, selectedImage, isProcessing, classificationResult }: ResultsTabProps) {
  if (isProcessing) {
    return <Alert><Info className="h-4 w-4" /><AlertDescription>A classificação está sendo executada no servidor. Aguarde a conclusão para visualizar os resultados.</AlertDescription></Alert>;
  }

  if (!imagePreview || !classificationResult) {
    return <Alert><AlertCircle className="h-4 w-4" /><AlertDescription>Nenhum resultado disponível. Faça upload de uma imagem e classifique-a primeiro.</AlertDescription></Alert>;
  }

  const eligibility = classificationResult.eligibility || classificationResult.result?.eligibility;
  if (classificationResult.status === 'rejected' || !classificationResult.result) {
    const rejection = classificationResult.eligibility;
    return (
      <div className="space-y-6">
        <Card className="border-2 border-red-200">
          <CardHeader><CardTitle>Imagem rejeitada antes da classificação</CardTitle><CardDescription>A entrada não foi encaminhada aos modelos porque falhou na triagem de qualidade ou de domínio.</CardDescription></CardHeader>
          <CardContent className="space-y-4">
            <Alert variant="destructive"><ShieldAlert className="h-4 w-4" /><AlertTitle>Fora dos critérios de elegibilidade</AlertTitle><AlertDescription>{rejection?.reasons?.join('; ') || 'Imagem não elegível para análise.'}</AlertDescription></Alert>
            {rejection?.warnings?.length ? <p className="text-sm text-amber-700">Avisos: {rejection.warnings.join('; ')}</p> : null}
          </CardContent>
        </Card>
        {rejection && <EligibilitySummary eligibility={rejection} />}
        <Card><CardContent className="pt-6"><img src={imagePreview} alt="Imagem rejeitada" className="max-h-96 w-full object-contain rounded-lg bg-slate-50" />{selectedImage && <p className="text-sm text-slate-600 mt-3"><span className="font-medium">Arquivo:</span> {selectedImage.name}</p>}</CardContent></Card>
      </div>
    );
  }

  const result = classificationResult.result;
  const uncertainty = result.ensembleResult.uncertainty;
  const heatmaps = result.heatmaps;
  const heatmapItems = heatmaps ? [
    ['CNN — Grad-CAM', heatmaps.cnnHeatmapPath],
    ['ViT — atribuição de tokens', heatmaps.vitHeatmapPath],
    ['Híbrido — mapa combinado', heatmaps.hybridHeatmapPath],
    ...(heatmaps.ensembleHeatmapPath ? [['Ensemble Learning — mapa agregado', heatmaps.ensembleHeatmapPath] as const] : []),
  ] as const : [];

  return (
    <div className="space-y-6">
      {eligibility && <EligibilitySummary eligibility={eligibility} />}

      <Card className="border-2">
        <CardHeader><CardTitle>Resultado da classificação</CardTitle><CardDescription>Saída do ensemble após triagem, inferência e combinação ponderada dos modelos.</CardDescription></CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4"><h3 className="font-semibold text-slate-900">Imagem analisada</h3><div className="border rounded-lg overflow-hidden bg-slate-50"><img src={imagePreview} alt="Imagem analisada" className="w-full h-auto max-h-96 object-contain" /></div>{selectedImage && <p className="text-sm text-slate-600"><span className="font-medium">Arquivo:</span> {selectedImage.name}</p>}</div>
            <div className="space-y-4"><h3 className="font-semibold text-slate-900">Decisão final</h3><div className="bg-gradient-to-br from-slate-50 to-slate-100 p-6 rounded-lg space-y-4"><div className="flex items-center justify-between"><span className="text-lg font-medium text-slate-900">Classificação:</span><Badge variant={classificationVariant(result.finalClassification)}>{classificationText(result.finalClassification)}</Badge></div><div className="space-y-2"><div className="flex items-center justify-between"><span className="text-sm font-medium text-slate-700">Confiança:</span><span className="text-2xl font-bold text-slate-900">{result.finalConfidence.toFixed(1)}%</span></div><Progress value={result.finalConfidence} className="h-3" /></div>{uncertainty?.abstain ? <Alert variant="destructive"><ShieldAlert className="h-4 w-4" /><AlertDescription><strong>Abstenção recomendada:</strong> a incerteza agregada ultrapassou o critério operacional.</AlertDescription></Alert> : <Alert className="border-green-200 bg-green-50"><CheckCircle className="h-4 w-4 text-green-600" /><AlertDescription className="text-green-800">A entrada foi aceita e a predição foi produzida. O resultado é auxiliar e não substitui avaliação dermatológica.</AlertDescription></Alert>}</div></div>
          </div>
        </CardContent>
      </Card>

      {uncertainty && <Card><CardHeader><CardTitle className="text-lg">Incerteza e abstensão</CardTitle><CardDescription>A decisão deve ser revista quando a incerteza indicar abstensão.</CardDescription></CardHeader><CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm"><div className="rounded-lg bg-slate-50 p-4"><p className="text-slate-500">Entropia preditiva</p><p className="font-semibold">{uncertainty.predictiveEntropy.toFixed(4)}</p></div><div className="rounded-lg bg-slate-50 p-4"><p className="text-slate-500">Variância TTA</p><p className="font-semibold">{uncertainty.ttaVariance.toFixed(6)}</p></div><div className="rounded-lg bg-slate-50 p-4"><p className="text-slate-500">Estado</p><p className="font-semibold">{uncertainty.abstain ? 'Abster-se' : 'Predição liberada'}</p></div></CardContent></Card>}

      <Card><CardHeader><CardTitle>Análise detalhada por modelo</CardTitle><CardDescription>As três saídas são preservadas antes da combinação do ensemble.</CardDescription></CardHeader><CardContent><div className="grid grid-cols-1 md:grid-cols-2 gap-4"><ModelCard title="CNN (ResNet-50)" scope="Local" result={result.cnnResult} /><ModelCard title="Vision Transformer" scope="Global" result={result.vitResult} /><ModelCard title="Híbrido CNN–ViT" scope="Híbrido" result={result.hybridResult} /><div className="bg-blue-50 border border-blue-100 rounded-lg"><ModelCard title="Ensemble Learning" scope="Final" result={result.ensembleResult} /></div></div></CardContent></Card>

      <Card><CardHeader><CardTitle>Mapas de explicabilidade</CardTitle><CardDescription>Visualizações produzidas pelos checkpoints reais para apoiar a inspeção das regiões relevantes.</CardDescription></CardHeader><CardContent><Alert className="border-blue-200 bg-blue-50"><Info className="h-4 w-4 text-blue-600" /><AlertDescription className="text-blue-800">Os mapas são explicações aproximadas da decisão e não constituem prova de causalidade clínica.</AlertDescription></Alert>{heatmapItems.length ? <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">{heatmapItems.map(([title, src]) => <div key={src} className="border rounded-lg p-4 space-y-2"><h4 className="font-semibold text-slate-900">{title}</h4><img src={src} alt={title} className="w-full h-64 object-contain rounded bg-slate-100" /></div>)}</div> : <Alert className="mt-4"><AlertDescription>Os heatmaps não foram gerados nesta execução; a classificação permanece registrada com os resultados dos modelos.</AlertDescription></Alert>}</CardContent></Card>
    </div>
  );
}
