import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertCircle, Loader2 } from 'lucide-react';
import { trpc } from '@/lib/trpc';

interface ModelMetric {
  modelName: string;
  modelVersion: string;
  accuracy: number;
  sensitivity: number;
  specificity: number;
  f1Score: number;
  auc: number;
  precision: number;
  sampleCount: number;
}

function displayName(modelName: string): string {
  return modelName
    .replace('Hibrido', 'Híbrido')
    .replace('Metricas', 'Métricas');
}

export default function MetricsTab() {
  const metricsQuery = trpc.metrics.getAllMetrics.useQuery(undefined, {
    staleTime: 5 * 60 * 1000,
  });
  const metrics = (metricsQuery.data || []) as ModelMetric[];

  const chartData = metrics.map((metric) => ({
    name: displayName(metric.modelName).replace(' (ResNet-50)', ''),
    accuracy: metric.accuracy,
    sensitivity: metric.sensitivity,
    specificity: metric.specificity,
    f1Score: metric.f1Score,
    auc: metric.auc,
    precision: metric.precision,
  }));

  if (metricsQuery.isLoading) {
    return (
      <Card>
        <CardContent className="py-12 flex items-center justify-center gap-3 text-slate-600">
          <Loader2 className="h-5 w-5 animate-spin" />
          Carregando métricas do experimento...
        </CardContent>
      </Card>
    );
  }

  if (metricsQuery.isError) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Falha ao carregar as métricas</AlertTitle>
        <AlertDescription>{metricsQuery.error.message}</AlertDescription>
      </Alert>
    );
  }

  if (!metrics.length) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          As métricas reais ainda não foram registradas no banco de dados. Execute o script de carga do experimento.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Métricas de desempenho dos modelos</CardTitle>
          <CardDescription>
            Valores derivados do conjunto de teste congelado do HAM10000; percentuais são arredondados no armazenamento.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-semibold text-slate-900">Modelo</th>
                  <th className="text-center py-3 px-4 font-semibold text-slate-900">Acurácia</th>
                  <th className="text-center py-3 px-4 font-semibold text-slate-900">Sensibilidade</th>
                  <th className="text-center py-3 px-4 font-semibold text-slate-900">Especificidade</th>
                  <th className="text-center py-3 px-4 font-semibold text-slate-900">F1-score</th>
                  <th className="text-center py-3 px-4 font-semibold text-slate-900">AUROC</th>
                  <th className="text-center py-3 px-4 font-semibold text-slate-900">Precisão</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map((metric) => (
                  <tr key={`${metric.modelName}-${metric.modelVersion}`} className="border-b hover:bg-slate-50">
                    <td className="py-3 px-4 font-medium text-slate-900">{displayName(metric.modelName)}</td>
                    <td className="py-3 px-4 text-center"><Badge variant="default">{metric.accuracy}%</Badge></td>
                    <td className="py-3 px-4 text-center"><Badge variant="outline">{metric.sensitivity}%</Badge></td>
                    <td className="py-3 px-4 text-center"><Badge variant="outline">{metric.specificity}%</Badge></td>
                    <td className="py-3 px-4 text-center"><Badge variant="outline">{metric.f1Score}%</Badge></td>
                    <td className="py-3 px-4 text-center"><Badge className="bg-blue-600">{metric.auc}%</Badge></td>
                    <td className="py-3 px-4 text-center"><Badge variant="outline">{metric.precision}%</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Comparação gráfica</CardTitle>
          <CardDescription>Comparação das principais métricas entre os componentes e o ensemble.</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" interval={0} angle={-12} textAnchor="end" height={60} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="accuracy" fill="#3b82f6" name="Acurácia" />
              <Bar dataKey="sensitivity" fill="#10b981" name="Sensibilidade" />
              <Bar dataKey="specificity" fill="#f59e0b" name="Especificidade" />
              <Bar dataKey="f1Score" fill="#8b5cf6" name="F1-score" />
              <Bar dataKey="auc" fill="#0f766e" name="AUROC" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {metrics.map((metric) => (
          <Card key={`${metric.modelName}-detail`}>
            <CardHeader>
              <CardTitle className="text-lg">{displayName(metric.modelName)}</CardTitle>
              <CardDescription>
                Amostras: {metric.sampleCount.toLocaleString('pt-BR')} · Versão: {metric.modelVersion}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {([
                ['Acurácia', metric.accuracy],
                ['Sensibilidade', metric.sensitivity],
                ['Especificidade', metric.specificity],
                ['F1-score', metric.f1Score],
                ['AUROC', metric.auc],
                ['Precisão', metric.precision],
              ] as const).map(([label, value]) => (
                <div key={label} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-700">{label}</span>
                    <span className="text-sm font-bold text-slate-900">{value}%</span>
                  </div>
                  <Progress value={value} className="h-2" />
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-base text-blue-900">Interpretação</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-blue-800">
          <p><strong>Sensibilidade</strong> representa a capacidade de identificar lesões positivas na definição binária adotada.</p>
          <p><strong>Especificidade</strong> representa a capacidade de reconhecer lesões negativas.</p>
          <p><strong>F1-score</strong> resume precisão e sensibilidade e é especialmente útil quando as classes são desbalanceadas.</p>
          <p><strong>AUROC</strong> mede a discriminação ao longo de diferentes limiares; não substitui validação clínica.</p>
        </CardContent>
      </Card>
    </div>
  );
}
