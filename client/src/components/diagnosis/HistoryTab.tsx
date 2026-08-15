import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertCircle, Eye, Loader2, ShieldCheck } from 'lucide-react';
import { trpc } from '@/lib/trpc';

function classificationText(classification: string): string {
  return classification === 'malignant' ? 'Maligna' : 'Benigna';
}

function dateText(value: Date | string): string {
  return new Date(value).toLocaleString('pt-BR');
}

export default function HistoryTab() {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const historyQuery = trpc.diagnosis.getHistory.useQuery();
  const detailQuery = trpc.diagnosis.getById.useQuery(
    { id: selectedId || 0 },
    { enabled: selectedId !== null },
  );

  if (historyQuery.isLoading) {
    return <Card><CardContent className="py-12 flex items-center justify-center gap-3 text-slate-600"><Loader2 className="h-5 w-5 animate-spin" />Carregando histórico real...</CardContent></Card>;
  }

  if (historyQuery.isError) {
    return <Alert variant="destructive"><AlertCircle className="h-4 w-4" /><AlertTitle>Falha ao carregar histórico</AlertTitle><AlertDescription>{historyQuery.error.message}</AlertDescription></Alert>;
  }

  const history = historyQuery.data || [];
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader><CardTitle>Histórico de diagnósticos</CardTitle><CardDescription>Registros persistidos para o usuário autenticado, ordenados do mais recente ao mais antigo.</CardDescription></CardHeader>
        <CardContent>
          {!history.length ? (
            <Alert><AlertCircle className="h-4 w-4" /><AlertDescription>Nenhum diagnóstico persistido. Faça upload de uma imagem elegível para iniciar uma análise.</AlertDescription></Alert>
          ) : (
            <div className="space-y-4">
              {history.map((record) => (
                <div key={record.id} className="border rounded-lg p-4 hover:bg-slate-50 transition-colors">
                  <div className="flex items-center justify-between mb-3 gap-3">
                    <div className="min-w-0"><p className="font-medium text-slate-900 truncate">{record.imageFileName}</p><p className="text-sm text-slate-500">{dateText(record.diagnosedAt)}</p></div>
                    <div className="flex items-center gap-2 shrink-0"><Badge variant={record.classification === 'malignant' ? 'destructive' : 'default'}>{classificationText(record.classification)}</Badge><Badge variant="outline">{record.confidence}%</Badge></div>
                  </div>
                  <div className="flex items-center justify-between gap-3"><p className="text-sm text-slate-600">Versão do modelo: <span className="font-medium">{record.modelVersion || 'não informada'}</span></p><Button variant="ghost" size="sm" onClick={() => setSelectedId(record.id)}><Eye className="w-4 h-4 mr-1" />Detalhes</Button></div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {selectedId !== null && (
        <Card>
          <CardHeader><CardTitle>Detalhes do diagnóstico</CardTitle><CardDescription>Dados retornados pela consulta protegida do diagnóstico selecionado.</CardDescription></CardHeader>
          <CardContent className="space-y-4">
            {detailQuery.isLoading && <div className="flex items-center gap-2 text-slate-600"><Loader2 className="h-4 w-4 animate-spin" />Carregando detalhes...</div>}
            {detailQuery.isError && <Alert variant="destructive"><AlertCircle className="h-4 w-4" /><AlertDescription>{detailQuery.error.message}</AlertDescription></Alert>}
            {detailQuery.data && <><div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm"><div><p className="text-slate-600">Classificação final</p><p className="font-semibold">{classificationText(detailQuery.data.classification)}</p></div><div><p className="text-slate-600">Confiança</p><p className="font-semibold">{detailQuery.data.confidence}%</p></div><div><p className="text-slate-600">Data</p><p className="font-semibold">{dateText(detailQuery.data.diagnosedAt)}</p></div><div><p className="text-slate-600">CNN</p><p className="font-semibold">{detailQuery.data.cnnResult || '—'} ({detailQuery.data.cnnConfidence ?? '—'}%)</p></div><div><p className="text-slate-600">ViT</p><p className="font-semibold">{detailQuery.data.vitResult || '—'} ({detailQuery.data.vitConfidence ?? '—'}%)</p></div><div><p className="text-slate-600">Híbrido</p><p className="font-semibold">{detailQuery.data.hybridResult || '—'} ({detailQuery.data.hybridConfidence ?? '—'}%)</p></div></div><Alert className="border-blue-200 bg-blue-50"><ShieldCheck className="h-4 w-4 text-blue-600" /><AlertDescription className="text-blue-800">O registro é informativo e não substitui avaliação dermatológica especializada.</AlertDescription></Alert></>}
            <Button variant="outline" className="w-full" onClick={() => setSelectedId(null)}>Fechar</Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
